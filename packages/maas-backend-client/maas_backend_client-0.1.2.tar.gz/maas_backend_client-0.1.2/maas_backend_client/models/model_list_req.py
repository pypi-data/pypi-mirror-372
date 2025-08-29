from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelListReq")


@_attrs_define
class ModelListReq:
    """
    Attributes:
        page (Union[Unset, int]): 当前页码 Default: 1.
        page_size (Union[Unset, int]): 页容量 Default: 10.
        type_ (Union[None, Unset, str]): 模型类别过滤，如 `YOLO`, `Qwen`, `OCR`
        task_type (Union[None, Unset, str]): 按支持任务类型过滤，如 `chat`, `embedding`
    """

    page: Union[Unset, int] = 1
    page_size: Union[Unset, int] = 10
    type_: Union[None, Unset, str] = UNSET
    task_type: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page

        page_size = self.page_size

        type_: Union[None, Unset, str]
        if isinstance(self.type_, Unset):
            type_ = UNSET
        else:
            type_ = self.type_

        task_type: Union[None, Unset, str]
        if isinstance(self.task_type, Unset):
            task_type = UNSET
        else:
            task_type = self.task_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if page is not UNSET:
            field_dict["page"] = page
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if type_ is not UNSET:
            field_dict["type"] = type_
        if task_type is not UNSET:
            field_dict["task_type"] = task_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        page = d.pop("page", UNSET)

        page_size = d.pop("page_size", UNSET)

        def _parse_type_(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        type_ = _parse_type_(d.pop("type", UNSET))

        def _parse_task_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        task_type = _parse_task_type(d.pop("task_type", UNSET))

        model_list_req = cls(
            page=page,
            page_size=page_size,
            type_=type_,
            task_type=task_type,
        )

        model_list_req.additional_properties = d
        return model_list_req

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
