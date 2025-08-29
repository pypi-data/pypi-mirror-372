from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_data_app_request import CreateDataAppRequest
from ...models.data_app_details_dto import DataAppDetailsDto
from ...types import Response


def _get_kwargs(
    *,
    body: CreateDataAppRequest,
    x_org_slug: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-slug"] = x_org_slug

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/data-apps",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[DataAppDetailsDto]:
    if response.status_code == 201:
        response_201 = DataAppDetailsDto.from_dict(response.json())

        return response_201
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(
            response.status_code, response.content, headers=response.headers
        )
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[DataAppDetailsDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateDataAppRequest,
    x_org_slug: str,
) -> Response[DataAppDetailsDto]:
    """
    Args:
        x_org_slug (str):
        body (CreateDataAppRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataAppDetailsDto]
    """

    kwargs = _get_kwargs(
        body=body,
        x_org_slug=x_org_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: CreateDataAppRequest,
    x_org_slug: str,
) -> Optional[DataAppDetailsDto]:
    """
    Args:
        x_org_slug (str):
        body (CreateDataAppRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataAppDetailsDto
    """

    return sync_detailed(
        client=client,
        body=body,
        x_org_slug=x_org_slug,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: CreateDataAppRequest,
    x_org_slug: str,
) -> Response[DataAppDetailsDto]:
    """
    Args:
        x_org_slug (str):
        body (CreateDataAppRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataAppDetailsDto]
    """

    kwargs = _get_kwargs(
        body=body,
        x_org_slug=x_org_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: CreateDataAppRequest,
    x_org_slug: str,
) -> Optional[DataAppDetailsDto]:
    """
    Args:
        x_org_slug (str):
        body (CreateDataAppRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataAppDetailsDto
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_org_slug=x_org_slug,
        )
    ).parsed
