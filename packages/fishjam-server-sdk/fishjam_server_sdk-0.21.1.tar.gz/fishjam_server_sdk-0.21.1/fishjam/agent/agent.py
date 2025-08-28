"""
Class for implementing Fishjam agents
"""

import asyncio
import functools
from contextlib import suppress
from types import TracebackType
from typing import Any, Callable, TypeAlias, TypeVar

import betterproto
from websockets import ClientConnection, CloseCode, ConnectionClosed
from websockets.asyncio import client

from fishjam.agent.errors import AgentAuthError
from fishjam.events._protos.fishjam import (
    AgentRequest,
    AgentRequestAuthRequest,
    AgentResponse,
    AgentResponseTrackData,
)

TrackDataHandler: TypeAlias = Callable[[AgentResponseTrackData], None]

TrackDataHandlerT = TypeVar("TrackDataHandlerT", bound=TrackDataHandler)


def _close_ok(e: ConnectionClosed):
    return e.code == CloseCode.NORMAL_CLOSURE


class Agent:
    """
    Allows for connecting to a Fishjam room as an agent peer.
    Provides callbacks for receiving audio.
    """

    def __init__(self, id: str, token: str, fishjam_url: str):
        """
        Create FishjamAgent instance, providing the fishjam id and management token.
        """

        self.id = id
        self._socket_url = f"{fishjam_url}/socket/agent/websocket".replace("http", "ws")
        self._token = token
        self._msg_loop: asyncio.Task[None] | None = None
        self._end_event = asyncio.Event()

        @functools.singledispatch
        def _message_handler(content: Any) -> None:
            raise TypeError(f"Unexpected message of type #{type(content)}")

        @_message_handler.register
        def _(_content: AgentResponseTrackData):
            return

        self._dispatch_handler = _message_handler

    def on_track_data(self, handler: TrackDataHandlerT) -> TrackDataHandlerT:
        """
        Decorator used for defining a handler for track data messages from Fishjam.
        """
        self._dispatch_handler.register(AgentResponseTrackData, handler)
        return handler

    async def connect(self):
        """
        Connect the agent to Fishjam to start receiving messages.

        Incoming messages from Fishjam will be routed to handlers
        defined with :func:`on_track_data`.

        :raises AgentAuthError: authentication failed
        """
        await self.disconnect()

        websocket = await client.connect(self._socket_url)
        await self._authenticate(websocket)

        task = asyncio.create_task(self._recv_loop(websocket))

        self._msg_loop = task

    async def disconnect(self, code: CloseCode = CloseCode.NORMAL_CLOSURE):
        """
        Disconnect the agent from Fishjam.

        Does nothing if already disconnected.
        """
        if (task := self._msg_loop) is None:
            return

        event = self._end_event

        self._end_event = asyncio.Event()
        self._msg_loop = None

        task.add_done_callback(lambda _t: event.set())
        if task.cancel(code):
            await event.wait()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        if exc_type is not None:
            await self.disconnect(CloseCode.INTERNAL_ERROR)
        else:
            await self.disconnect()

    async def _authenticate(self, websocket: ClientConnection):
        req = AgentRequest(auth_request=AgentRequestAuthRequest(token=self._token))
        try:
            await websocket.send(bytes(req))
            # Fishjam will close the socket if auth fails and send a response on success
            await websocket.recv(decode=False)
        except ConnectionClosed as e:
            raise AgentAuthError(e.reason)

    async def _recv_loop(self, websocket: ClientConnection):
        close_code = CloseCode.NORMAL_CLOSURE
        try:
            while True:
                message = await websocket.recv(decode=False)
                message = AgentResponse().parse(message)

                _which, content = betterproto.which_one_of(message, "content")
                self._dispatch_handler(content)
        except ConnectionClosed as e:
            if not _close_ok(e):
                close_code = CloseCode.INTERNAL_ERROR
                raise
        except asyncio.CancelledError as e:
            # NOTE: e.args[0] is the close code supplied by disconnect()
            # However cancellation can have other causes, which we treat as normal
            with suppress(IndexError):
                close_code = e.args[0]
            raise
        except Exception:
            close_code = CloseCode.INTERNAL_ERROR
            raise
        finally:
            await websocket.close(close_code)
