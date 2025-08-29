from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.import_status import ImportStatus
from ..models.publish_status import PublishStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataSetListRespItem")


@_attrs_define
class DataSetListRespItem:
    """
    Attributes:
        id (int): id
        name (Union[None, Unset, str]): 数据集名称
        type_name (Union[None, Unset, str]): 数据集类型名称
        version (Union[None, Unset, int]): 最新版本
        last_version_id (Union[None, Unset, int]): 最新版本id
        content_count (Union[None, Unset, int]): 数据量
        import_status (Union[ImportStatus, None, Unset]): 导入状态（1: 导入中, 2: 导入成功, 3: 导入失败）
        publish_status (Union[None, PublishStatus, Unset]): 发布状态（1 草稿、2 发布）
        version_update_at (Union[None, Unset, str]): 版本更新时间
    """

    id: int
    name: Union[None, Unset, str] = UNSET
    type_name: Union[None, Unset, str] = UNSET
    version: Union[None, Unset, int] = UNSET
    last_version_id: Union[None, Unset, int] = UNSET
    content_count: Union[None, Unset, int] = UNSET
    import_status: Union[ImportStatus, None, Unset] = UNSET
    publish_status: Union[None, PublishStatus, Unset] = UNSET
    version_update_at: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        type_name: Union[None, Unset, str]
        if isinstance(self.type_name, Unset):
            type_name = UNSET
        else:
            type_name = self.type_name

        version: Union[None, Unset, int]
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        last_version_id: Union[None, Unset, int]
        if isinstance(self.last_version_id, Unset):
            last_version_id = UNSET
        else:
            last_version_id = self.last_version_id

        content_count: Union[None, Unset, int]
        if isinstance(self.content_count, Unset):
            content_count = UNSET
        else:
            content_count = self.content_count

        import_status: Union[None, Unset, int]
        if isinstance(self.import_status, Unset):
            import_status = UNSET
        elif isinstance(self.import_status, ImportStatus):
            import_status = self.import_status.value
        else:
            import_status = self.import_status

        publish_status: Union[None, Unset, int]
        if isinstance(self.publish_status, Unset):
            publish_status = UNSET
        elif isinstance(self.publish_status, PublishStatus):
            publish_status = self.publish_status.value
        else:
            publish_status = self.publish_status

        version_update_at: Union[None, Unset, str]
        if isinstance(self.version_update_at, Unset):
            version_update_at = UNSET
        else:
            version_update_at = self.version_update_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if type_name is not UNSET:
            field_dict["type_name"] = type_name
        if version is not UNSET:
            field_dict["version"] = version
        if last_version_id is not UNSET:
            field_dict["last_version_id"] = last_version_id
        if content_count is not UNSET:
            field_dict["content_count"] = content_count
        if import_status is not UNSET:
            field_dict["import_status"] = import_status
        if publish_status is not UNSET:
            field_dict["publish_status"] = publish_status
        if version_update_at is not UNSET:
            field_dict["version_update_at"] = version_update_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_type_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        type_name = _parse_type_name(d.pop("type_name", UNSET))

        def _parse_version(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        version = _parse_version(d.pop("version", UNSET))

        def _parse_last_version_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        last_version_id = _parse_last_version_id(d.pop("last_version_id", UNSET))

        def _parse_content_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        content_count = _parse_content_count(d.pop("content_count", UNSET))

        def _parse_import_status(data: object) -> Union[ImportStatus, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, int):
                    raise TypeError()
                import_status_type_0 = ImportStatus(data)

                return import_status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[ImportStatus, None, Unset], data)

        import_status = _parse_import_status(d.pop("import_status", UNSET))

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

        def _parse_version_update_at(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        version_update_at = _parse_version_update_at(d.pop("version_update_at", UNSET))

        data_set_list_resp_item = cls(
            id=id,
            name=name,
            type_name=type_name,
            version=version,
            last_version_id=last_version_id,
            content_count=content_count,
            import_status=import_status,
            publish_status=publish_status,
            version_update_at=version_update_at,
        )

        data_set_list_resp_item.additional_properties = d
        return data_set_list_resp_item

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
