from enum import Enum


class RoomConfigRoomType(str, Enum):
    """The use-case of the room. If not provided, this defaults to conference."""

    AUDIO_ONLY = "audio_only"
    BROADCASTER = "broadcaster"
    CONFERENCE = "conference"
    FULL_FEATURE = "full_feature"
    LIVESTREAM = "livestream"

    def __str__(self) -> str:
        return str(self.value)
