from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetConnectorCredentialsDto")


@_attrs_define
class GetConnectorCredentialsDto:
    """
    Attributes:
        access_key_id (str): AWS Credentials
        secret_access_key (str): AWS Secret Access Key
        session_token (str): AWS Session Token
        expiration_date (str): Expiration Date
    """

    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration_date: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_key_id = self.access_key_id

        secret_access_key = self.secret_access_key

        session_token = self.session_token

        expiration_date = self.expiration_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accessKeyId": access_key_id,
                "secretAccessKey": secret_access_key,
                "sessionToken": session_token,
                "expirationDate": expiration_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        access_key_id = d.pop("accessKeyId")

        secret_access_key = d.pop("secretAccessKey")

        session_token = d.pop("sessionToken")

        expiration_date = d.pop("expirationDate")

        get_connector_credentials_dto = cls(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            expiration_date=expiration_date,
        )

        get_connector_credentials_dto.additional_properties = d
        return get_connector_credentials_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
