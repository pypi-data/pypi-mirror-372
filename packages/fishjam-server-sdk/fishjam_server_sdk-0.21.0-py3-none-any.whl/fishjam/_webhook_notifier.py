"""
Module defining a function allowing decoding received webhook 
notification from fishjam to notification structs.
"""

from typing import Union

import betterproto

from fishjam.events._protos.fishjam import ServerMessage
from fishjam.events.allowed_notifications import (
    ALLOWED_NOTIFICATIONS,
    AllowedNotification,
)


def receive_binary(binary: bytes) -> Union[AllowedNotification, None]:
    """
    Transform received protobuf notification to adequate notification instance.
    The available notifications are listed in `fishjam.events` module.
    """
    message = ServerMessage().parse(binary)
    _which, message = betterproto.which_one_of(message, "content")

    if isinstance(message, ALLOWED_NOTIFICATIONS):
        return message

    return None
