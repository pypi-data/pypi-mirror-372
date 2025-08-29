from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadInitReq")


@_attrs_define
class UploadInitReq:
    """
    Attributes:
        md5 (str): 文件 md5
        file_name (str): 文件名称
        file_size (int): 文件大小(单位 byte)
        part_size (Union[Unset, int]): 分片大小(单位 m，分片上传 >= 5，非分片 = 0) Default: 0.
    """

    md5: str
    file_name: str
    file_size: int
    part_size: Union[Unset, int] = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        md5 = self.md5

        file_name = self.file_name

        file_size = self.file_size

        part_size = self.part_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "md5": md5,
                "file_name": file_name,
                "file_size": file_size,
            }
        )
        if part_size is not UNSET:
            field_dict["part_size"] = part_size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        md5 = d.pop("md5")

        file_name = d.pop("file_name")

        file_size = d.pop("file_size")

        part_size = d.pop("part_size", UNSET)

        upload_init_req = cls(
            md5=md5,
            file_name=file_name,
            file_size=file_size,
            part_size=part_size,
        )

        upload_init_req.additional_properties = d
        return upload_init_req

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
