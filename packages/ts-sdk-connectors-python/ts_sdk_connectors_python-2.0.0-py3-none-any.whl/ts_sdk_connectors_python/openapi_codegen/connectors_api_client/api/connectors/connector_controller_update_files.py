from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.save_connector_files_request import SaveConnectorFilesRequest
from ...models.save_connector_files_response import SaveConnectorFilesResponse
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: SaveConnectorFilesRequest,
    x_org_slug: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-slug"] = x_org_slug

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/v1/data-acquisition/connectors/{id}/files",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SaveConnectorFilesResponse]:
    if response.status_code == 200:
        response_200 = SaveConnectorFilesResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(
            response.status_code, response.content, headers=response.headers
        )
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SaveConnectorFilesResponse]:
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
    body: SaveConnectorFilesRequest,
    x_org_slug: str,
) -> Response[SaveConnectorFilesResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):
        body (SaveConnectorFilesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SaveConnectorFilesResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
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
    body: SaveConnectorFilesRequest,
    x_org_slug: str,
) -> Optional[SaveConnectorFilesResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):
        body (SaveConnectorFilesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SaveConnectorFilesResponse
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
        x_org_slug=x_org_slug,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    body: SaveConnectorFilesRequest,
    x_org_slug: str,
) -> Response[SaveConnectorFilesResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):
        body (SaveConnectorFilesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SaveConnectorFilesResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        x_org_slug=x_org_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    body: SaveConnectorFilesRequest,
    x_org_slug: str,
) -> Optional[SaveConnectorFilesResponse]:
    """
    Args:
        id (str):
        x_org_slug (str):
        body (SaveConnectorFilesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SaveConnectorFilesResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
            x_org_slug=x_org_slug,
        )
    ).parsed
