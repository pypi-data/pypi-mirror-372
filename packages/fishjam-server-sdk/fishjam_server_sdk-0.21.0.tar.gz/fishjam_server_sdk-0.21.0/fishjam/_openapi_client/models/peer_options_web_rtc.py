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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.peer_options_web_rtc_metadata import PeerOptionsWebRTCMetadata
    from ..models.peer_options_web_rtc_subscribe_options import (
        PeerOptionsWebRTCSubscribeOptions,
    )


T = TypeVar("T", bound="PeerOptionsWebRTC")


@_attrs_define
class PeerOptionsWebRTC:
    """Options specific to the WebRTC peer

    Attributes:
        enable_simulcast (Union[Unset, bool]): Enables the peer to use simulcast Default: True.
        metadata (Union[Unset, PeerOptionsWebRTCMetadata]): Custom peer metadata
        subscribe (Union['PeerOptionsWebRTCSubscribeOptions', None, Unset]): Configuration of server-side subscriptions
            to the peer's tracks Example: {'audioFormat': 'pcm16'}.
    """

    enable_simulcast: Union[Unset, bool] = True
    metadata: Union[Unset, "PeerOptionsWebRTCMetadata"] = UNSET
    subscribe: Union["PeerOptionsWebRTCSubscribeOptions", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.peer_options_web_rtc_subscribe_options import (
            PeerOptionsWebRTCSubscribeOptions,
        )

        enable_simulcast = self.enable_simulcast

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        subscribe: Union[None, Unset, dict[str, Any]]
        if isinstance(self.subscribe, Unset):
            subscribe = UNSET
        elif isinstance(self.subscribe, PeerOptionsWebRTCSubscribeOptions):
            subscribe = self.subscribe.to_dict()
        else:
            subscribe = self.subscribe

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable_simulcast is not UNSET:
            field_dict["enableSimulcast"] = enable_simulcast
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if subscribe is not UNSET:
            field_dict["subscribe"] = subscribe

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.peer_options_web_rtc_metadata import PeerOptionsWebRTCMetadata
        from ..models.peer_options_web_rtc_subscribe_options import (
            PeerOptionsWebRTCSubscribeOptions,
        )

        d = dict(src_dict)
        enable_simulcast = d.pop("enableSimulcast", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, PeerOptionsWebRTCMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PeerOptionsWebRTCMetadata.from_dict(_metadata)

        def _parse_subscribe(
            data: object,
        ) -> Union["PeerOptionsWebRTCSubscribeOptions", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                subscribe_type_0 = PeerOptionsWebRTCSubscribeOptions.from_dict(data)

                return subscribe_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PeerOptionsWebRTCSubscribeOptions", None, Unset], data)

        subscribe = _parse_subscribe(d.pop("subscribe", UNSET))

        peer_options_web_rtc = cls(
            enable_simulcast=enable_simulcast,
            metadata=metadata,
            subscribe=subscribe,
        )

        peer_options_web_rtc.additional_properties = d
        return peer_options_web_rtc

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
