import asyncio
import io
import json
import textwrap
from typing import Literal, Optional
from urllib.parse import urlencode
from uuid import UUID, uuid4

import aioboto3
import pydantic
from s3transfer import TransferConfig
from types_aiobotocore_s3 import S3Client, S3ServiceResource
from types_aiobotocore_s3.type_defs import GetObjectOutputTypeDef

from ts_sdk_connectors_python.aws_factory import AWSFactory
from ts_sdk_connectors_python.checksums import (
    ParameterChecksumDict,
    map_parameter_to_metadata_checksum,
)
from ts_sdk_connectors_python.config import TdpApiConfig
from ts_sdk_connectors_python.file_uploader.models import (
    Directive,
    ExtraArgs,
    Metadata,
    S3Metadata,
    StrictUploadFileRequest,
    Tags,
    Trace,
    UploadFileRequest,
    UploadFileResponse,
)
from ts_sdk_connectors_python.logger import get_logger
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import (
    ConnectorDetailsDto,
    ConnectorDetailsDtoHostType,
)
from ts_sdk_connectors_python.ts_lib_shared_schema import (
    API_UPLOAD_V1_INTEGRATION_ID,
    FileCategories,
    IntegrationTypes,
    S3MetadataFields,
    SourceTypes,
)
from ts_sdk_connectors_python.utils import text_shorten, unique_list

logger = get_logger(__name__)


# annotating this on pydantic models will auto-strip strings of left and right whitespace


def validate_upload_file_request(request: UploadFileRequest):
    """
    Validates the upload file request against :class:`StrictUploadFileRequest`

    :param request: The upload file request
    :raises ValueError: On MTL validation error
    :return: None
    """
    try:
        data = request.model_dump()
        data["content"] = request.content
        StrictUploadFileRequest(**data)
    except pydantic.ValidationError as validation_error:
        validation_error: pydantic.ValidationError
        msgs = []
        for err in validation_error.errors():
            name = ".".join([str(x) for x in err["loc"]])
            shortened_input_txt = text_shorten(repr(err["input"]), 50, "...")
            err_msg = err["msg"]

            shortened_input_txt = textwrap.indent(f"input: {shortened_input_txt}", "\t")
            err_msg = textwrap.indent(err_msg, "\t")
            if not name:
                name = UploadFileRequest.__name__
                msgs.append(f"{name}\n{err_msg}")
            else:
                msgs.append(f"{name}\n\t{err['msg']}\n\t{shortened_input_txt}".rstrip())
        msg_txt = textwrap.indent("\n".join(msgs), prefix="\t")
        raise ValueError(
            f"Upload file request failed validation:\n{msg_txt}"
        ) from validation_error


async def wait_for_s3_obj(
    session: aioboto3.Session, bucket: str, key: str, timeout: int
) -> GetObjectOutputTypeDef:

    async with asyncio.timeout(timeout):
        async with session.resource("s3") as s3:
            s3: S3ServiceResource
            s3_obj = await s3.Object(bucket, key)
            await s3_obj.wait_until_exists()
            result = await s3_obj.get()
            return result


# see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.S3Transfer.ALLOWED_UPLOAD_ARGS


def _coerce_metadata_to_str(metadata: S3Metadata) -> dict[str, str]:
    """Convert keys and values of a metadata dictionary to str for s3 uploads."""
    ascii_metadata: dict[str, str] = {}
    for key, value in metadata.items():
        if not isinstance(key, str):
            raise ValueError(f"Keys must be str. Found {value} ({type(value)}).")

        key = str(key)  # convert any strenums to just a str
        if isinstance(value, str):
            ascii_metadata[key] = value
        elif isinstance(value, (int, float, list, dict)):
            ascii_metadata[key] = json.dumps(value)
        elif isinstance(value, UUID):
            ascii_metadata[key] = str(value)
        elif value is not None:
            raise ValueError(f"Cannot coerce value {value} to str. {key}={value}")
    return ascii_metadata


class FileUploader:
    def __init__(self, *, connector_details: ConnectorDetailsDto, config: TdpApiConfig):
        """
        Async file uploader class that uploads files to the TDP Datalake.

        :param connector_details: Connector details
        :param config: Config

        """
        self.config = config
        self.connector_details = connector_details

    @staticmethod
    def _transform_trace_metadata(trace: Trace):
        """
        Transforms the metadata fields to include the "ts_" prefix
        :param trace:
        :return:
        """
        ts_prefix: Literal["ts_"] = "ts_"

        def add_prefix(key: str):
            if not key.startswith(ts_prefix):
                return ts_prefix + key
            return key

        return {add_prefix(key): val for key, val in trace.items()}

    async def upload_file(
        self,
        request: UploadFileRequest,
        strict_mtl_validation: bool = False,
        transfer_config: Optional[TransferConfig] = None,
    ):
        """
        Upload a file to the TDP datalake.

        :param request: The upload file request.
        :param strict_mtl_validation: Whether to throw an error if the request MTL is invalid. If false, will just log
            a warning.
        :param transfer_config: S3 Transfer config
        :return:
        """
        try:
            validate_upload_file_request(request)
        except Exception as exc:
            msg = f"Invalid MTL on upload file request\n{str(exc)}"
            if strict_mtl_validation:
                logger.error(msg)
                raise exc
            else:
                logger.warning(msg)

        org_slug = self.config.org_slug
        connector_id = (
            self.connector_details.id
            if self.connector_details
            else self.config.connector_id
        )
        datalake_bucket = self.config.datalake_bucket

        id_for_key = request.destination_id or connector_id
        file_id = request.file_id or str(uuid4())
        trace_id = request.trace_id or file_id
        s3_key = self.build_s3_key(
            org_slug, id_for_key, FileCategories.RAW, request.filepath
        )

        logger.debug(
            "Uploading file",
            extra={"fileId": file_id, "traceId": trace_id, "key": s3_key},
        )

        parameter_checksums: ParameterChecksumDict = request.checksums or {}
        aws_checksums: ExtraArgs = {
            "ChecksumAlgorithm": parameter_checksums.get("s3AdditionalChecksum", None)
            or "SHA256",
        }
        s3_metadata = self._get_s3_metadata(
            request, connector_id, file_id, trace_id, parameter_checksums
        )
        extra_args = self.get_extra_args(request, s3_metadata, aws_checksums)

        request_content = request.content
        if isinstance(request_content, bytes):
            request_content = io.BytesIO(request_content)
        elif isinstance(request_content, str):
            request_content = io.BytesIO(request_content.encode("utf-8"))

        # upload labels and file to S3
        aws = await AWSFactory().get_aws_instance(
            connector_id=connector_id,
            org_slug=org_slug,
            aws_region=self.config.aws_region,
        )
        async with await aws.create_client("s3") as s3_client:
            s3_client: S3Client
            if request.labels:
                await self.put_labels(
                    s3_client,
                    request=request,
                    file_id=file_id,
                    id_for_key=id_for_key,
                    aws_checksums=aws_checksums,
                )

            await s3_client.upload_fileobj(
                Fileobj=request_content,
                Bucket=datalake_bucket,
                Key=s3_key,
                ExtraArgs=extra_args,
                Config=transfer_config,
            )

        #####  boto3.upload_fileobj does not return info about the upload, connector does not have getObject permissions
        ## presently the version_id is inaccessible until AWS Case ID 174248890200377 is addressed or a patch is made
        #     file_obj = await wait_for_s3_obj(
        #         session=self.aws.session, bucket=datalake_bucket, key=s3_key, timeout=600
        #     )

        # version_id = file_obj.get("VersionId", None)
        version_id = None

        logger.debug(
            "Uploaded file",
            extra={
                "fileId": file_id,
                "traceId": trace_id,
                "key": s3_key,
                # "versionId": version_id,
            },
        )

        return UploadFileResponse(
            fileId=file_id, bucket=datalake_bucket, key=s3_key, versionId=version_id
        )

    def _get_s3_metadata(
        self,
        request: UploadFileRequest,
        connector_id: str,
        file_id: str,
        trace_id: str,
        parameter_checksums: ParameterChecksumDict,
    ):
        custom_metadata: Metadata = {}
        if request.metadata_directive == Directive.REPLACE:
            custom_metadata.update(request.metadata or {})
        else:
            if self.connector_details:
                custom_metadata.update(self.connector_details.metadata.to_dict() or {})
            custom_metadata.update(request.metadata or {})
        custom_tags: Tags = []
        if request.tags_directive == Directive.REPLACE:
            custom_tags.extend(request.tags or [])
        else:
            if self.connector_details:
                custom_tags.extend(self.connector_details.tags or [])
            custom_tags.extend(request.tags or [])
        metadata_checksums = map_parameter_to_metadata_checksum(parameter_checksums)
        artifact = self.connector_details.artifact if self.connector_details else None
        connector_slug = artifact.slug if artifact else None
        connector_namespace = artifact.namespace if artifact else None
        connector_version = artifact.version if artifact else None
        source_type = SourceTypes.UNKNOWN
        if request.source_type:
            source_type = request.source_type
        elif hasattr(artifact, "source_type"):
            source_type = artifact.source_type
        host_type = self.connector_details.host_type if self.connector_details else None
        is_hub_connector = host_type == ConnectorDetailsDtoHostType.HUB
        integration_type = (
            IntegrationTypes.HUB if is_hub_connector else IntegrationTypes.API
        )
        integration_id = API_UPLOAD_V1_INTEGRATION_ID
        if self.connector_details and self.connector_details.hub:
            integration_id = self.connector_details.hub.id
        trace = request.trace or {}
        trace_metadata = self._transform_trace_metadata(trace)

        do_not_inherit_labels = request.labels_directive == Directive.REPLACE
        source_name = self.connector_details.name if self.connector_details else None
        s3_metadata: S3Metadata = {
            **metadata_checksums,
            **trace_metadata,
            S3MetadataFields.FILE_ID: file_id,
            S3MetadataFields.TRACE_ID: trace_id,
            S3MetadataFields.INTEGRATION_TYPE: integration_type,
            S3MetadataFields.INTEGRATION_ID: integration_id,
            S3MetadataFields.CONNECTOR_NAMESPACE: connector_namespace,
            S3MetadataFields.CONNECTOR_SLUG: connector_slug,
            S3MetadataFields.CONNECTOR_VERSION: connector_version,
            S3MetadataFields.CUSTOM_METADATA: urlencode(custom_metadata, doseq=True),
            S3MetadataFields.CUSTOM_TAGS: ",".join(unique_list(custom_tags)),
            S3MetadataFields.SOURCE_ID: connector_id,
            S3MetadataFields.SOURCE_NAME: source_name,
            S3MetadataFields.SOURCE_TYPE: source_type,
            S3MetadataFields.DO_NOT_INHERIT_LABELS: do_not_inherit_labels,
            S3MetadataFields.DESTINATION_ID: request.destination_id,
        }

        return s3_metadata

    def get_encryption_opts(self) -> ExtraArgs:
        return {
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": self.config.kms_key_id,
        }

    def get_extra_args(
        self, request, s3_metadata: S3Metadata, aws_checksums: ExtraArgs
    ) -> ExtraArgs:
        metadata: dict[str, str] = _coerce_metadata_to_str(s3_metadata)

        extra_args: ExtraArgs = self.get_encryption_opts() | aws_checksums
        if request.content_type:
            extra_args["ContentType"] = request.content_type
        if request.content_encoding:
            extra_args["ContentEncoding"] = request.content_encoding
        extra_args["Metadata"] = metadata

        return extra_args

    async def put_labels(
        self,
        s3_client: S3Client,
        *,
        request: UploadFileRequest,
        file_id: str,
        id_for_key: str,
        aws_checksums: dict,
    ) -> None:
        """
        Upload the labels object to s3 if labels are available on the provided :class:`UploadFileRequest`

        :param s3_client: The s3 client
        :param request: The upload file request
        :param file_id: The file id
        :param id_for_key: The key id
        :param aws_checksums: AWS checksums
        :return:
        """
        label_key = self.build_s3_key(
            self.config.org_slug,
            id_for_key,
            FileCategories.TMP,
            f"{request.filepath}/{file_id}.labels",
        )
        label_file = None
        if request.labels:
            label_file = json.dumps([label.model_dump() for label in request.labels])

        await s3_client.put_object(
            Bucket=self.config.datalake_bucket,
            Key=label_key,
            Body=label_file,
            **self.get_encryption_opts(),
            **aws_checksums,
        )

    @staticmethod
    def build_s3_key(
        org_slug: str, id_for_key: str, category: str, filepath: str
    ) -> str:
        prefix = f"{org_slug}/{id_for_key}/{category}"
        if filepath.startswith("/"):
            return prefix + filepath
        return f"{prefix}/{filepath}"
