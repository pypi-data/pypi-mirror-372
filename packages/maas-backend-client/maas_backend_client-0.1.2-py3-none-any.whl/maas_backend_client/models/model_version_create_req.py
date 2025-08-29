from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_version_create_req_config_type_0 import ModelVersionCreateReqConfigType0
    from ..models.remote_source import RemoteSource
    from ..models.task_item import TaskItem


T = TypeVar("T", bound="ModelVersionCreateReq")


@_attrs_define
class ModelVersionCreateReq:
    """
    Attributes:
        model_id (int): 模型 ID
        name (str): 模型版本名称，如 `v1.0`、`qwen-7b`
        tasks (list['TaskItem']): 本模型版本支持的任务定义列表
        description (Union[None, Unset, str]): 模型版本描述
        model_file_id (Union[None, Unset, int]): 本地上传的模型文件 id（zip）
        remote (Union['RemoteSource', None, Unset]): 远程上传的模型
        config (Union['ModelVersionCreateReqConfigType0', None, Unset]): 版本整体默认运行配置
    """

    model_id: int
    name: str
    tasks: list["TaskItem"]
    description: Union[None, Unset, str] = UNSET
    model_file_id: Union[None, Unset, int] = UNSET
    remote: Union["RemoteSource", None, Unset] = UNSET
    config: Union["ModelVersionCreateReqConfigType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_version_create_req_config_type_0 import ModelVersionCreateReqConfigType0
        from ..models.remote_source import RemoteSource

        model_id = self.model_id

        name = self.name

        tasks = []
        for tasks_item_data in self.tasks:
            tasks_item = tasks_item_data.to_dict()
            tasks.append(tasks_item)

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        model_file_id: Union[None, Unset, int]
        if isinstance(self.model_file_id, Unset):
            model_file_id = UNSET
        else:
            model_file_id = self.model_file_id

        remote: Union[None, Unset, dict[str, Any]]
        if isinstance(self.remote, Unset):
            remote = UNSET
        elif isinstance(self.remote, RemoteSource):
            remote = self.remote.to_dict()
        else:
            remote = self.remote

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, ModelVersionCreateReqConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_id": model_id,
                "name": name,
                "tasks": tasks,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if model_file_id is not UNSET:
            field_dict["model_file_id"] = model_file_id
        if remote is not UNSET:
            field_dict["remote"] = remote
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_version_create_req_config_type_0 import ModelVersionCreateReqConfigType0
        from ..models.remote_source import RemoteSource
        from ..models.task_item import TaskItem

        d = dict(src_dict)
        model_id = d.pop("model_id")

        name = d.pop("name")

        tasks = []
        _tasks = d.pop("tasks")
        for tasks_item_data in _tasks:
            tasks_item = TaskItem.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_model_file_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        model_file_id = _parse_model_file_id(d.pop("model_file_id", UNSET))

        def _parse_remote(data: object) -> Union["RemoteSource", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                remote_type_0 = RemoteSource.from_dict(data)

                return remote_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RemoteSource", None, Unset], data)

        remote = _parse_remote(d.pop("remote", UNSET))

        def _parse_config(data: object) -> Union["ModelVersionCreateReqConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = ModelVersionCreateReqConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ModelVersionCreateReqConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        model_version_create_req = cls(
            model_id=model_id,
            name=name,
            tasks=tasks,
            description=description,
            model_file_id=model_file_id,
            remote=remote,
            config=config,
        )

        model_version_create_req.additional_properties = d
        return model_version_create_req

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
