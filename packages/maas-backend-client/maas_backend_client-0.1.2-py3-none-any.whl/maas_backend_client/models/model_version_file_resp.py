from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.model_version_file_resp_dir_item import ModelVersionFileRespDirItem
    from ..models.model_version_file_resp_file_item import ModelVersionFileRespFileItem


T = TypeVar("T", bound="ModelVersionFileResp")


@_attrs_define
class ModelVersionFileResp:
    """
    Attributes:
        dirs (list['ModelVersionFileRespDirItem']): 子目录列表
        files (list['ModelVersionFileRespFileItem']): 文件列表
    """

    dirs: list["ModelVersionFileRespDirItem"]
    files: list["ModelVersionFileRespFileItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dirs = []
        for dirs_item_data in self.dirs:
            dirs_item = dirs_item_data.to_dict()
            dirs.append(dirs_item)

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dirs": dirs,
                "files": files,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_version_file_resp_dir_item import ModelVersionFileRespDirItem
        from ..models.model_version_file_resp_file_item import ModelVersionFileRespFileItem

        d = dict(src_dict)
        dirs = []
        _dirs = d.pop("dirs")
        for dirs_item_data in _dirs:
            dirs_item = ModelVersionFileRespDirItem.from_dict(dirs_item_data)

            dirs.append(dirs_item)

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = ModelVersionFileRespFileItem.from_dict(files_item_data)

            files.append(files_item)

        model_version_file_resp = cls(
            dirs=dirs,
            files=files,
        )

        model_version_file_resp.additional_properties = d
        return model_version_file_resp

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
