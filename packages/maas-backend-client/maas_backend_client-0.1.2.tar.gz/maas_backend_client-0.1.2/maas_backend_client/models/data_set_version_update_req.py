from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.publish_status import PublishStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataSetVersionUpdateReq")


@_attrs_define
class DataSetVersionUpdateReq:
    """
    Attributes:
        append_file_ids (Union[None, Unset, list[int]]): 新导入的文件id
        publish_status (Union[None, PublishStatus, Unset]): 发布状态（1 草稿、2 发布）
    """

    append_file_ids: Union[None, Unset, list[int]] = UNSET
    publish_status: Union[None, PublishStatus, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        append_file_ids: Union[None, Unset, list[int]]
        if isinstance(self.append_file_ids, Unset):
            append_file_ids = UNSET
        elif isinstance(self.append_file_ids, list):
            append_file_ids = self.append_file_ids

        else:
            append_file_ids = self.append_file_ids

        publish_status: Union[None, Unset, int]
        if isinstance(self.publish_status, Unset):
            publish_status = UNSET
        elif isinstance(self.publish_status, PublishStatus):
            publish_status = self.publish_status.value
        else:
            publish_status = self.publish_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if append_file_ids is not UNSET:
            field_dict["append_file_ids"] = append_file_ids
        if publish_status is not UNSET:
            field_dict["publish_status"] = publish_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_append_file_ids(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                append_file_ids_type_0 = cast(list[int], data)

                return append_file_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        append_file_ids = _parse_append_file_ids(d.pop("append_file_ids", UNSET))

        def _parse_publish_status(data: object) -> Union[None, PublishStatus, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, int):
                    raise TypeError()
                publish_status_type_0 = PublishStatus(data)

                return publish_status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, PublishStatus, Unset], data)

        publish_status = _parse_publish_status(d.pop("publish_status", UNSET))

        data_set_version_update_req = cls(
            append_file_ids=append_file_ids,
            publish_status=publish_status,
        )

        data_set_version_update_req.additional_properties = d
        return data_set_version_update_req

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
