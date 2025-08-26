from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define

from ..models.peer_options_web_rtc_subscribe_options_audio_format import (
    PeerOptionsWebRTCSubscribeOptionsAudioFormat,
)
from ..models.peer_options_web_rtc_subscribe_options_audio_sample_rate import (
    PeerOptionsWebRTCSubscribeOptionsAudioSampleRate,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PeerOptionsWebRTCSubscribeOptions")


@_attrs_define
class PeerOptionsWebRTCSubscribeOptions:
    """Configuration of server-side subscriptions to the peer's tracks

    Example:
        {'audioFormat': 'pcm16'}

    Attributes:
        audio_format (Union[Unset, PeerOptionsWebRTCSubscribeOptionsAudioFormat]): The format of the output audio
            Default: PeerOptionsWebRTCSubscribeOptionsAudioFormat.PCM16. Example: pcm16.
        audio_sample_rate (Union[Unset, PeerOptionsWebRTCSubscribeOptionsAudioSampleRate]): The sample rate of the
            output audio Default: PeerOptionsWebRTCSubscribeOptionsAudioSampleRate.VALUE_16000. Example: 16000.
    """

    audio_format: Union[
        Unset, PeerOptionsWebRTCSubscribeOptionsAudioFormat
    ] = PeerOptionsWebRTCSubscribeOptionsAudioFormat.PCM16
    audio_sample_rate: Union[
        Unset, PeerOptionsWebRTCSubscribeOptionsAudioSampleRate
    ] = PeerOptionsWebRTCSubscribeOptionsAudioSampleRate.VALUE_16000

    def to_dict(self) -> dict[str, Any]:
        audio_format: Union[Unset, str] = UNSET
        if not isinstance(self.audio_format, Unset):
            audio_format = self.audio_format.value

        audio_sample_rate: Union[Unset, int] = UNSET
        if not isinstance(self.audio_sample_rate, Unset):
            audio_sample_rate = self.audio_sample_rate.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if audio_format is not UNSET:
            field_dict["audioFormat"] = audio_format
        if audio_sample_rate is not UNSET:
            field_dict["audioSampleRate"] = audio_sample_rate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _audio_format = d.pop("audioFormat", UNSET)
        audio_format: Union[Unset, PeerOptionsWebRTCSubscribeOptionsAudioFormat]
        if isinstance(_audio_format, Unset):
            audio_format = UNSET
        else:
            audio_format = PeerOptionsWebRTCSubscribeOptionsAudioFormat(_audio_format)

        _audio_sample_rate = d.pop("audioSampleRate", UNSET)
        audio_sample_rate: Union[
            Unset, PeerOptionsWebRTCSubscribeOptionsAudioSampleRate
        ]
        if isinstance(_audio_sample_rate, Unset):
            audio_sample_rate = UNSET
        else:
            audio_sample_rate = PeerOptionsWebRTCSubscribeOptionsAudioSampleRate(
                _audio_sample_rate
            )

        peer_options_web_rtc_subscribe_options = cls(
            audio_format=audio_format,
            audio_sample_rate=audio_sample_rate,
        )

        return peer_options_web_rtc_subscribe_options
