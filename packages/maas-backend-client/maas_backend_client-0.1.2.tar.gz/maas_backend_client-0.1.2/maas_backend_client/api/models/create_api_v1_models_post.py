from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_response_model_create_resp import BaseResponseModelCreateResp
from ...models.http_validation_error import HTTPValidationError
from ...models.model_create_req import ModelCreateReq
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: ModelCreateReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["x-request-id"] = x_request_id

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/models",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BaseResponseModelCreateResp, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BaseResponseModelCreateResp.from_dict(response.json())

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
) -> Response[Union[BaseResponseModelCreateResp, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelCreateReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseModelCreateResp, HTTPValidationError]]:
    """模型创建

     模型创建

    Args:
        x_request_id (Union[Unset, str]):
        body (ModelCreateReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseModelCreateResp, HTTPValidationError]]
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
    body: ModelCreateReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseModelCreateResp, HTTPValidationError]]:
    """模型创建

     模型创建

    Args:
        x_request_id (Union[Unset, str]):
        body (ModelCreateReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseModelCreateResp, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        x_request_id=x_request_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelCreateReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseModelCreateResp, HTTPValidationError]]:
    """模型创建

     模型创建

    Args:
        x_request_id (Union[Unset, str]):
        body (ModelCreateReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseModelCreateResp, HTTPValidationError]]
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
    body: ModelCreateReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseModelCreateResp, HTTPValidationError]]:
    """模型创建

     模型创建

    Args:
        x_request_id (Union[Unset, str]):
        body (ModelCreateReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseModelCreateResp, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_request_id=x_request_id,
        )
    ).parsed
