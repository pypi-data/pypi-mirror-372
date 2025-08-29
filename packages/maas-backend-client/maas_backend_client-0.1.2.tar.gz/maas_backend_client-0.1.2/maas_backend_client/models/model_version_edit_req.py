from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_version_edit_req_config_type_0 import ModelVersionEditReqConfigType0
    from ..models.remote_source import RemoteSource
    from ..models.task_item import TaskItem


T = TypeVar("T", bound="ModelVersionEditReq")


@_attrs_define
class ModelVersionEditReq:
    """
    Attributes:
        name (Union[None, Unset, str]): 模型版本名称
        description (Union[None, Unset, str]): 模型版本描述
        model_file_id (Union[None, Unset, int]): 本地上传的模型文件 id
        remote (Union['RemoteSource', None, Unset]): 远程上传的模型
        config (Union['ModelVersionEditReqConfigType0', None, Unset]): 版本整体默认运行配置
        tasks (Union[None, Unset, list['TaskItem']]): 更新后的任务定义列表
        related_dataset_version_ids (Union[None, Unset, list[int]]): 关联的数据集版本 ID
    """

    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    model_file_id: Union[None, Unset, int] = UNSET
    remote: Union["RemoteSource", None, Unset] = UNSET
    config: Union["ModelVersionEditReqConfigType0", None, Unset] = UNSET
    tasks: Union[None, Unset, list["TaskItem"]] = UNSET
    related_dataset_version_ids: Union[None, Unset, list[int]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_version_edit_req_config_type_0 import ModelVersionEditReqConfigType0
        from ..models.remote_source import RemoteSource

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

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
        elif isinstance(self.config, ModelVersionEditReqConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        tasks: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.tasks, Unset):
            tasks = UNSET
        elif isinstance(self.tasks, list):
            tasks = []
            for tasks_type_0_item_data in self.tasks:
                tasks_type_0_item = tasks_type_0_item_data.to_dict()
                tasks.append(tasks_type_0_item)

        else:
            tasks = self.tasks

        related_dataset_version_ids: Union[None, Unset, list[int]]
        if isinstance(self.related_dataset_version_ids, Unset):
            related_dataset_version_ids = UNSET
        elif isinstance(self.related_dataset_version_ids, list):
            related_dataset_version_ids = self.related_dataset_version_ids

        else:
            related_dataset_version_ids = self.related_dataset_version_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if model_file_id is not UNSET:
            field_dict["model_file_id"] = model_file_id
        if remote is not UNSET:
            field_dict["remote"] = remote
        if config is not UNSET:
            field_dict["config"] = config
        if tasks is not UNSET:
            field_dict["tasks"] = tasks
        if related_dataset_version_ids is not UNSET:
            field_dict["related_dataset_version_ids"] = related_dataset_version_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_version_edit_req_config_type_0 import ModelVersionEditReqConfigType0
        from ..models.remote_source import RemoteSource
        from ..models.task_item import TaskItem

        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

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

        def _parse_config(data: object) -> Union["ModelVersionEditReqConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = ModelVersionEditReqConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ModelVersionEditReqConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        def _parse_tasks(data: object) -> Union[None, Unset, list["TaskItem"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tasks_type_0 = []
                _tasks_type_0 = data
                for tasks_type_0_item_data in _tasks_type_0:
                    tasks_type_0_item = TaskItem.from_dict(tasks_type_0_item_data)

                    tasks_type_0.append(tasks_type_0_item)

                return tasks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TaskItem"]], data)

        tasks = _parse_tasks(d.pop("tasks", UNSET))

        def _parse_related_dataset_version_ids(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                related_dataset_version_ids_type_0 = cast(list[int], data)

                return related_dataset_version_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        related_dataset_version_ids = _parse_related_dataset_version_ids(d.pop("related_dataset_version_ids", UNSET))

        model_version_edit_req = cls(
            name=name,
            description=description,
            model_file_id=model_file_id,
            remote=remote,
            config=config,
            tasks=tasks,
            related_dataset_version_ids=related_dataset_version_ids,
        )

        model_version_edit_req.additional_properties = d
        return model_version_edit_req

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
