import json
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from auth import verify_token
from game_state import get_room, remove_room, RoomStatus
from game_engine import GameEngine

router = APIRouter()


@router.websocket("/ws/game/{room_id}")
async def game_websocket(websocket: WebSocket, room_id: str, token: str = ""):
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4001, reason="认证失败")
        return

    uid = str(payload["uid"])
    username = payload["sub"]

    room = get_room(room_id)
    if not room:
        await websocket.close(code=4004, reason="房间不存在")
        return

    if uid not in room.players:
        await websocket.close(code=4003, reason="你不在这个房间中")
        return

    await websocket.accept()
    room.connections[uid] = websocket

    try:
        # Send initial room info
        await websocket.send_text(json.dumps({
            "type": "room_info",
            **room.to_dict(),
        }))

        # Notify others
        await _broadcast_to_room(room, {
            "type": "player_join",
            "player_id": uid,
            "username": username,
        }, exclude=uid)

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("type")

            if msg_type == "input":
                # Direction change during game
                direction = msg.get("direction")
                if room.engine and direction:
                    room.engine.set_direction(uid, direction)

            elif msg_type == "settings":
                # Update player settings (emoji, color)
                player = room.players.get(uid)
                if player and room.status == RoomStatus.WAITING:
                    if "emoji" in msg:
                        emoji = msg["emoji"]
                        if len(emoji) <= 2:
                            player.emoji = emoji
                    if "color" in msg:
                        color = msg["color"]
                        if isinstance(color, str) and len(color) <= 10:
                            player.color = color
                    # Broadcast updated player info
                    await _broadcast_to_room(room, {
                        "type": "room_info",
                        **room.to_dict(),
                    })

            elif msg_type == "start_game":
                # Only host can start
                if uid == room.host_id and room.status == RoomStatus.WAITING:
                    room.status = RoomStatus.PLAYING
                    engine = GameEngine(room)
                    room.engine = engine

                    await _broadcast_to_room(room, {
                        "type": "game_start",
                        "map_width": 60,
                        "map_height": 40,
                    })

                    engine.start()

            elif msg_type == "chat":
                # Simple pass-through (optional)
                pass

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        # Cleanup
        room.connections.pop(uid, None)

        if room.engine:
            room.engine.remove_player(uid)

        if uid in room.players:
            del room.players[uid]

        if len(room.players) == 0:
            if room.engine:
                await room.engine.stop()
            remove_room(room_id)
        else:
            if room.host_id == uid:
                room.host_id = next(iter(room.players))

            await _broadcast_to_room(room, {
                "type": "player_leave",
                "player_id": uid,
                "username": username,
            })
            await _broadcast_to_room(room, {
                "type": "room_info",
                **room.to_dict(),
            })


async def _broadcast_to_room(room, data: dict, exclude: str | None = None):
    msg = json.dumps(data)
    disconnected = []
    for uid, ws in list(room.connections.items()):
        if uid == exclude:
            continue
        try:
            await ws.send_text(msg)
        except Exception:
            disconnected.append(uid)
    for uid in disconnected:
        room.connections.pop(uid, None)
