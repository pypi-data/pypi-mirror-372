from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.base_response_none_type import BaseResponseNoneType
from ...models.http_validation_error import HTTPValidationError
from ...models.model_version_edit_req import ModelVersionEditReq
from ...types import UNSET, Response, Unset


def _get_kwargs(
    version_id: int,
    *,
    body: ModelVersionEditReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_request_id, Unset):
        headers["x-request-id"] = x_request_id

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/models/versions/{version_id}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BaseResponseNoneType, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = BaseResponseNoneType.from_dict(response.json())

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
) -> Response[Union[BaseResponseNoneType, HTTPValidationError]]:
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
    body: ModelVersionEditReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseNoneType, HTTPValidationError]]:
    """模型版本编辑

     修改某个模型版本的元信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):
        body (ModelVersionEditReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseNoneType, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        version_id=version_id,
        body=body,
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
    body: ModelVersionEditReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseNoneType, HTTPValidationError]]:
    """模型版本编辑

     修改某个模型版本的元信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):
        body (ModelVersionEditReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseNoneType, HTTPValidationError]
    """

    return sync_detailed(
        version_id=version_id,
        client=client,
        body=body,
        x_request_id=x_request_id,
    ).parsed


async def asyncio_detailed(
    version_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelVersionEditReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Response[Union[BaseResponseNoneType, HTTPValidationError]]:
    """模型版本编辑

     修改某个模型版本的元信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):
        body (ModelVersionEditReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BaseResponseNoneType, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        version_id=version_id,
        body=body,
        x_request_id=x_request_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    version_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelVersionEditReq,
    x_request_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BaseResponseNoneType, HTTPValidationError]]:
    """模型版本编辑

     修改某个模型版本的元信息

    Args:
        version_id (int):
        x_request_id (Union[Unset, str]):
        body (ModelVersionEditReq):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BaseResponseNoneType, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            version_id=version_id,
            client=client,
            body=body,
            x_request_id=x_request_id,
        )
    ).parsed
