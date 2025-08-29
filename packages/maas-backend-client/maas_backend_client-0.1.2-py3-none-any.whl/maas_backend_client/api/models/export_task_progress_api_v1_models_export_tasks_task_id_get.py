from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_response_model_version_export_task_progress_resp import (
    BaseResponseModelVersionExportTaskProgressResp,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    task_id: int,
    *,
    x_request_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["x-request-id"] = x_request_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/models/export_tasks/{task_id}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BaseResponseModelVersionExportTaskProgressResp.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]:
    """查询导出任务进度

     查询指定模型导出任务的状态与进度信息

    Args:
        task_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        task_id=task_id,
        x_request_id=x_request_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]:
    """查询导出任务进度

     查询指定模型导出任务的状态与进度信息

    Args:
        task_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]
    """

    return sync_detailed(
        task_id=task_id,
        client=client,
        x_request_id=x_request_id,
    ).parsed


async def asyncio_detailed(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]:
    """查询导出任务进度

     查询指定模型导出任务的状态与进度信息

    Args:
        task_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        task_id=task_id,
        x_request_id=x_request_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    task_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]]:
    """查询导出任务进度

     查询指定模型导出任务的状态与进度信息

    Args:
        task_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseModelVersionExportTaskProgressResp, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            task_id=task_id,
            client=client,
            x_request_id=x_request_id,
        )
    ).parsed
