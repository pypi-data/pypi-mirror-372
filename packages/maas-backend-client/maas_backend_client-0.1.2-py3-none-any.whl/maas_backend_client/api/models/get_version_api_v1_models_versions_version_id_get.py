from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_response_model_version_get_resp import BaseResponseModelVersionGetResp
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    version_id: int,
    *,
    x_request_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["x-request-id"] = x_request_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/models/versions/{version_id}",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BaseResponseModelVersionGetResp.from_dict(response.json())

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
) -> Response[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    version_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]:
    """获取模型版本详情

     查询某个模型版本的详细信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        version_id=version_id,
        x_request_id=x_request_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    version_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]:
    """获取模型版本详情

     查询某个模型版本的详细信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseModelVersionGetResp, HTTPValidationError]
    """

    return sync_detailed(
        version_id=version_id,
        client=client,
        x_request_id=x_request_id,
    ).parsed


async def asyncio_detailed(
    version_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]:
    """获取模型版本详情

     查询某个模型版本的详细信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        version_id=version_id,
        x_request_id=x_request_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    version_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseModelVersionGetResp, HTTPValidationError]]:
    """获取模型版本详情

     查询某个模型版本的详细信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseModelVersionGetResp, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            version_id=version_id,
            client=client,
            x_request_id=x_request_id,
        )
    ).parsed
