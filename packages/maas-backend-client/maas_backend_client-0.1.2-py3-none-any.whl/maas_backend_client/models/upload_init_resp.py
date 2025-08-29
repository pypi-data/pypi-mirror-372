from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.upload_path_resp_item import UploadPathRespItem


T = TypeVar("T", bound="UploadInitResp")


@_attrs_define
class UploadInitResp:
    """
    Attributes:
        is_exist (bool): 文件是否已经存在
        file_id (int): 文件id
        path_list (list['UploadPathRespItem']): 上传地址列表
    """

    is_exist: bool
    file_id: int
    path_list: list["UploadPathRespItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_exist = self.is_exist

        file_id = self.file_id

        path_list = []
        for path_list_item_data in self.path_list:
            path_list_item = path_list_item_data.to_dict()
            path_list.append(path_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_exist": is_exist,
                "file_id": file_id,
                "path_list": path_list,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.upload_path_resp_item import UploadPathRespItem

        d = dict(src_dict)
        is_exist = d.pop("is_exist")

        file_id = d.pop("file_id")

        path_list = []
        _path_list = d.pop("path_list")
        for path_list_item_data in _path_list:
            path_list_item = UploadPathRespItem.from_dict(path_list_item_data)

            path_list.append(path_list_item)

        upload_init_resp = cls(
            is_exist=is_exist,
            file_id=file_id,
            path_list=path_list,
        )

        upload_init_resp.additional_properties = d
        return upload_init_resp

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
