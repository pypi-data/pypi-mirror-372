from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_set_version_line_list_resp_item import DataSetVersionLineListRespItem


T = TypeVar("T", bound="DataSetVersionLineListResp")


@_attrs_define
class DataSetVersionLineListResp:
    """
    Attributes:
        data_list (list['DataSetVersionLineListRespItem']): 行列表
        role_list (list[str]): 角色列表
    """

    data_list: list["DataSetVersionLineListRespItem"]
    role_list: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_list = []
        for data_list_item_data in self.data_list:
            data_list_item = data_list_item_data.to_dict()
            data_list.append(data_list_item)

        role_list = self.role_list

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_list": data_list,
                "role_list": role_list,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_set_version_line_list_resp_item import DataSetVersionLineListRespItem

        d = dict(src_dict)
        data_list = []
        _data_list = d.pop("data_list")
        for data_list_item_data in _data_list:
            data_list_item = DataSetVersionLineListRespItem.from_dict(data_list_item_data)

            data_list.append(data_list_item)

        role_list = cast(list[str], d.pop("role_list"))

        data_set_version_line_list_resp = cls(
            data_list=data_list,
            role_list=role_list,
        )

        data_set_version_line_list_resp.additional_properties = d
        return data_set_version_line_list_resp

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
