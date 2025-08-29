from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.publish_status import PublishStatus

T = TypeVar("T", bound="DataSetCreateReq")


@_attrs_define
class DataSetCreateReq:
    """
    Attributes:
        name (str): 名称
        type_id (int): 类型id
        file_ids (list[int]): 上传的文件id
        publish_status (PublishStatus):
    """

    name: str
    type_id: int
    file_ids: list[int]
    publish_status: PublishStatus
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_id = self.type_id

        file_ids = self.file_ids

        publish_status = self.publish_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type_id": type_id,
                "file_ids": file_ids,
                "publish_status": publish_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        type_id = d.pop("type_id")

        file_ids = cast(list[int], d.pop("file_ids"))

        publish_status = PublishStatus(d.pop("publish_status"))

        data_set_create_req = cls(
            name=name,
            type_id=type_id,
            file_ids=file_ids,
            publish_status=publish_status,
        )

        data_set_create_req.additional_properties = d
        return data_set_create_req

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
