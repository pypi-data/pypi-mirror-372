from enum import Enum


class PeerType(str, Enum):
    """Peer type"""

    AGENT = "agent"
    WEBRTC = "webrtc"

    def __str__(self) -> str:
        return str(self.value)
