from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_set_template_file_format import DataSetTemplateFileFormat

T = TypeVar("T", bound="DataSetTemplateReq")


@_attrs_define
class DataSetTemplateReq:
    """
    Attributes:
        type_id (int): 类型id
        file_format (DataSetTemplateFileFormat):
    """

    type_id: int
    file_format: DataSetTemplateFileFormat
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_id = self.type_id

        file_format = self.file_format.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type_id": type_id,
                "file_format": file_format,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_id = d.pop("type_id")

        file_format = DataSetTemplateFileFormat(d.pop("file_format"))

        data_set_template_req = cls(
            type_id=type_id,
            file_format=file_format,
        )

        data_set_template_req.additional_properties = d
        return data_set_template_req

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
