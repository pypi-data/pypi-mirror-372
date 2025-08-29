from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.publish_status import PublishStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataSetVersionCreateReq")


@_attrs_define
class DataSetVersionCreateReq:
    """
    Attributes:
        publish_status (PublishStatus):
        version_id (Union[None, Unset, int]): 继承的 version_id
        file_ids (Union[None, Unset, list[int]]): 上传的文件id
    """

    publish_status: PublishStatus
    version_id: Union[None, Unset, int] = UNSET
    file_ids: Union[None, Unset, list[int]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        publish_status = self.publish_status.value

        version_id: Union[None, Unset, int]
        if isinstance(self.version_id, Unset):
            version_id = UNSET
        else:
            version_id = self.version_id

        file_ids: Union[None, Unset, list[int]]
        if isinstance(self.file_ids, Unset):
            file_ids = UNSET
        elif isinstance(self.file_ids, list):
            file_ids = self.file_ids

        else:
            file_ids = self.file_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "publish_status": publish_status,
            }
        )
        if version_id is not UNSET:
            field_dict["version_id"] = version_id
        if file_ids is not UNSET:
            field_dict["file_ids"] = file_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        publish_status = PublishStatus(d.pop("publish_status"))

        def _parse_version_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        version_id = _parse_version_id(d.pop("version_id", UNSET))

        def _parse_file_ids(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                file_ids_type_0 = cast(list[int], data)

                return file_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        file_ids = _parse_file_ids(d.pop("file_ids", UNSET))

        data_set_version_create_req = cls(
            publish_status=publish_status,
            version_id=version_id,
            file_ids=file_ids,
        )

        data_set_version_create_req.additional_properties = d
        return data_set_version_create_req

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
