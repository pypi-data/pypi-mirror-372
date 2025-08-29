from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.import_status import ImportStatus
from ..models.publish_status import PublishStatus

T = TypeVar("T", bound="DataSetDetailRespVersionItem")


@_attrs_define
class DataSetDetailRespVersionItem:
    """
    Attributes:
        id (int): id
        version (int): 版本号
        content_count (int): 数据量
        import_status (ImportStatus):
        publish_status (PublishStatus):
        created_at (Union[None, str]): 版本创建时间
    """

    id: int
    version: int
    content_count: int
    import_status: ImportStatus
    publish_status: PublishStatus
    created_at: Union[None, str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        version = self.version

        content_count = self.content_count

        import_status = self.import_status.value

        publish_status = self.publish_status.value

        created_at: Union[None, str]
        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "version": version,
                "content_count": content_count,
                "import_status": import_status,
                "publish_status": publish_status,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        version = d.pop("version")

        content_count = d.pop("content_count")

        import_status = ImportStatus(d.pop("import_status"))

        publish_status = PublishStatus(d.pop("publish_status"))

        def _parse_created_at(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        created_at = _parse_created_at(d.pop("created_at"))

        data_set_detail_resp_version_item = cls(
            id=id,
            version=version,
            content_count=content_count,
            import_status=import_status,
            publish_status=publish_status,
            created_at=created_at,
        )

        data_set_detail_resp_version_item.additional_properties = d
        return data_set_detail_resp_version_item

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
