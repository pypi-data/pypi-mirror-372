<img src="./images/fishjam-card.png" width="100%">

# Fishjam Python Server SDK

Python server SDK for the [Fishjam](https://fishjam.io/).

Read the docs [here](https://fishjam-cloud.github.io/python-server-sdk)

## Installation

```
pip install fishjam-server-sdk
```

## Usage

The SDK exports two main classes for interacting with Fishjam server:
`FishjamClient` and `FishjamNotifier`.

`FishjamClient` wraps http REST api calls, while `FishjamNotifier` is responsible for receiving real-time updates from the server.

### FishjamClient

Create a `FishjamClient` instance, providing the fishjam server address and api token

```python
from fishjam import FishjamClient

fishjam_client = FishjamClient(fishjam_url="localhost:5002", management_token="development")
```

You can use it to interact with Fishjam to manage rooms and peers

```python
# Create a room
options = RoomOptions(video_codec="h264", webhook_url="http://localhost:5000/webhook")
room = fishjam_client.create_room(options=options)

# Room(components=[], config=RoomConfig(max_peers=None, video_codec=<RoomConfigVideoCodec.H264: 'h264'>, webhook_url='http://localhost:5000/webhook'), id='1d905478-ccfc-44d6-a6e7-8ccb1b38d955', peers=[])

# Add peer to the room
peer, token = fishjam_client.create_peer(room.id)

# Peer(id='b1232c7e-c969-4450-acdf-ea24f3cdd7f6', status=<PeerStatus.DISCONNECTED: 'disconnected'>, type='webrtc'), 'M8TUGhj-L11KpyG-2zBPIo'
```

All methods in `FishjamClient` may raise one of the exceptions deriving from `fishjam.errors.HTTPError`. They are defined in `fishjam.errors`.

### FishjamNotifier

FishjamNotifier allows for receiving real-time updates from the Fishjam Server.

You can read more about notifications in the
[Fishjam Docs](https://fishjam-cloud.github.io/fishjam-docs/next/getting_started/notifications).

Create `FishjamNotifier` instance

```python
from fishjam import FishjamNotifier

fishjam_notifier = FishjamNotifier(fishjam_url='localhost:5002', management_token='development')
```

Then define a handler for incoming messages

```python
@notifier.on_server_notification
def handle_notification(server_notification):
    print(f'Received a notification: {server_notification}')
```

After that you can start the notifier

```python
async def test_notifier():
    notifier_task = asyncio.create_task(fishjam_notifier.connect())

    # Wait for notifier to be ready to receive messages
    await fishjam_notifier.wait_ready()

    # Create a room to trigger a server notification
    fishjam_client = FishjamClient()
    fishjam_client.create_room()

    await notifier_task

asyncio.run(test_notifier())

# Received a notification: ServerMessageRoomCreated(room_id='69a3fd1a-6a4d-47bc-ae54-0c72b0d05e29')
```

## License

Licensed under the [Apache License, Version 2.0](LICENSE)

## Fishjam is created by Software Mansion

Since 2012 [Software Mansion](https://swmansion.com) is a software agency with experience in building web and mobile
apps. We are Core React Native Contributors and experts in dealing with all kinds of React Native issues. We can help
you build your next dream product –
[Hire us](https://swmansion.com/contact/projects?utm_source=fishjam&utm_medium=python-readme).

[![Software Mansion](https://logo.swmansion.com/logo?color=white&variant=desktop&width=200&tag=react-client)](https://swmansion.com/contact/projects?utm_source=fishjam&utm_medium=python-readme)
