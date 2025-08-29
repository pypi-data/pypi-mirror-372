from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.hub_details_dto import HubDetailsDto
from ...types import UNSET, Response


def _get_kwargs(
    id: str,
    *,
    include: str,
    x_org_slug: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-slug"] = x_org_slug

    params: dict[str, Any] = {}

    params["include"] = include

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/hubs/{id}",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[HubDetailsDto]:
    if response.status_code == 200:
        response_200 = HubDetailsDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(
            response.status_code, response.content, headers=response.headers
        )
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[HubDetailsDto]:
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
    include: str,
    x_org_slug: str,
) -> Response[HubDetailsDto]:
    """
    Args:
        id (str):
        include (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HubDetailsDto]
    """

    kwargs = _get_kwargs(
        id=id,
        include=include,
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
    include: str,
    x_org_slug: str,
) -> Optional[HubDetailsDto]:
    """
    Args:
        id (str):
        include (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HubDetailsDto
    """

    return sync_detailed(
        id=id,
        client=client,
        include=include,
        x_org_slug=x_org_slug,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    include: str,
    x_org_slug: str,
) -> Response[HubDetailsDto]:
    """
    Args:
        id (str):
        include (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HubDetailsDto]
    """

    kwargs = _get_kwargs(
        id=id,
        include=include,
        x_org_slug=x_org_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    include: str,
    x_org_slug: str,
) -> Optional[HubDetailsDto]:
    """
    Args:
        id (str):
        include (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HubDetailsDto
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            include=include,
            x_org_slug=x_org_slug,
        )
    ).parsed
