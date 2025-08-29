from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_set_list_resp import DataSetListResp
    from ..models.pagination_schema import PaginationSchema


T = TypeVar("T", bound="PaginatedResponseDataSetListResp")


@_attrs_define
class PaginatedResponseDataSetListResp:
    """
    Attributes:
        code (Union[Unset, int]):  Default: 200.
        message (Union[Unset, str]):  Default: 'success'.
        data (Union['DataSetListResp', None, Unset]):
        request_id (Union[None, Unset, str]):
        pagination (Union['PaginationSchema', None, Unset]):
    """

    code: Union[Unset, int] = 200
    message: Union[Unset, str] = "success"
    data: Union["DataSetListResp", None, Unset] = UNSET
    request_id: Union[None, Unset, str] = UNSET
    pagination: Union["PaginationSchema", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_set_list_resp import DataSetListResp
        from ..models.pagination_schema import PaginationSchema

        code = self.code

        message = self.message

        data: Union[None, Unset, dict[str, Any]]
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, DataSetListResp):
            data = self.data.to_dict()
        else:
            data = self.data

        request_id: Union[None, Unset, str]
        if isinstance(self.request_id, Unset):
            request_id = UNSET
        else:
            request_id = self.request_id

        pagination: Union[None, Unset, dict[str, Any]]
        if isinstance(self.pagination, Unset):
            pagination = UNSET
        elif isinstance(self.pagination, PaginationSchema):
            pagination = self.pagination.to_dict()
        else:
            pagination = self.pagination

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if message is not UNSET:
            field_dict["message"] = message
        if data is not UNSET:
            field_dict["data"] = data
        if request_id is not UNSET:
            field_dict["request_id"] = request_id
        if pagination is not UNSET:
            field_dict["pagination"] = pagination

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_set_list_resp import DataSetListResp
        from ..models.pagination_schema import PaginationSchema

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        message = d.pop("message", UNSET)

        def _parse_data(data: object) -> Union["DataSetListResp", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = DataSetListResp.from_dict(data)

                return data_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DataSetListResp", None, Unset], data)

        data = _parse_data(d.pop("data", UNSET))

        def _parse_request_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        request_id = _parse_request_id(d.pop("request_id", UNSET))

        def _parse_pagination(data: object) -> Union["PaginationSchema", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pagination_type_0 = PaginationSchema.from_dict(data)

                return pagination_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PaginationSchema", None, Unset], data)

        pagination = _parse_pagination(d.pop("pagination", UNSET))

        paginated_response_data_set_list_resp = cls(
            code=code,
            message=message,
            data=data,
            request_id=request_id,
            pagination=pagination,
        )

        paginated_response_data_set_list_resp.additional_properties = d
        return paginated_response_data_set_list_resp

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
