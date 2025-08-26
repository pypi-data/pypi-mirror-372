from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.peer_type import PeerType

if TYPE_CHECKING:
    from ..models.peer_options_agent import PeerOptionsAgent
    from ..models.peer_options_web_rtc import PeerOptionsWebRTC


T = TypeVar("T", bound="AddPeerBody")


@_attrs_define
class AddPeerBody:
    """
    Attributes:
        options (Union['PeerOptionsAgent', 'PeerOptionsWebRTC']): Peer-specific options
        type_ (PeerType): Peer type Example: webrtc.
    """

    options: Union["PeerOptionsAgent", "PeerOptionsWebRTC"]
    type_: PeerType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.peer_options_web_rtc import PeerOptionsWebRTC

        options: dict[str, Any]
        if isinstance(self.options, PeerOptionsWebRTC):
            options = self.options.to_dict()
        else:
            options = self.options.to_dict()

        type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "options": options,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.peer_options_agent import PeerOptionsAgent
        from ..models.peer_options_web_rtc import PeerOptionsWebRTC

        d = dict(src_dict)

        def _parse_options(
            data: object,
        ) -> Union["PeerOptionsAgent", "PeerOptionsWebRTC"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_peer_options_type_0 = PeerOptionsWebRTC.from_dict(
                    data
                )

                return componentsschemas_peer_options_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_peer_options_type_1 = PeerOptionsAgent.from_dict(data)

            return componentsschemas_peer_options_type_1

        options = _parse_options(d.pop("options"))

        type_ = PeerType(d.pop("type"))

        add_peer_body = cls(
            options=options,
            type_=type_,
        )

        add_peer_body.additional_properties = d
        return add_peer_body

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
