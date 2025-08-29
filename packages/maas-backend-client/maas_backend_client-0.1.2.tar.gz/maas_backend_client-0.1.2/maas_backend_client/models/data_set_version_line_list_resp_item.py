from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_set_version_line_content_item import DataSetVersionLineContentItem


T = TypeVar("T", bound="DataSetVersionLineListRespItem")


@_attrs_define
class DataSetVersionLineListRespItem:
    """
    Attributes:
        id (int): id
        content_list (list['DataSetVersionLineContentItem']): 内容列表
    """

    id: int
    content_list: list["DataSetVersionLineContentItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        content_list = []
        for content_list_item_data in self.content_list:
            content_list_item = content_list_item_data.to_dict()
            content_list.append(content_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "content_list": content_list,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_set_version_line_content_item import DataSetVersionLineContentItem

        d = dict(src_dict)
        id = d.pop("id")

        content_list = []
        _content_list = d.pop("content_list")
        for content_list_item_data in _content_list:
            content_list_item = DataSetVersionLineContentItem.from_dict(content_list_item_data)

            content_list.append(content_list_item)

        data_set_version_line_list_resp_item = cls(
            id=id,
            content_list=content_list,
        )

        data_set_version_line_list_resp_item.additional_properties = d
        return data_set_version_line_list_resp_item

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
