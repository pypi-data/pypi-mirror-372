from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ModelVersionGetRespRelatedDataSet")


@_attrs_define
class ModelVersionGetRespRelatedDataSet:
    """
    Attributes:
        data_set_id (int): 数据集id
        data_set_name (str): 数据集id
        created_at (Union[None, str]): 关联时间
    """

    data_set_id: int
    data_set_name: str
    created_at: Union[None, str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_set_id = self.data_set_id

        data_set_name = self.data_set_name

        created_at: Union[None, str]
        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_set_id": data_set_id,
                "data_set_name": data_set_name,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data_set_id = d.pop("data_set_id")

        data_set_name = d.pop("data_set_name")

        def _parse_created_at(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        created_at = _parse_created_at(d.pop("created_at"))

        model_version_get_resp_related_data_set = cls(
            data_set_id=data_set_id,
            data_set_name=data_set_name,
            created_at=created_at,
        )

        model_version_get_resp_related_data_set.additional_properties = d
        return model_version_get_resp_related_data_set

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
