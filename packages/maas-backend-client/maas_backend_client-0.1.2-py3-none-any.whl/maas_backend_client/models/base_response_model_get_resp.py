from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_get_resp import ModelGetResp


T = TypeVar("T", bound="BaseResponseModelGetResp")


@_attrs_define
class BaseResponseModelGetResp:
    """
    Attributes:
        code (Union[Unset, int]):  Default: 200.
        message (Union[Unset, str]):  Default: 'success'.
        data (Union['ModelGetResp', None, Unset]):
        request_id (Union[None, Unset, str]):
    """

    code: Union[Unset, int] = 200
    message: Union[Unset, str] = "success"
    data: Union["ModelGetResp", None, Unset] = UNSET
    request_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_get_resp import ModelGetResp

        code = self.code

        message = self.message

        data: Union[None, Unset, dict[str, Any]]
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, ModelGetResp):
            data = self.data.to_dict()
        else:
            data = self.data

        request_id: Union[None, Unset, str]
        if isinstance(self.request_id, Unset):
            request_id = UNSET
        else:
            request_id = self.request_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if message is not UNSET:
            field_dict["message"] = message
        if data is not UNSET:
            field_dict["data"] = data
        if request_id is not UNSET:
            field_dict["request_id"] = request_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_get_resp import ModelGetResp

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        message = d.pop("message", UNSET)

        def _parse_data(data: object) -> Union["ModelGetResp", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = ModelGetResp.from_dict(data)

                return data_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ModelGetResp", None, Unset], data)

        data = _parse_data(d.pop("data", UNSET))

        def _parse_request_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        request_id = _parse_request_id(d.pop("request_id", UNSET))

        base_response_model_get_resp = cls(
            code=code,
            message=message,
            data=data,
            request_id=request_id,
        )

        base_response_model_get_resp.additional_properties = d
        return base_response_model_get_resp

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
