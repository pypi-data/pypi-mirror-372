from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelGetResp")


@_attrs_define
class ModelGetResp:
    """
    Attributes:
        id (int): 模型 ID
        name (str): 模型名称
        model_type (str): 模型类别
        task_types (list[str]): 支持的任务类型列表
        version_ids (list[int]): 版本 ID 列表
        created_at (Union[None, str]): 创建时间
        updated_at (Union[None, str]): 更新时间
        description (Union[None, Unset, str]): 模型介绍
    """

    id: int
    name: str
    model_type: str
    task_types: list[str]
    version_ids: list[int]
    created_at: Union[None, str]
    updated_at: Union[None, str]
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        model_type = self.model_type

        task_types = self.task_types

        version_ids = self.version_ids

        created_at: Union[None, str]
        created_at = self.created_at

        updated_at: Union[None, str]
        updated_at = self.updated_at

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
                "model_type": model_type,
                "task_types": task_types,
                "version_ids": version_ids,
                "created_at": created_at,
                "updated_at": updated_at,
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

        model_type = d.pop("model_type")

        task_types = cast(list[str], d.pop("task_types"))

        version_ids = cast(list[int], d.pop("version_ids"))

        def _parse_created_at(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        created_at = _parse_created_at(d.pop("created_at"))

        def _parse_updated_at(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        updated_at = _parse_updated_at(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        model_get_resp = cls(
            id=id,
            name=name,
            model_type=model_type,
            task_types=task_types,
            version_ids=version_ids,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
        )

        model_get_resp.additional_properties = d
        return model_get_resp

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
