import asyncio
import json

import websockets

ROOMS = {}  # Store rooms with their participants


async def signaling_handler(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            room_id = data.get("room")
            if not room_id:
                await websocket.send(json.dumps({"error": "Room ID is required"}))
                continue

            # Initialize room
            room = ROOMS.setdefault(room_id, {"caller": None, "answerer": None})

            if data["type"] == "offer":
                if room["caller"] is None:
                    room["caller"] = websocket
                    print(f"Caller joined room {room_id}")
                else:
                    await websocket.send(
                        json.dumps({"error": "Room already has a caller"})
                    )
                    continue

                # Forward offer to answerer if present
                if room["answerer"]:
                    await room["answerer"].send(json.dumps(data))

            elif data["type"] == "answer":
                if room["answerer"] is None:
                    room["answerer"] = websocket
                    print(f"Answerer joined room {room_id}")
                else:
                    await websocket.send(
                        json.dumps({"error": "Room already has an answerer"})
                    )
                    continue

                # Forward answer to caller
                if room["caller"]:
                    await room["caller"].send(json.dumps(data))

            elif data["type"] == "ice":
                # Relay ICE candidates to the other peer
                target = (
                    room["caller"]
                    if websocket == room["answerer"]
                    else room["answerer"]
                )
                if target:
                    await target.send(json.dumps(data))

    except websockets.ConnectionClosed:
        print(f"Connection closed: {websocket.remote_address}")
        await cleanup_room(websocket)

    except Exception as e:
        print(f"Error: {e}")


async def cleanup_room(websocket):
    """Clean up the room when a participant disconnects."""
    for room_id, participants in list(ROOMS.items()):
        if websocket in participants.values():
            # Notify the other participant, if connected
            other_peer = (
                participants["answerer"]
                if participants["caller"] == websocket
                else participants["caller"]
            )
            if other_peer:
                try:
                    await other_peer.send(json.dumps({"type": "peer-disconnected"}))
                except Exception as e:
                    print(f"Failed to notify peer: {e}")

            # Remove the disconnected peer and clean up the room
            ROOMS.pop(room_id, None)
            print(f"Room {room_id} cleaned up")
            break


# Start WebSocket server
start_server = websockets.serve(signaling_handler, "0.0.0.0", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
