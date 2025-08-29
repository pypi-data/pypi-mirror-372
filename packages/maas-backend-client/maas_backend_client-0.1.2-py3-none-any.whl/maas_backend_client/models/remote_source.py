from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RemoteSource")


@_attrs_define
class RemoteSource:
    """
    Attributes:
        remote_source (str): 模型来源：`huggingface` / `modelscope`
        repo (str): 仓库路径，如 `Qwen/Qwen-7B`
        revision (Union[None, Unset, str]): 分支或 tag，默认 `main` / `master` Default: 'main'.
        sub_path (Union[None, Unset, str]): 子目录
    """

    remote_source: str
    repo: str
    revision: Union[None, Unset, str] = "main"
    sub_path: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        remote_source = self.remote_source

        repo = self.repo

        revision: Union[None, Unset, str]
        if isinstance(self.revision, Unset):
            revision = UNSET
        else:
            revision = self.revision

        sub_path: Union[None, Unset, str]
        if isinstance(self.sub_path, Unset):
            sub_path = UNSET
        else:
            sub_path = self.sub_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "remote_source": remote_source,
                "repo": repo,
            }
        )
        if revision is not UNSET:
            field_dict["revision"] = revision
        if sub_path is not UNSET:
            field_dict["sub_path"] = sub_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        remote_source = d.pop("remote_source")

        repo = d.pop("repo")

        def _parse_revision(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        revision = _parse_revision(d.pop("revision", UNSET))

        def _parse_sub_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sub_path = _parse_sub_path(d.pop("sub_path", UNSET))

        remote_source = cls(
            remote_source=remote_source,
            repo=repo,
            revision=revision,
            sub_path=sub_path,
        )

        remote_source.additional_properties = d
        return remote_source

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
