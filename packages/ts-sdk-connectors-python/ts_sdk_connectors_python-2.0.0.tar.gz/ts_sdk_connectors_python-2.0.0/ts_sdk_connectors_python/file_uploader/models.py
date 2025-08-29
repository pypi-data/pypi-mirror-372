import io
import re
import textwrap
from enum import StrEnum
from typing import Annotated, Any, Literal, Optional, Self, TypeAlias

from pydantic import UUID4, BaseModel, Field, StringConstraints, model_validator

from ts_sdk_connectors_python.checksums import ParameterChecksumDict
from ts_sdk_connectors_python.ts_lib_shared_schema import S3MetadataFields
from ts_sdk_connectors_python.utils import calculate_size_in_bytes

TrimmedStr = Annotated[str, StringConstraints(strip_whitespace=True)]
Trace: TypeAlias = dict[str, str]
Metadata: TypeAlias = dict[TrimmedStr, TrimmedStr]
Tags: TypeAlias = list[TrimmedStr]


class UploadFileResponse(BaseModel):
    """
    Response upon successfully uploading a file.
    """

    bucket: str
    key: str
    versionId: Optional[str]
    fileId: str


class Label(BaseModel):
    """Upload file label"""

    name: TrimmedStr
    value: TrimmedStr


class Directive(StrEnum):
    """Directive for how to handle uploaded file metadata, tags, and labels (MTL) along with existing
    connector metadata, tags, and labels.

    'Append' means to merge connector MTL data with the upload file data. 'Replace' means only the
    uploaded file MTL data will be used."""

    APPEND = "Append"
    REPLACE = "Replace"


class UploadFileRequest(BaseModel):
    """
    Upload file request.

    Attributes:
        content (io.BytesIO | str | bytes): The file content, which can be a
            byte stream, string, or raw bytes.
        filepath (str): The target file path where the content should be stored.
            Must not be empty.
        source_type (Optional[str]): The source type of the file (e.g., system,
            user-uploaded, etc.).
        file_id (Optional[str]): An optional unique identifier for the file.
        trace_id (Optional[str]): An optional trace identifier for tracking
            operations.
        trace (Optional[Trace]): Additional trace details, if applicable.
        metadata (Optional[Metadata]): Additional metadata associated with the file.
        metadata_directive (Optional[Directive]): A directive specifying how
            metadata should be handled.
            If 'Append' is specified, connector metadata will be merged with
            upload file metadata.
            If 'Replace' is specified, only upload file metadata will be used.
        tags (Optional[Tags]): A collection of tags associated with the file.
        tags_directive (Optional[Directive]): A directive specifying how tags
            should be applied.
            If 'Append' is specified, connector tags will be merged with
            upload file tags.
            If 'Replace' is specified, only upload file tags will be used.
        labels (Optional[list[Label]]): A list of labels associated with the file.
        labels_directive (Optional[Directive]): A directive specifying how labels
            should be managed.
            If 'Append' is specified, connector labels will be merged with
            upload file labels.
            If 'Replace' is specified, only upload file labels will be used.
        checksums (Optional[ParameterChecksumDict]): A dictionary containing
            checksums for integrity verification.
        content_encoding (Optional[str]): Specifies the encoding type of the content
            (e.g., gzip, base64).
        content_type (Optional[str]): The MIME type of the file content.
        object_size (Optional[int | float]): The size of the object in bytes.
        destination_id (Optional[UUID4]): The unique identifier of the destination
            where the file will be uploaded. If not provided, the connector id will be used instead.
    """

    class Config:
        arbitrary_types_allowed = True

    content: io.BytesIO | str | bytes
    filepath: str = Field(min_length=1)
    source_type: Optional[str] = None
    file_id: Optional[str] = None
    trace_id: Optional[str] = None
    trace: Optional[Trace] = None
    metadata: Optional[Metadata] = None
    metadata_directive: Optional[Directive] = None
    tags: Optional[Tags] = None
    tags_directive: Optional[Directive] = None
    labels: Optional[list[Label]] = None
    labels_directive: Optional[Directive] = None
    checksums: Optional[ParameterChecksumDict] = None
    content_encoding: Optional[str] = None
    content_type: Optional[str] = None
    object_size: Optional[int | float] = None
    # abort_controller: Optional[AbortController] = None
    destination_id: Optional[UUID4] = None


UploadFileLabelNameAndValueRegex = re.compile(r"^(?![\uFFFE\uFFFF\n\r]).+$", re.UNICODE)
UploadFileTagSchemaValueRegex = re.compile(r"^[0-9a-zA-Z-_+. /]+$")
UploadFileMetadataKeyRegex = re.compile(r"^[0-9a-zA-Z-_+ ]+$")
UploadFileMetadataValueRegex = re.compile(r"^[0-9a-zA-Z-_+., /]+$")
HttpHeaderNameRegex = re.compile("^[a-zA-Z0-9!#$%&'*+-.^_`|~]+$")


class StrictLabel(Label):
    """
    A strictly validated file label.

    Attributes:
        name (str): The label name.
            - Whitespace is stripped.
            - Must match the pattern defined in ``UploadFileLabelNameAndValueRegex``.
            - Maximum length is 128 characters.
        value (str): The label value.
            - Whitespace is stripped.
            - Must match the pattern defined in ``UploadFileLabelNameAndValueRegex``.
    """

    name: Annotated[
        str,
        StringConstraints(  # type: ignore
            strip_whitespace=True,
            pattern=UploadFileLabelNameAndValueRegex,
            max_length=128,
        ),
    ]
    value: Annotated[
        str,
        StringConstraints(  # type: ignore
            strip_whitespace=True, pattern=UploadFileLabelNameAndValueRegex
        ),
    ]


class StrictUploadFileRequest(UploadFileRequest):
    """
    A strictly validated UploadFileRequest that enforces constraints on labels, metadata, and tags.

    Attributes:
        labels (Optional[List[StrictLabel]]):
            A list of strictly validated file labels.
        metadata (Optional[Dict[str, str]]):
            A dictionary of metadata key-value pairs. Both keys and values are validated:
                - Keys:
                  - Whitespace is stripped.
                  - Must match the pattern defined in ``UploadFileMetadataKeyRegex``.
                - Values:
                  - Whitespace is stripped.
                  - Must match the pattern defined in ``UploadFileMetadataValueRegex``.
        tags (Optional[List[str]]):
            A list of tags where each tag is validated:
                - Whitespace is stripped.
                - Maximum length is 128 characters.
                - Must match the pattern defined in ``UploadFileTagSchemaValueRegex``.

    Validators:
        validate_metadata_and_tag_size:
            Ensures that the combined size (in bytes) of the metadata and tags does not exceed 1.5 KB.
            - Uses the ``calculate_size_in_bytes`` function to compute sizes.
            - Raises a ValueError if the total size exceeds 1.5 KB, providing details of the individual sizes.
    """

    labels: Optional[list[StrictLabel]] = Field()
    metadata: Optional[
        dict[
            Annotated[
                str,
                StringConstraints(  # type: ignore
                    strip_whitespace=True, pattern=UploadFileMetadataKeyRegex
                ),
            ],
            Annotated[
                str,
                StringConstraints(  # type: ignore
                    strip_whitespace=True, pattern=UploadFileMetadataValueRegex
                ),
            ],
        ]
    ] = None
    tags: Optional[
        list[
            Annotated[
                str,
                StringConstraints(  # type: ignore
                    strip_whitespace=True,
                    max_length=128,
                    pattern=UploadFileTagSchemaValueRegex,
                ),
            ]
        ]
    ] = None

    @model_validator(mode="after")
    def validate_metadata_and_tag_size(self) -> Self:
        metadata_size = calculate_size_in_bytes(self.metadata)
        tags_size = calculate_size_in_bytes(self.tags)
        max_kb_size = 1.5
        total_size = metadata_size + tags_size
        if total_size > 1024 * max_kb_size:  # 1.5kb in bytes
            msg = f"Metadata and tags length cannot be larger than {max_kb_size}KB."
            additional_msg_lines = [
                f"Metadata size: {metadata_size}",
                f"Tags size: {tags_size}",
                f"Total size: {total_size}",
            ]
            additional_msg_txt = textwrap.indent("\n".join(additional_msg_lines), "\t")
            raise ValueError(f"{msg}\n{additional_msg_txt}")
        return self


# allowed upload args for boto3
ALLOWED_UPLOAD_ARGS = Literal[
    "ACL",
    "CacheControl",
    "ChecksumAlgorithm",
    "ContentDisposition",
    "ContentEncoding",
    "ContentLanguage",
    "ContentType",
    "ExpectedBucketOwner",
    "Expires",
    "GrantFullControl",
    "GrantRead",
    "GrantReadACP",
    "GrantWriteACP",
    "Metadata",
    "ObjectLockLegalHoldStatus",
    "ObjectLockMode",
    "ObjectLockRetainUntilDate",
    "RequestPayer",
    "ServerSideEncryption",
    "StorageClass",
    "SSECustomerAlgorithm",
    "SSECustomerKey",
    "SSECustomerKeyMD5",
    "SSEKMSKeyId",
    "SSEKMSEncryptionContext",
    "Tagging",
    "WebsiteRedirectLocation",
    "ChecksumType",
    "MpuObjectSize",
    "ChecksumCRC32",
    "ChecksumCRC32C",
    "ChecksumCRC64NVME",
    "ChecksumSHA1",
    "ChecksumSHA256",
]

# extra args for uploading files to s3 using boto
ExtraArgs: TypeAlias = dict[ALLOWED_UPLOAD_ARGS, Any]

# type alias for things that are roughly cohersible to JSON
CohersibleToJSON: TypeAlias = str | int | list | dict

# S3 metadata type
S3Metadata: TypeAlias = dict[S3MetadataFields, CohersibleToJSON]
