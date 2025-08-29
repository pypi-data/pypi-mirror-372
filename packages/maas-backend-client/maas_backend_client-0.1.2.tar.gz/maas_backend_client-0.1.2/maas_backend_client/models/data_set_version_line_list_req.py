from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataSetVersionLineListReq")


@_attrs_define
class DataSetVersionLineListReq:
    """
    Attributes:
        page (Union[Unset, int]): 当前页码 Default: 1.
        page_size (Union[Unset, int]): 页容量 Default: 10.
        role (Union[None, Unset, str]): 角色
        content (Union[None, Unset, str]): 内容
    """

    page: Union[Unset, int] = 1
    page_size: Union[Unset, int] = 10
    role: Union[None, Unset, str] = UNSET
    content: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page

        page_size = self.page_size

        role: Union[None, Unset, str]
        if isinstance(self.role, Unset):
            role = UNSET
        else:
            role = self.role

        content: Union[None, Unset, str]
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if page is not UNSET:
            field_dict["page"] = page
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if role is not UNSET:
            field_dict["role"] = role
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        page = d.pop("page", UNSET)

        page_size = d.pop("page_size", UNSET)

        def _parse_role(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        role = _parse_role(d.pop("role", UNSET))

        def _parse_content(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        content = _parse_content(d.pop("content", UNSET))

        data_set_version_line_list_req = cls(
            page=page,
            page_size=page_size,
            role=role,
            content=content,
        )

        data_set_version_line_list_req.additional_properties = d
        return data_set_version_line_list_req

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
