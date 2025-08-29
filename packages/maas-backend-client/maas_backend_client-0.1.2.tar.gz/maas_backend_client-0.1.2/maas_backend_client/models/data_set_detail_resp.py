from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_set_detail_resp_version_item import DataSetDetailRespVersionItem


T = TypeVar("T", bound="DataSetDetailResp")


@_attrs_define
class DataSetDetailResp:
    """
    Attributes:
        id (int): id
        name (str): 名称
        version_list (list['DataSetDetailRespVersionItem']): 版本列表
        type_name (Union[None, Unset, str]): 数据集类型名称
    """

    id: int
    name: str
    version_list: list["DataSetDetailRespVersionItem"]
    type_name: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        version_list = []
        for version_list_item_data in self.version_list:
            version_list_item = version_list_item_data.to_dict()
            version_list.append(version_list_item)

        type_name: Union[None, Unset, str]
        if isinstance(self.type_name, Unset):
            type_name = UNSET
        else:
            type_name = self.type_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "version_list": version_list,
            }
        )
        if type_name is not UNSET:
            field_dict["type_name"] = type_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_set_detail_resp_version_item import DataSetDetailRespVersionItem

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        version_list = []
        _version_list = d.pop("version_list")
        for version_list_item_data in _version_list:
            version_list_item = DataSetDetailRespVersionItem.from_dict(version_list_item_data)

            version_list.append(version_list_item)

        def _parse_type_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        type_name = _parse_type_name(d.pop("type_name", UNSET))

        data_set_detail_resp = cls(
            id=id,
            name=name,
            version_list=version_list,
            type_name=type_name,
        )

        data_set_detail_resp.additional_properties = d
        return data_set_detail_resp

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
