import datetime
from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.connector_controller_get_files_order_direction import (
    ConnectorControllerGetFilesOrderDirection,
)
from ...models.connector_controller_get_files_statuses_item import (
    ConnectorControllerGetFilesStatusesItem,
)
from ...models.connector_files_response import ConnectorFilesResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    file_ids: Union[Unset, list[str]] = UNSET,
    exclude_file_ids: Union[Unset, list[str]] = UNSET,
    unique_external_ids: Union[Unset, list[str]] = UNSET,
    exclude_unique_external_ids: Union[Unset, list[str]] = UNSET,
    statuses: Union[Unset, list[ConnectorControllerGetFilesStatusesItem]] = UNSET,
    max_errors: Union[Unset, float] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    updated_before: Union[Unset, datetime.datetime] = UNSET,
    updated_after: Union[Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, str] = UNSET,
    order_direction: Union[Unset, ConnectorControllerGetFilesOrderDirection] = UNSET,
    take: Union[Unset, float] = UNSET,
    skip: Union[Unset, float] = UNSET,
    x_org_slug: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-org-slug"] = x_org_slug

    params: dict[str, Any] = {}

    json_file_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(file_ids, Unset):
        json_file_ids = file_ids

    params["fileIds"] = json_file_ids

    json_exclude_file_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(exclude_file_ids, Unset):
        json_exclude_file_ids = exclude_file_ids

    params["excludeFileIds"] = json_exclude_file_ids

    json_unique_external_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(unique_external_ids, Unset):
        json_unique_external_ids = unique_external_ids

    params["uniqueExternalIds"] = json_unique_external_ids

    json_exclude_unique_external_ids: Union[Unset, list[str]] = UNSET
    if not isinstance(exclude_unique_external_ids, Unset):
        json_exclude_unique_external_ids = exclude_unique_external_ids

    params["excludeUniqueExternalIds"] = json_exclude_unique_external_ids

    json_statuses: Union[Unset, list[str]] = UNSET
    if not isinstance(statuses, Unset):
        json_statuses = []
        for statuses_item_data in statuses:
            statuses_item = statuses_item_data.value
            json_statuses.append(statuses_item)

    params["statuses"] = json_statuses

    params["maxErrors"] = max_errors

    json_created_before: Union[Unset, str] = UNSET
    if not isinstance(created_before, Unset):
        json_created_before = created_before.isoformat()
    params["createdBefore"] = json_created_before

    json_created_after: Union[Unset, str] = UNSET
    if not isinstance(created_after, Unset):
        json_created_after = created_after.isoformat()
    params["createdAfter"] = json_created_after

    json_updated_before: Union[Unset, str] = UNSET
    if not isinstance(updated_before, Unset):
        json_updated_before = updated_before.isoformat()
    params["updatedBefore"] = json_updated_before

    json_updated_after: Union[Unset, str] = UNSET
    if not isinstance(updated_after, Unset):
        json_updated_after = updated_after.isoformat()
    params["updatedAfter"] = json_updated_after

    params["orderBy"] = order_by

    json_order_direction: Union[Unset, str] = UNSET
    if not isinstance(order_direction, Unset):
        json_order_direction = order_direction.value

    params["orderDirection"] = json_order_direction

    params["take"] = take

    params["skip"] = skip

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/v1/data-acquisition/connectors/{id}/files",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ConnectorFilesResponse]:
    if response.status_code == 200:
        response_200 = ConnectorFilesResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(
            response.status_code, response.content, headers=response.headers
        )
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ConnectorFilesResponse]:
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
    file_ids: Union[Unset, list[str]] = UNSET,
    exclude_file_ids: Union[Unset, list[str]] = UNSET,
    unique_external_ids: Union[Unset, list[str]] = UNSET,
    exclude_unique_external_ids: Union[Unset, list[str]] = UNSET,
    statuses: Union[Unset, list[ConnectorControllerGetFilesStatusesItem]] = UNSET,
    max_errors: Union[Unset, float] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    updated_before: Union[Unset, datetime.datetime] = UNSET,
    updated_after: Union[Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, str] = UNSET,
    order_direction: Union[Unset, ConnectorControllerGetFilesOrderDirection] = UNSET,
    take: Union[Unset, float] = UNSET,
    skip: Union[Unset, float] = UNSET,
    x_org_slug: str,
) -> Response[ConnectorFilesResponse]:
    """
    Args:
        id (str):
        file_ids (Union[Unset, list[str]]):
        exclude_file_ids (Union[Unset, list[str]]):
        unique_external_ids (Union[Unset, list[str]]):
        exclude_unique_external_ids (Union[Unset, list[str]]):
        statuses (Union[Unset, list[ConnectorControllerGetFilesStatusesItem]]):
        max_errors (Union[Unset, float]):
        created_before (Union[Unset, datetime.datetime]):
        created_after (Union[Unset, datetime.datetime]):
        updated_before (Union[Unset, datetime.datetime]):
        updated_after (Union[Unset, datetime.datetime]):
        order_by (Union[Unset, str]):
        order_direction (Union[Unset, ConnectorControllerGetFilesOrderDirection]):
        take (Union[Unset, float]):
        skip (Union[Unset, float]):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorFilesResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        file_ids=file_ids,
        exclude_file_ids=exclude_file_ids,
        unique_external_ids=unique_external_ids,
        exclude_unique_external_ids=exclude_unique_external_ids,
        statuses=statuses,
        max_errors=max_errors,
        created_before=created_before,
        created_after=created_after,
        updated_before=updated_before,
        updated_after=updated_after,
        order_by=order_by,
        order_direction=order_direction,
        take=take,
        skip=skip,
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
    file_ids: Union[Unset, list[str]] = UNSET,
    exclude_file_ids: Union[Unset, list[str]] = UNSET,
    unique_external_ids: Union[Unset, list[str]] = UNSET,
    exclude_unique_external_ids: Union[Unset, list[str]] = UNSET,
    statuses: Union[Unset, list[ConnectorControllerGetFilesStatusesItem]] = UNSET,
    max_errors: Union[Unset, float] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    updated_before: Union[Unset, datetime.datetime] = UNSET,
    updated_after: Union[Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, str] = UNSET,
    order_direction: Union[Unset, ConnectorControllerGetFilesOrderDirection] = UNSET,
    take: Union[Unset, float] = UNSET,
    skip: Union[Unset, float] = UNSET,
    x_org_slug: str,
) -> Optional[ConnectorFilesResponse]:
    """
    Args:
        id (str):
        file_ids (Union[Unset, list[str]]):
        exclude_file_ids (Union[Unset, list[str]]):
        unique_external_ids (Union[Unset, list[str]]):
        exclude_unique_external_ids (Union[Unset, list[str]]):
        statuses (Union[Unset, list[ConnectorControllerGetFilesStatusesItem]]):
        max_errors (Union[Unset, float]):
        created_before (Union[Unset, datetime.datetime]):
        created_after (Union[Unset, datetime.datetime]):
        updated_before (Union[Unset, datetime.datetime]):
        updated_after (Union[Unset, datetime.datetime]):
        order_by (Union[Unset, str]):
        order_direction (Union[Unset, ConnectorControllerGetFilesOrderDirection]):
        take (Union[Unset, float]):
        skip (Union[Unset, float]):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorFilesResponse
    """

    return sync_detailed(
        id=id,
        client=client,
        file_ids=file_ids,
        exclude_file_ids=exclude_file_ids,
        unique_external_ids=unique_external_ids,
        exclude_unique_external_ids=exclude_unique_external_ids,
        statuses=statuses,
        max_errors=max_errors,
        created_before=created_before,
        created_after=created_after,
        updated_before=updated_before,
        updated_after=updated_after,
        order_by=order_by,
        order_direction=order_direction,
        take=take,
        skip=skip,
        x_org_slug=x_org_slug,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient,
    file_ids: Union[Unset, list[str]] = UNSET,
    exclude_file_ids: Union[Unset, list[str]] = UNSET,
    unique_external_ids: Union[Unset, list[str]] = UNSET,
    exclude_unique_external_ids: Union[Unset, list[str]] = UNSET,
    statuses: Union[Unset, list[ConnectorControllerGetFilesStatusesItem]] = UNSET,
    max_errors: Union[Unset, float] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    updated_before: Union[Unset, datetime.datetime] = UNSET,
    updated_after: Union[Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, str] = UNSET,
    order_direction: Union[Unset, ConnectorControllerGetFilesOrderDirection] = UNSET,
    take: Union[Unset, float] = UNSET,
    skip: Union[Unset, float] = UNSET,
    x_org_slug: str,
) -> Response[ConnectorFilesResponse]:
    """
    Args:
        id (str):
        file_ids (Union[Unset, list[str]]):
        exclude_file_ids (Union[Unset, list[str]]):
        unique_external_ids (Union[Unset, list[str]]):
        exclude_unique_external_ids (Union[Unset, list[str]]):
        statuses (Union[Unset, list[ConnectorControllerGetFilesStatusesItem]]):
        max_errors (Union[Unset, float]):
        created_before (Union[Unset, datetime.datetime]):
        created_after (Union[Unset, datetime.datetime]):
        updated_before (Union[Unset, datetime.datetime]):
        updated_after (Union[Unset, datetime.datetime]):
        order_by (Union[Unset, str]):
        order_direction (Union[Unset, ConnectorControllerGetFilesOrderDirection]):
        take (Union[Unset, float]):
        skip (Union[Unset, float]):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ConnectorFilesResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        file_ids=file_ids,
        exclude_file_ids=exclude_file_ids,
        unique_external_ids=unique_external_ids,
        exclude_unique_external_ids=exclude_unique_external_ids,
        statuses=statuses,
        max_errors=max_errors,
        created_before=created_before,
        created_after=created_after,
        updated_before=updated_before,
        updated_after=updated_after,
        order_by=order_by,
        order_direction=order_direction,
        take=take,
        skip=skip,
        x_org_slug=x_org_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient,
    file_ids: Union[Unset, list[str]] = UNSET,
    exclude_file_ids: Union[Unset, list[str]] = UNSET,
    unique_external_ids: Union[Unset, list[str]] = UNSET,
    exclude_unique_external_ids: Union[Unset, list[str]] = UNSET,
    statuses: Union[Unset, list[ConnectorControllerGetFilesStatusesItem]] = UNSET,
    max_errors: Union[Unset, float] = UNSET,
    created_before: Union[Unset, datetime.datetime] = UNSET,
    created_after: Union[Unset, datetime.datetime] = UNSET,
    updated_before: Union[Unset, datetime.datetime] = UNSET,
    updated_after: Union[Unset, datetime.datetime] = UNSET,
    order_by: Union[Unset, str] = UNSET,
    order_direction: Union[Unset, ConnectorControllerGetFilesOrderDirection] = UNSET,
    take: Union[Unset, float] = UNSET,
    skip: Union[Unset, float] = UNSET,
    x_org_slug: str,
) -> Optional[ConnectorFilesResponse]:
    """
    Args:
        id (str):
        file_ids (Union[Unset, list[str]]):
        exclude_file_ids (Union[Unset, list[str]]):
        unique_external_ids (Union[Unset, list[str]]):
        exclude_unique_external_ids (Union[Unset, list[str]]):
        statuses (Union[Unset, list[ConnectorControllerGetFilesStatusesItem]]):
        max_errors (Union[Unset, float]):
        created_before (Union[Unset, datetime.datetime]):
        created_after (Union[Unset, datetime.datetime]):
        updated_before (Union[Unset, datetime.datetime]):
        updated_after (Union[Unset, datetime.datetime]):
        order_by (Union[Unset, str]):
        order_direction (Union[Unset, ConnectorControllerGetFilesOrderDirection]):
        take (Union[Unset, float]):
        skip (Union[Unset, float]):
        x_org_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ConnectorFilesResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            file_ids=file_ids,
            exclude_file_ids=exclude_file_ids,
            unique_external_ids=unique_external_ids,
            exclude_unique_external_ids=exclude_unique_external_ids,
            statuses=statuses,
            max_errors=max_errors,
            created_before=created_before,
            created_after=created_after,
            updated_before=updated_before,
            updated_after=updated_after,
            order_by=order_by,
            order_direction=order_direction,
            take=take,
            skip=skip,
            x_org_slug=x_org_slug,
        )
    ).parsed
