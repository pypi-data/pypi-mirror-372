from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataSetVersionFileReq")


@_attrs_define
class DataSetVersionFileReq:
    """
    Attributes:
        page (Union[Unset, int]): 当前页码 Default: 1.
        page_size (Union[Unset, int]): 页容量 Default: 10.
        directory_id (Union[None, Unset, int]): 目录 ID，若指定则只列出该目录下的文件
    """

    page: Union[Unset, int] = 1
    page_size: Union[Unset, int] = 10
    directory_id: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page

        page_size = self.page_size

        directory_id: Union[None, Unset, int]
        if isinstance(self.directory_id, Unset):
            directory_id = UNSET
        else:
            directory_id = self.directory_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if page is not UNSET:
            field_dict["page"] = page
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if directory_id is not UNSET:
            field_dict["directory_id"] = directory_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        page = d.pop("page", UNSET)

        page_size = d.pop("page_size", UNSET)

        def _parse_directory_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        directory_id = _parse_directory_id(d.pop("directory_id", UNSET))

        data_set_version_file_req = cls(
            page=page,
            page_size=page_size,
            directory_id=directory_id,
        )

        data_set_version_file_req.additional_properties = d
        return data_set_version_file_req

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
