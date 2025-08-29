from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.type_ import Type

T = TypeVar("T", bound="DataSetTypeRespItem")


@_attrs_define
class DataSetTypeRespItem:
    """
    Attributes:
        id (int): id
        name (str): 名称
        template_format (list[str]): 模板格式
        type_ (Type):
    """

    id: int
    name: str
    template_format: list[str]
    type_: Type
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        template_format = self.template_format

        type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "template_format": template_format,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        template_format = cast(list[str], d.pop("template_format"))

        type_ = Type(d.pop("type"))

        data_set_type_resp_item = cls(
            id=id,
            name=name,
            template_format=template_format,
            type_=type_,
        )

        data_set_type_resp_item.additional_properties = d
        return data_set_type_resp_item

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
