import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, field_validator

from auth import verify_token
from game_state import rooms, create_room, get_room, remove_room, PlayerInfo, RoomStatus

router = APIRouter(prefix="/api", tags=["rooms"])


def get_current_user(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证头")
    token = authorization[7:]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token无效或已过期")
    return payload


class CreateRoomRequest(BaseModel):
    room_name: str = "新房间"

    @field_validator("room_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1 or len(v) > 30:
            raise ValueError("房间名长度需要1-30个字符")
        return v


@router.get("/rooms")
async def list_rooms():
    return {
        "rooms": [room.to_dict() for room in rooms.values()]
    }


@router.post("/rooms")
async def create_room_api(req: CreateRoomRequest, user: dict = Depends(get_current_user)):
    # Check if user is already in a room
    uid = str(user["uid"])
    for room in rooms.values():
        if uid in room.players:
            raise HTTPException(status_code=400, detail="你已经在一个房间中了")

    room_id = uuid.uuid4().hex[:8]
    room = create_room(room_id, req.room_name, uid, user["sub"])
    return room.to_dict()


@router.post("/rooms/{room_id}/join")
async def join_room(room_id: str, user: dict = Depends(get_current_user)):
    uid = str(user["uid"])

    # Check if user is already in another room
    for r in rooms.values():
        if uid in r.players and r.room_id != room_id:
            raise HTTPException(status_code=400, detail="你已经在另一个房间中了")

    room = get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    if room.status == RoomStatus.PLAYING:
        raise HTTPException(status_code=400, detail="游戏已经开始了")
    if len(room.players) >= 10:
        raise HTTPException(status_code=400, detail="房间已满")
    if uid not in room.players:
        room.players[uid] = PlayerInfo(user_id=uid, username=user["sub"])
    return room.to_dict()


@router.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, user: dict = Depends(get_current_user)):
    uid = str(user["uid"])
    room = get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")

    if uid not in room.players:
        raise HTTPException(status_code=400, detail="你不在这个房间中")

    del room.players[uid]

    if len(room.players) == 0:
        if room.engine:
            await room.engine.stop()
        remove_room(room_id)
        return {"message": "房间已解散"}

    # Transfer host if needed
    if room.host_id == uid:
        room.host_id = next(iter(room.players))

    return room.to_dict()
