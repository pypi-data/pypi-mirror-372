from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_set_list_resp_item import DataSetListRespItem


T = TypeVar("T", bound="DataSetListResp")


@_attrs_define
class DataSetListResp:
    """
    Attributes:
        list_ (list['DataSetListRespItem']):
    """

    list_: list["DataSetListRespItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        list_ = []
        for list_item_data in self.list_:
            list_item = list_item_data.to_dict()
            list_.append(list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "list": list_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_set_list_resp_item import DataSetListRespItem

        d = dict(src_dict)
        list_ = []
        _list_ = d.pop("list")
        for list_item_data in _list_:
            list_item = DataSetListRespItem.from_dict(list_item_data)

            list_.append(list_item)

        data_set_list_resp = cls(
            list_=list_,
        )

        data_set_list_resp.additional_properties = d
        return data_set_list_resp

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
