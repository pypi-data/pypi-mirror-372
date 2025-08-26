from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.peer import Peer
    from ..models.room_config import RoomConfig


T = TypeVar("T", bound="Room")


@_attrs_define
class Room:
    """Description of the room state

    Attributes:
        config (RoomConfig): Room configuration
        id (str): Room ID Example: room-1.
        peers (list['Peer']): List of all peers
    """

    config: "RoomConfig"
    id: str
    peers: list["Peer"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config = self.config.to_dict()

        id = self.id

        peers = []
        for peers_item_data in self.peers:
            peers_item = peers_item_data.to_dict()
            peers.append(peers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "id": id,
                "peers": peers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.peer import Peer
        from ..models.room_config import RoomConfig

        d = dict(src_dict)
        config = RoomConfig.from_dict(d.pop("config"))

        id = d.pop("id")

        peers = []
        _peers = d.pop("peers")
        for peers_item_data in _peers:
            peers_item = Peer.from_dict(peers_item_data)

            peers.append(peers_item)

        room = cls(
            config=config,
            id=id,
            peers=peers,
        )

        room.additional_properties = d
        return room

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
