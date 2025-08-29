from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelCreateReq")


@_attrs_define
class ModelCreateReq:
    """
    Attributes:
        name (str): 模型名称，如 `YOLOv5`
        model_type (str): 模型类别，如 `YOLO`, `Qwen`, `OCR`
        task_types (list[str]): 支持的任务类型列表，如 `["chat","embedding"]`
        file_id (Union[None, Unset, int]): 基础模型文件ID
        description (Union[None, Unset, str]): 模型介绍
    """

    name: str
    model_type: str
    task_types: list[str]
    file_id: Union[None, Unset, int] = UNSET
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        model_type = self.model_type

        task_types = self.task_types

        file_id: Union[None, Unset, int]
        if isinstance(self.file_id, Unset):
            file_id = UNSET
        else:
            file_id = self.file_id

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "model_type": model_type,
                "task_types": task_types,
            }
        )
        if file_id is not UNSET:
            field_dict["file_id"] = file_id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        model_type = d.pop("model_type")

        task_types = cast(list[str], d.pop("task_types"))

        def _parse_file_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        file_id = _parse_file_id(d.pop("file_id", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        model_create_req = cls(
            name=name,
            model_type=model_type,
            task_types=task_types,
            file_id=file_id,
            description=description,
        )

        model_create_req.additional_properties = d
        return model_create_req

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
