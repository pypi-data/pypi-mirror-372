from enum import IntEnum


class SubscribeOptionsAudioSampleRate(IntEnum):
    VALUE_16000 = 16000
    VALUE_24000 = 24000

    def __str__(self) -> str:
        return str(self.value)
