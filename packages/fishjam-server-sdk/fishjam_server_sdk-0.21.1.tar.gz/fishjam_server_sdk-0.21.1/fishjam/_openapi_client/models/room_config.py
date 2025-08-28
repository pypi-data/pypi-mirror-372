from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.room_config_room_type import RoomConfigRoomType
from ..models.room_config_video_codec import RoomConfigVideoCodec
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoomConfig")


@_attrs_define
class RoomConfig:
    """Room configuration

    Attributes:
        max_peers (Union[None, Unset, int]): Maximum amount of peers allowed into the room Example: 10.
        public (Union[Unset, bool]): True if livestream viewers can omit specifying a token. Default: False.
        room_type (Union[Unset, RoomConfigRoomType]): The use-case of the room. If not provided, this defaults to
            conference. Default: RoomConfigRoomType.CONFERENCE.
        video_codec (Union[Unset, RoomConfigVideoCodec]): Enforces video codec for each peer in the room Default:
            RoomConfigVideoCodec.H264.
        webhook_url (Union[None, Unset, str]): URL where Fishjam notifications will be sent Example:
            https://backend.address.com/fishjam-notifications-endpoint.
    """

    max_peers: Union[None, Unset, int] = UNSET
    public: Union[Unset, bool] = False
    room_type: Union[Unset, RoomConfigRoomType] = RoomConfigRoomType.CONFERENCE
    video_codec: Union[Unset, RoomConfigVideoCodec] = RoomConfigVideoCodec.H264
    webhook_url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_peers: Union[None, Unset, int]
        if isinstance(self.max_peers, Unset):
            max_peers = UNSET
        else:
            max_peers = self.max_peers

        public = self.public

        room_type: Union[Unset, str] = UNSET
        if not isinstance(self.room_type, Unset):
            room_type = self.room_type.value

        video_codec: Union[Unset, str] = UNSET
        if not isinstance(self.video_codec, Unset):
            video_codec = self.video_codec.value

        webhook_url: Union[None, Unset, str]
        if isinstance(self.webhook_url, Unset):
            webhook_url = UNSET
        else:
            webhook_url = self.webhook_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_peers is not UNSET:
            field_dict["maxPeers"] = max_peers
        if public is not UNSET:
            field_dict["public"] = public
        if room_type is not UNSET:
            field_dict["roomType"] = room_type
        if video_codec is not UNSET:
            field_dict["videoCodec"] = video_codec
        if webhook_url is not UNSET:
            field_dict["webhookUrl"] = webhook_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_max_peers(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_peers = _parse_max_peers(d.pop("maxPeers", UNSET))

        public = d.pop("public", UNSET)

        _room_type = d.pop("roomType", UNSET)
        room_type: Union[Unset, RoomConfigRoomType]
        if isinstance(_room_type, Unset):
            room_type = UNSET
        else:
            room_type = RoomConfigRoomType(_room_type)

        _video_codec = d.pop("videoCodec", UNSET)
        video_codec: Union[Unset, RoomConfigVideoCodec]
        if isinstance(_video_codec, Unset):
            video_codec = UNSET
        else:
            video_codec = RoomConfigVideoCodec(_video_codec)

        def _parse_webhook_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        webhook_url = _parse_webhook_url(d.pop("webhookUrl", UNSET))

        room_config = cls(
            max_peers=max_peers,
            public=public,
            room_type=room_type,
            video_codec=video_codec,
            webhook_url=webhook_url,
        )

        room_config.additional_properties = d
        return room_config

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
