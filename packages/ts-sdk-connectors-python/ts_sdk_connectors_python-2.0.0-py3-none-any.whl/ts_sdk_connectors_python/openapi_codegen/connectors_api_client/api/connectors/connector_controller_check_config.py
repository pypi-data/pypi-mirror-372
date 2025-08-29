from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.check_connector_config_response import CheckConnectorConfigResponse
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    x_org_slug: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-slug"] = x_org_slug

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/data-acquisition/connectors/{id}/config-check",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CheckConnectorConfigResponse]:
    if response.status_code == 201:
        response_201 = CheckConnectorConfigResponse.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(
            response.status_code, response.content, headers=response.headers
        )
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CheckConnectorConfigResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Response[CheckConnectorConfigResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CheckConnectorConfigResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        x_org_slug=x_org_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Optional[CheckConnectorConfigResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CheckConnectorConfigResponse
    """

    return sync_detailed(
        id=id,
        client=client,
        x_org_slug=x_org_slug,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Response[CheckConnectorConfigResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CheckConnectorConfigResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        x_org_slug=x_org_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Optional[CheckConnectorConfigResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CheckConnectorConfigResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            x_org_slug=x_org_slug,
        )
    ).parsed
