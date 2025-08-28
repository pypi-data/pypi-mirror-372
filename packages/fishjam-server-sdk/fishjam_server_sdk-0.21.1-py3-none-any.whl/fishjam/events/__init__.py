"""
.. include:: ../../docs/server_notifications.md
"""

# Exported messages
from fishjam.events._protos.fishjam import (
    ServerMessagePeerAdded,
    ServerMessagePeerConnected,
    ServerMessagePeerCrashed,
    ServerMessagePeerDeleted,
    ServerMessagePeerDisconnected,
    ServerMessagePeerMetadataUpdated,
    ServerMessageRoomCrashed,
    ServerMessageRoomCreated,
    ServerMessageRoomDeleted,
    ServerMessageStreamConnected,
    ServerMessageStreamDisconnected,
    ServerMessageTrackAdded,
    ServerMessageTrackMetadataUpdated,
    ServerMessageTrackRemoved,
    ServerMessageViewerConnected,
    ServerMessageViewerDisconnected,
)
from fishjam.events._protos.fishjam.notifications import Track, TrackEncoding, TrackType

__all__ = [
    "ServerMessageRoomCreated",
    "ServerMessageRoomDeleted",
    "ServerMessageRoomCrashed",
    "ServerMessagePeerAdded",
    "ServerMessagePeerConnected",
    "ServerMessagePeerDeleted",
    "ServerMessagePeerDisconnected",
    "ServerMessagePeerMetadataUpdated",
    "ServerMessagePeerCrashed",
    "ServerMessageStreamConnected",
    "ServerMessageStreamDisconnected",
    "ServerMessageTrackAdded",
    "ServerMessageTrackMetadataUpdated",
    "ServerMessageTrackRemoved",
    "ServerMessageViewerConnected",
    "ServerMessageViewerDisconnected",
    "Track",
    "TrackEncoding",
    "TrackType",
]
