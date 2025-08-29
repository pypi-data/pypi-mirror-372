from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModelVersionListReq")


@_attrs_define
class ModelVersionListReq:
    """
    Attributes:
        model_id (int): 模型 ID
        page (Union[Unset, int]): 当前页码 Default: 1.
        page_size (Union[Unset, int]): 页容量 Default: 10.
    """

    model_id: int
    page: Union[Unset, int] = 1
    page_size: Union[Unset, int] = 10
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        model_id = self.model_id

        page = self.page

        page_size = self.page_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_id": model_id,
            }
        )
        if page is not UNSET:
            field_dict["page"] = page
        if page_size is not UNSET:
            field_dict["page_size"] = page_size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        model_id = d.pop("model_id")

        page = d.pop("page", UNSET)

        page_size = d.pop("page_size", UNSET)

        model_version_list_req = cls(
            model_id=model_id,
            page=page,
            page_size=page_size,
        )

        model_version_list_req.additional_properties = d
        return model_version_list_req

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
