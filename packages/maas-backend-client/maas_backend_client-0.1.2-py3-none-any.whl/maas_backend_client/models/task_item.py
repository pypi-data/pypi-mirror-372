from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.task_item_default_config_type_0 import TaskItemDefaultConfigType0
    from ..models.task_item_input_schema_type_0 import TaskItemInputSchemaType0
    from ..models.task_item_output_schema_type_0 import TaskItemOutputSchemaType0


T = TypeVar("T", bound="TaskItem")


@_attrs_define
class TaskItem:
    """
    Attributes:
        type_ (str): 任务类型，如 `chat`, `embedding`, `object-detection`
        description (Union[None, Unset, str]): 任务描述，用于前端展示
        input_schema (Union['TaskItemInputSchemaType0', None, Unset]): 输入参数的结构定义
        output_schema (Union['TaskItemOutputSchemaType0', None, Unset]): 输出参数的结构定义
        default_config (Union['TaskItemDefaultConfigType0', None, Unset]): 本任务的默认运行参数（覆盖版本级 config）
    """

    type_: str
    description: Union[None, Unset, str] = UNSET
    input_schema: Union["TaskItemInputSchemaType0", None, Unset] = UNSET
    output_schema: Union["TaskItemOutputSchemaType0", None, Unset] = UNSET
    default_config: Union["TaskItemDefaultConfigType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.task_item_default_config_type_0 import TaskItemDefaultConfigType0
        from ..models.task_item_input_schema_type_0 import TaskItemInputSchemaType0
        from ..models.task_item_output_schema_type_0 import TaskItemOutputSchemaType0

        type_ = self.type_

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        input_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.input_schema, Unset):
            input_schema = UNSET
        elif isinstance(self.input_schema, TaskItemInputSchemaType0):
            input_schema = self.input_schema.to_dict()
        else:
            input_schema = self.input_schema

        output_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.output_schema, Unset):
            output_schema = UNSET
        elif isinstance(self.output_schema, TaskItemOutputSchemaType0):
            output_schema = self.output_schema.to_dict()
        else:
            output_schema = self.output_schema

        default_config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.default_config, Unset):
            default_config = UNSET
        elif isinstance(self.default_config, TaskItemDefaultConfigType0):
            default_config = self.default_config.to_dict()
        else:
            default_config = self.default_config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if input_schema is not UNSET:
            field_dict["input_schema"] = input_schema
        if output_schema is not UNSET:
            field_dict["output_schema"] = output_schema
        if default_config is not UNSET:
            field_dict["default_config"] = default_config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_item_default_config_type_0 import TaskItemDefaultConfigType0
        from ..models.task_item_input_schema_type_0 import TaskItemInputSchemaType0
        from ..models.task_item_output_schema_type_0 import TaskItemOutputSchemaType0

        d = dict(src_dict)
        type_ = d.pop("type")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_input_schema(data: object) -> Union["TaskItemInputSchemaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_schema_type_0 = TaskItemInputSchemaType0.from_dict(data)

                return input_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TaskItemInputSchemaType0", None, Unset], data)

        input_schema = _parse_input_schema(d.pop("input_schema", UNSET))

        def _parse_output_schema(data: object) -> Union["TaskItemOutputSchemaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                output_schema_type_0 = TaskItemOutputSchemaType0.from_dict(data)

                return output_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TaskItemOutputSchemaType0", None, Unset], data)

        output_schema = _parse_output_schema(d.pop("output_schema", UNSET))

        def _parse_default_config(data: object) -> Union["TaskItemDefaultConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                default_config_type_0 = TaskItemDefaultConfigType0.from_dict(data)

                return default_config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TaskItemDefaultConfigType0", None, Unset], data)

        default_config = _parse_default_config(d.pop("default_config", UNSET))

        task_item = cls(
            type_=type_,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            default_config=default_config,
        )

        task_item.additional_properties = d
        return task_item

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
