from typing import Literal, TypeAlias

from types_aiobotocore_s3.literals import ChecksumAlgorithmType

AllChecksumAlgorithmTypes = ChecksumAlgorithmType | Literal["MD5"]


parameter_check_sum_keys = Literal[
    "rawMd5Checksum",
    "rawSha1Checksum",
    "rawSha256Checksum",
    "rawCrc32Checksum",
    "rawCrc32cChecksum",
    "s3AdditionalChecksum",
]
metadata_checksum_keys = Literal[
    "ts_raw_md5_checksum",
    "ts_raw_sha1_checksum",
    "ts_raw_sha256_checksum",
    "ts_raw_crc32_checksum",
    "ts_raw_crc32c_checksum",
]

ParameterChecksumDict: TypeAlias = dict[parameter_check_sum_keys, str]
MetadataChecksumDict: TypeAlias = dict[metadata_checksum_keys, str]

checksum_mapping: dict[parameter_check_sum_keys, metadata_checksum_keys] = {
    "rawMd5Checksum": "ts_raw_md5_checksum",
    "rawSha1Checksum": "ts_raw_sha1_checksum",
    "rawSha256Checksum": "ts_raw_sha256_checksum",
    "rawCrc32Checksum": "ts_raw_crc32_checksum",
    "rawCrc32cChecksum": "ts_raw_crc32c_checksum",
}


def map_parameter_to_metadata_checksum(
    parameter_checksums: ParameterChecksumDict,
) -> MetadataChecksumDict:
    metadata_checksums: MetadataChecksumDict = {}
    for parameter_key, parameter_checksum_val in parameter_checksums.items():
        if parameter_key in checksum_mapping:  # exclude s3AdditionalChecksum
            metadata_key = checksum_mapping[parameter_key]
            metadata_checksums[metadata_key] = parameter_checksum_val
    return metadata_checksums
