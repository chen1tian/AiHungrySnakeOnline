from __future__ import annotations

import asyncio
import json
import random
import time
from typing import TYPE_CHECKING

from config import (
    MAP_WIDTH, MAP_HEIGHT, TICK_RATE, RESPAWN_TIME,
    INITIAL_SNAKE_LENGTH, INITIAL_HP, DAMAGE_IMMUNE_DURATION,
    SPECIAL_APPLE_INTERVAL_MIN,
    SPECIAL_APPLE_INTERVAL_MAX, SPEED_BOOST_DURATION,
    SLOW_MOTION_DURATION,
)
from game_state import (
    Apple, AppleType, Direction, DIRECTION_VECTORS, OPPOSITE_DIRECTIONS,
    Point, Room, Snake,
)

if TYPE_CHECKING:
    pass


class GameEngine:
    def __init__(self, room: Room):
        self.room = room
        self.snakes: dict[str, Snake] = {}
        self.apples: list[Apple] = []
        self.running = False
        self._task: asyncio.Task | None = None
        self.slow_motion_until: float = 0
        self.last_special_apple_time: float = 0
        self.next_special_apple_interval: float = random.uniform(
            SPECIAL_APPLE_INTERVAL_MIN, SPECIAL_APPLE_INTERVAL_MAX
        )
        self.tick_count = 0

    def start(self):
        self.running = True
        now = time.time()
        self.last_special_apple_time = now

        # Initialize snakes for all players
        for uid, player in self.room.players.items():
            snake = self._create_snake(uid, player.username, player.emoji, player.color)
            self.snakes[uid] = snake

        # Generate initial drop items
        target_count = max(4, len(self.room.players) * 2)
        drop_types = [AppleType.HEART, AppleType.SPIKE, AppleType.SPEED, AppleType.GROWTH, AppleType.INVINCIBLE, AppleType.SLOW]
        for _ in range(target_count):
            self._spawn_apple(random.choice(drop_types))

        self._task = asyncio.create_task(self._game_loop())

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def _create_snake(self, player_id: str, username: str, emoji: str, color: str) -> Snake:
        pos = self._random_spawn_position()
        body = [Point(pos.x - i, pos.y) for i in range(INITIAL_SNAKE_LENGTH)]
        # Ensure body is within map bounds
        for p in body:
            p.x = max(0, min(MAP_WIDTH - 1, p.x))
        return Snake(
            player_id=player_id,
            username=username,
            body=body,
            direction=Direction.RIGHT,
            emoji=emoji,
            color=color,
            hp=INITIAL_HP,
        )

    def _random_spawn_position(self) -> Point:
        margin = INITIAL_SNAKE_LENGTH + 2
        x = random.randint(margin, MAP_WIDTH - margin - 1)
        y = random.randint(margin, MAP_HEIGHT - margin - 1)
        return Point(x, y)

    def _get_occupied_positions(self) -> set[tuple[int, int]]:
        occupied = set()
        for snake in self.snakes.values():
            if snake.alive:
                for p in snake.body:
                    occupied.add((p.x, p.y))
        for apple in self.apples:
            occupied.add((apple.position.x, apple.position.y))
        return occupied

    def _find_empty_position(self) -> Point | None:
        occupied = self._get_occupied_positions()
        attempts = 0
        while attempts < 100:
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if (x, y) not in occupied:
                return Point(x, y)
            attempts += 1
        # Fallback: brute force
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if (x, y) not in occupied:
                    return Point(x, y)
        return None

    def _spawn_apple(self, apple_type: AppleType) -> bool:
        pos = self._find_empty_position()
        if pos is None:
            return False
        invincible_duration = 0
        if apple_type == AppleType.INVINCIBLE:
            invincible_duration = random.choice([3, 5, 10])
        self.apples.append(Apple(
            position=pos,
            apple_type=apple_type,
            invincible_duration=invincible_duration,
        ))
        return True

    def set_direction(self, player_id: str, direction: str):
        snake = self.snakes.get(player_id)
        if not snake or not snake.alive:
            return
        try:
            new_dir = Direction(direction)
        except ValueError:
            return
        # Prevent 180-degree turn
        if OPPOSITE_DIRECTIONS.get(new_dir) == snake.direction:
            return
        snake.direction = new_dir

    async def _game_loop(self):
        try:
            while self.running:
                now = time.time()
                is_slow = now < self.slow_motion_until
                tick_rate = TICK_RATE * 2 if is_slow else TICK_RATE

                await asyncio.sleep(tick_rate)

                if not self.running:
                    break

                self.tick_count += 1
                now = time.time()

                self._move_snakes(now)
                self._check_collisions(now)
                self._check_apple_collisions(now)
                self._handle_respawns(now)
                self._manage_apples(now)

                await self._broadcast_state(now)
        except asyncio.CancelledError:
            pass

    def _move_snakes(self, now: float):
        for snake in self.snakes.values():
            if not snake.alive:
                continue

            dx, dy = DIRECTION_VECTORS[snake.direction]

            # Speed boost: move twice
            moves = 2 if snake.is_speed_boosted(now) else 1

            for _ in range(moves):
                new_head = Point(snake.head().x + dx, snake.head().y + dy)
                snake.body.insert(0, new_head)

                if snake.pending_growth > 0:
                    snake.pending_growth -= 1
                else:
                    snake.body.pop()

    def _check_collisions(self, now: float):
        damage_events = []  # list of (target_snake, attacker_snake_or_None)

        for snake in list(self.snakes.values()):
            if not snake.alive:
                continue

            head = snake.head()

            # Wall collision
            if head.x < 0 or head.x >= MAP_WIDTH or head.y < 0 or head.y >= MAP_HEIGHT:
                # Always bounce off wall
                snake.body.pop(0)
                snake.direction = OPPOSITE_DIRECTIONS[snake.direction]
                damage_events.append((snake, None))
                continue

            # Self collision (check body excluding head)
            for segment in snake.body[1:]:
                if head == segment:
                    damage_events.append((snake, None))
                    break

        # Snake vs snake collision
        alive_snakes = [s for s in self.snakes.values() if s.alive]
        head_on_processed = set()

        for snake in alive_snakes:
            head = snake.head()
            for other in alive_snakes:
                if other.player_id == snake.player_id:
                    continue
                # Check if same team (same color)
                if snake.color == other.color:
                    continue

                for i, segment in enumerate(other.body):
                    if head == segment:
                        if i == 0:
                            # Head-on collision: both take damage
                            pair = tuple(sorted([snake.player_id, other.player_id]))
                            if pair not in head_on_processed:
                                damage_events.append((snake, other))
                                damage_events.append((other, snake))
                                head_on_processed.add(pair)
                        elif i <= other.hp:
                            # Hit head/hearts area: defender takes damage
                            damage_events.append((other, snake))
                        elif other.spikes > 0 and i >= len(other.body) - other.spikes:
                            # Hit spike segments: attacker takes damage
                            damage_events.append((snake, other))
                        else:
                            # Hit regular body: attacker takes damage
                            damage_events.append((snake, None))
                        break

        # Apply all damage events
        for target, attacker in damage_events:
            self._damage_snake(target, now, killer=attacker)

    def _check_apple_collisions(self, now: float):
        for snake in self.snakes.values():
            if not snake.alive:
                continue
            head = snake.head()
            eaten = []
            for i, apple in enumerate(self.apples):
                if head == apple.position:
                    self._apply_apple_effect(snake, apple, now)
                    eaten.append(i)
            # Remove eaten apples (reverse order to preserve indices)
            for i in reversed(eaten):
                self.apples.pop(i)

    def _apply_apple_effect(self, snake: Snake, apple: Apple, now: float):
        if apple.apple_type == AppleType.SPEED:
            snake.speed_boost_until = now + SPEED_BOOST_DURATION
        elif apple.apple_type == AppleType.GROWTH:
            snake.pending_growth += 3
        elif apple.apple_type == AppleType.INVINCIBLE:
            snake.invincible_until = now + apple.invincible_duration
        elif apple.apple_type == AppleType.SLOW:
            self.slow_motion_until = now + SLOW_MOTION_DURATION
        elif apple.apple_type == AppleType.HEART:
            snake.hp += 1
            # Insert a heart segment right after the current last heart
            insert_idx = min(snake.hp, len(snake.body))
            if insert_idx > 0 and insert_idx <= len(snake.body):
                ref_point = snake.body[insert_idx - 1]
                snake.body.insert(insert_idx, Point(ref_point.x, ref_point.y))
        elif apple.apple_type == AppleType.SPIKE:
            snake.spikes += 1
            snake.pending_growth += 1  # grows at tail

    def _damage_snake(self, snake: Snake, now: float, killer: Snake | None = None):
        if not snake.alive:
            return
        if snake.is_invincible(now) or snake.is_damage_immune(now):
            return
        snake.hp -= 1
        snake.damage_immune_until = now + DAMAGE_IMMUNE_DURATION
        if snake.hp <= 0:
            if killer and killer.alive:
                killer.kills += 1
            self._kill_snake(snake, now)
            return
        # Remove one body segment (the lost heart)
        remove_idx = snake.hp + 1
        if remove_idx < len(snake.body):
            snake.body.pop(remove_idx)
        elif len(snake.body) > 1:
            snake.body.pop()

    def _kill_snake(self, snake: Snake, now: float):
        if not snake.alive:
            return
        snake.alive = False
        snake.respawn_timer = now + RESPAWN_TIME
        snake.body.clear()
        snake.hp = 0
        snake.spikes = 0

    def _handle_respawns(self, now: float):
        for snake in self.snakes.values():
            if not snake.alive and snake.respawn_timer > 0 and now >= snake.respawn_timer:
                # Respawn
                pos = self._random_spawn_position()
                snake.body = [Point(pos.x - i, pos.y) for i in range(INITIAL_SNAKE_LENGTH)]
                for p in snake.body:
                    p.x = max(0, min(MAP_WIDTH - 1, p.x))
                snake.direction = Direction.RIGHT
                snake.alive = True
                snake.respawn_timer = 0
                snake.pending_growth = 0
                snake.hp = INITIAL_HP
                snake.spikes = 0
                snake.damage_immune_until = 0

    def _manage_apples(self, now: float):
        # Keep minimum drop items on map
        drop_types = [AppleType.HEART, AppleType.SPIKE, AppleType.SPEED, AppleType.GROWTH, AppleType.INVINCIBLE, AppleType.SLOW]
        total_count = len(self.apples)
        target_count = max(4, len(self.snakes) * 2)
        while total_count < target_count:
            if self._spawn_apple(random.choice(drop_types)):
                total_count += 1
            else:
                break

        # Special apple spawn timer
        if now - self.last_special_apple_time >= self.next_special_apple_interval:
            special_type = random.choice([
                AppleType.SPEED, AppleType.GROWTH,
                AppleType.INVINCIBLE, AppleType.SLOW,
                AppleType.HEART, AppleType.SPIKE,
            ])
            self._spawn_apple(special_type)
            self.last_special_apple_time = now
            self.next_special_apple_interval = random.uniform(
                SPECIAL_APPLE_INTERVAL_MIN, SPECIAL_APPLE_INTERVAL_MAX
            )

    def remove_player(self, player_id: str):
        snake = self.snakes.pop(player_id, None)
        if snake:
            snake.alive = False

    def get_state(self, now: float) -> dict:
        return {
            "type": "state",
            "snakes": [s.to_dict(now) for s in self.snakes.values()],
            "apples": [a.to_dict() for a in self.apples],
            "map_width": MAP_WIDTH,
            "map_height": MAP_HEIGHT,
            "slow_motion": now < self.slow_motion_until,
            "tick": self.tick_count,
        }

    async def _broadcast_state(self, now: float):
        state = self.get_state(now)
        msg = json.dumps(state)
        disconnected = []
        for uid, ws in list(self.room.connections.items()):
            try:
                await ws.send_text(msg)
            except Exception:
                disconnected.append(uid)
        for uid in disconnected:
            self.room.connections.pop(uid, None)
