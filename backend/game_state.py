from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_ws import ConnectionManager

from config import MAP_WIDTH, MAP_HEIGHT


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class AppleType(str, Enum):
    NORMAL = "normal"
    SPEED = "speed"
    GROWTH = "growth"
    INVINCIBLE = "invincible"
    SLOW = "slow"


DIRECTION_VECTORS = {
    Direction.UP: (0, -1),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0),
    Direction.RIGHT: (1, 0),
}

OPPOSITE_DIRECTIONS = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


@dataclass
class Point:
    x: int
    y: int

    def to_dict(self):
        return {"x": self.x, "y": self.y}

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


@dataclass
class Snake:
    player_id: str
    username: str
    body: list[Point] = field(default_factory=list)
    direction: Direction = Direction.RIGHT
    alive: bool = True
    respawn_timer: float = 0
    speed_boost_until: float = 0
    invincible_until: float = 0
    emoji: str = "🐍"
    color: str = "#4CAF50"
    kills: int = 0
    pending_growth: int = 0

    def head(self) -> Point:
        return self.body[0] if self.body else Point(0, 0)

    def is_speed_boosted(self, now: float) -> bool:
        return now < self.speed_boost_until

    def is_invincible(self, now: float) -> bool:
        return now < self.invincible_until

    def to_dict(self, now: float) -> dict:
        return {
            "player_id": self.player_id,
            "username": self.username,
            "body": [p.to_dict() for p in self.body],
            "direction": self.direction.value,
            "alive": self.alive,
            "respawn_timer": max(0, round(self.respawn_timer - now, 1)) if not self.alive else 0,
            "emoji": self.emoji,
            "color": self.color,
            "kills": self.kills,
            "length": len(self.body),
            "invincible": self.is_invincible(now),
            "speed_boost": self.is_speed_boosted(now),
        }


@dataclass
class Apple:
    position: Point
    apple_type: AppleType = AppleType.NORMAL
    invincible_duration: int = 0  # only for invincible apples: 3, 5, or 10

    def to_dict(self) -> dict:
        d = {
            "position": self.position.to_dict(),
            "type": self.apple_type.value,
        }
        if self.apple_type == AppleType.INVINCIBLE:
            d["duration"] = self.invincible_duration
        return d


@dataclass
class PlayerInfo:
    user_id: str
    username: str
    emoji: str = "🐍"
    color: str = "#4CAF50"
    ready: bool = False


class RoomStatus(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"


@dataclass
class Room:
    room_id: str
    room_name: str
    host_id: str
    players: dict[str, PlayerInfo] = field(default_factory=dict)
    status: RoomStatus = RoomStatus.WAITING
    engine: object | None = None  # GameEngine instance, set when game starts
    connections: dict[str, object] = field(default_factory=dict)  # user_id -> WebSocket

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "host_id": self.host_id,
            "player_count": len(self.players),
            "players": {
                uid: {"username": p.username, "emoji": p.emoji, "color": p.color}
                for uid, p in self.players.items()
            },
            "status": self.status.value,
        }


# Global room storage
rooms: dict[str, Room] = {}


def get_room(room_id: str) -> Room | None:
    return rooms.get(room_id)


def create_room(room_id: str, room_name: str, host_id: str, host_username: str) -> Room:
    room = Room(
        room_id=room_id,
        room_name=room_name,
        host_id=host_id,
    )
    room.players[host_id] = PlayerInfo(user_id=host_id, username=host_username)
    rooms[room_id] = room
    return room


def remove_room(room_id: str):
    rooms.pop(room_id, None)
