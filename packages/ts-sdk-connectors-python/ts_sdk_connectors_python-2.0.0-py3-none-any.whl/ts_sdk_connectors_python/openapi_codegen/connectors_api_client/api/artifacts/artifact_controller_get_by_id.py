from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.artifact_details_dto import ArtifactDetailsDto
from ...types import Response


def _get_kwargs(
    type_: str,
    *,
    x_org_slug: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-slug"] = x_org_slug

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/artifacts/{type_}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ArtifactDetailsDto]:
    if response.status_code == 200:
        response_200 = ArtifactDetailsDto.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(
            response.status_code, response.content, headers=response.headers
        )
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ArtifactDetailsDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    type_: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Response[ArtifactDetailsDto]:
    """
    Args:
        type_ (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactDetailsDto]
    """

    kwargs = _get_kwargs(
        type_=type_,
        x_org_slug=x_org_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    type_: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Optional[ArtifactDetailsDto]:
    """
    Args:
        type_ (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactDetailsDto
    """

    return sync_detailed(
        type_=type_,
        client=client,
        x_org_slug=x_org_slug,
    ).parsed


async def asyncio_detailed(
    type_: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Response[ArtifactDetailsDto]:
    """
    Args:
        type_ (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactDetailsDto]
    """

    kwargs = _get_kwargs(
        type_=type_,
        x_org_slug=x_org_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    type_: str,
    *,
    client: AuthenticatedClient,
    x_org_slug: str,
) -> Optional[ArtifactDetailsDto]:
    """
    Args:
        type_ (str):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactDetailsDto
    """

    return (
        await asyncio_detailed(
            type_=type_,
            client=client,
            x_org_slug=x_org_slug,
        )
    ).parsed
