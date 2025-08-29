from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelListItem")


@_attrs_define
class ModelListItem:
    """
    Attributes:
        id (int): 模型 ID
        name (str): 模型名称
        type_ (str): 模型类别
        task_types (list[str]): 支持的任务类型列表
        version_count (int): 模型的版本数量
        description (Union[None, Unset, str]): 模型介绍
    """

    id: int
    name: str
    type_: str
    task_types: list[str]
    version_count: int
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_ = self.type_

        task_types = self.task_types

        version_count = self.version_count

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "type": type_,
                "task_types": task_types,
                "version_count": version_count,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        type_ = d.pop("type")

        task_types = cast(list[str], d.pop("task_types"))

        version_count = d.pop("version_count")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        model_list_item = cls(
            id=id,
            name=name,
            type_=type_,
            task_types=task_types,
            version_count=version_count,
            description=description,
        )

        model_list_item.additional_properties = d
        return model_list_item

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
