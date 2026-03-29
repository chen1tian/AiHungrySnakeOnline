import secrets

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DATABASE_URL = "sqlite+aiosqlite:///./snake_game.db"

# Game settings
MAP_WIDTH = 60
MAP_HEIGHT = 40
TICK_RATE = 0.1  # 100ms per tick
RESPAWN_TIME = 5  # seconds
INITIAL_SNAKE_LENGTH = 3
SPECIAL_APPLE_INTERVAL_MIN = 5  # seconds
SPECIAL_APPLE_INTERVAL_MAX = 10  # seconds
SPEED_BOOST_DURATION = 5  # seconds
SLOW_MOTION_DURATION = 5  # seconds
