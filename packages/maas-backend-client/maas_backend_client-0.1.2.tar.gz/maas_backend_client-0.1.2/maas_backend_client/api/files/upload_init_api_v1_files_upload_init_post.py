from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_response_upload_init_resp import BaseResponseUploadInitResp
from ...models.http_validation_error import HTTPValidationError
from ...models.upload_init_req import UploadInitReq
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: UploadInitReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["x-request-id"] = x_request_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/files/upload/init",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BaseResponseUploadInitResp, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BaseResponseUploadInitResp.from_dict(response.json())

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
) -> Response[Union[BaseResponseUploadInitResp, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadInitReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseUploadInitResp, HTTPValidationError]]:
    """上传初始化

     上传初始化

    Args:
        x_request_id (Union[Unset, str]):
        body (UploadInitReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseUploadInitResp, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        x_request_id=x_request_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadInitReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseUploadInitResp, HTTPValidationError]]:
    """上传初始化

     上传初始化

    Args:
        x_request_id (Union[Unset, str]):
        body (UploadInitReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseUploadInitResp, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        x_request_id=x_request_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadInitReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseUploadInitResp, HTTPValidationError]]:
    """上传初始化

     上传初始化

    Args:
        x_request_id (Union[Unset, str]):
        body (UploadInitReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseUploadInitResp, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        x_request_id=x_request_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: UploadInitReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseUploadInitResp, HTTPValidationError]]:
    """上传初始化

     上传初始化

    Args:
        x_request_id (Union[Unset, str]):
        body (UploadInitReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseUploadInitResp, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_request_id=x_request_id,
        )
    ).parsed
