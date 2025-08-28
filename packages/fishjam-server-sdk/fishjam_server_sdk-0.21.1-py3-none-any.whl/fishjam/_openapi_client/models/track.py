from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.track_type import TrackType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.track_metadata_type_0 import TrackMetadataType0


T = TypeVar("T", bound="Track")


@_attrs_define
class Track:
    """Describes media track of a Peer or Component

    Attributes:
        id (Union[Unset, str]):
        metadata (Union['TrackMetadataType0', None, Unset]):  Example: {'source': 'camera'}.
        type_ (Union[Unset, TrackType]):
    """

    id: Union[Unset, str] = UNSET
    metadata: Union["TrackMetadataType0", None, Unset] = UNSET
    type_: Union[Unset, TrackType] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.track_metadata_type_0 import TrackMetadataType0

        id = self.id

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, TrackMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.track_metadata_type_0 import TrackMetadataType0

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        def _parse_metadata(data: object) -> Union["TrackMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = TrackMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TrackMetadataType0", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, TrackType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = TrackType(_type_)

        track = cls(
            id=id,
            metadata=metadata,
            type_=type_,
        )

        track.additional_properties = d
        return track

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
