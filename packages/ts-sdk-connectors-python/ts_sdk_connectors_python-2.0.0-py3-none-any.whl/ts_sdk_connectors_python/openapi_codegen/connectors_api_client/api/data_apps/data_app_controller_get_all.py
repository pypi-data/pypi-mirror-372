from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_apps_response import DataAppsResponse
from ...types import Response


def _get_kwargs(
    *,
    x_org_slug: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-slug"] = x_org_slug

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/data-apps",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[DataAppsResponse]:
    if response.status_code == 200:
        response_200 = DataAppsResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(
            response.status_code, response.content, headers=response.headers
        )
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[DataAppsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Response[DataAppsResponse]:
    """
    Args:
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataAppsResponse]
    """

    kwargs = _get_kwargs(
        x_org_slug=x_org_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Optional[DataAppsResponse]:
    """
    Args:
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataAppsResponse
    """

    return sync_detailed(
        client=client,
        x_org_slug=x_org_slug,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Response[DataAppsResponse]:
    """
    Args:
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataAppsResponse]
    """

    kwargs = _get_kwargs(
        x_org_slug=x_org_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Optional[DataAppsResponse]:
    """
    Args:
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataAppsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            x_org_slug=x_org_slug,
        )
    ).parsed
