from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelEditReq")


@_attrs_define
class ModelEditReq:
    """
    Attributes:
        name (Union[None, Unset, str]): 模型名称
        model_type (Union[None, Unset, str]): 模型类别
        description (Union[None, Unset, str]): 模型介绍
        task_types (Union[None, Unset, list[str]]): 支持的任务类型列表
    """

    name: Union[None, Unset, str] = UNSET
    model_type: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    task_types: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        model_type: Union[None, Unset, str]
        if isinstance(self.model_type, Unset):
            model_type = UNSET
        else:
            model_type = self.model_type

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        task_types: Union[None, Unset, list[str]]
        if isinstance(self.task_types, Unset):
            task_types = UNSET
        elif isinstance(self.task_types, list):
            task_types = self.task_types

        else:
            task_types = self.task_types

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if model_type is not UNSET:
            field_dict["model_type"] = model_type
        if description is not UNSET:
            field_dict["description"] = description
        if task_types is not UNSET:
            field_dict["task_types"] = task_types

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_model_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        model_type = _parse_model_type(d.pop("model_type", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_task_types(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                task_types_type_0 = cast(list[str], data)

                return task_types_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        task_types = _parse_task_types(d.pop("task_types", UNSET))

        model_edit_req = cls(
            name=name,
            model_type=model_type,
            description=description,
            task_types=task_types,
        )

        model_edit_req.additional_properties = d
        return model_edit_req

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
