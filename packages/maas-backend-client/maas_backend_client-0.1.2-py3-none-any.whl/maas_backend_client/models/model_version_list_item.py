from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_version_list_item_config_type_0 import ModelVersionListItemConfigType0


T = TypeVar("T", bound="ModelVersionListItem")


@_attrs_define
class ModelVersionListItem:
    """
    Attributes:
        id (int): 模型版本 ID
        name (str): 版本名称
        created_at (Union[None, str]): 创建时间
        updated_at (Union[None, str]): 更新时间
        description (Union[None, Unset, str]): 版本描述
        config (Union['ModelVersionListItemConfigType0', None, Unset]): 版本级默认配置
    """

    id: int
    name: str
    created_at: Union[None, str]
    updated_at: Union[None, str]
    description: Union[None, Unset, str] = UNSET
    config: Union["ModelVersionListItemConfigType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_version_list_item_config_type_0 import ModelVersionListItemConfigType0

        id = self.id

        name = self.name

        created_at: Union[None, str]
        created_at = self.created_at

        updated_at: Union[None, str]
        updated_at = self.updated_at

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, ModelVersionListItemConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_version_list_item_config_type_0 import ModelVersionListItemConfigType0

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        def _parse_created_at(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        created_at = _parse_created_at(d.pop("created_at"))

        def _parse_updated_at(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        updated_at = _parse_updated_at(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_config(data: object) -> Union["ModelVersionListItemConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = ModelVersionListItemConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ModelVersionListItemConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        model_version_list_item = cls(
            id=id,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            config=config,
        )

        model_version_list_item.additional_properties = d
        return model_version_list_item

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
