from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ModelVersionFileRespFileItem")


@_attrs_define
class ModelVersionFileRespFileItem:
    """
    Attributes:
        id (int): 文件 ID
        name (str): 文件名称
        size (int): 文件大小，单位字节
        created_at (Union[None, str]): 创建时间
        updated_at (Union[None, str]): 更新时间
    """

    id: int
    name: str
    size: int
    created_at: Union[None, str]
    updated_at: Union[None, str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        size = self.size

        created_at: Union[None, str]
        created_at = self.created_at

        updated_at: Union[None, str]
        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "size": size,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        size = d.pop("size")

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

        model_version_file_resp_file_item = cls(
            id=id,
            name=name,
            size=size,
            created_at=created_at,
            updated_at=updated_at,
        )

        model_version_file_resp_file_item.additional_properties = d
        return model_version_file_resp_file_item

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
