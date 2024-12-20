from typing import List, Optional
from pydantic import BaseModel, Field, RootModel
from datetime import datetime

# Определяем классы для Direction3D и Point3D как RootModel
class Direction3D(RootModel):
    root: List[int] = Field(..., min_items=3, max_items=3, example=[0, 0, 0])

class Point3D(RootModel):
    root: List[int] = Field(..., min_items=3, max_items=3, example=[152, 51, 10])

# Определяем класс для SnakeRequest
class SnakeRequest(BaseModel):
    class SnakeItem(BaseModel):
        id: str = Field(..., description="Unique snake identifier", example="6c1dfac6d106e6f4d0ffdddb665238253574ac1f")
        direction: Direction3D = Field(...)

    snakes: List[SnakeItem]

# Определяем класс для Snake
class Snake(BaseModel):
    id: str = Field(..., description="Unique snake identifier", example="db59f7bff43351d69b540c666fa8ff9f1c81f05c")
    direction: List[int] = Field(..., description="Current direction vector [x, y, z]", example=[1, 0, 0])
    oldDirection: List[int] = Field(..., description="Previous direction vector [x, y, z]", example=[0, 0, -1])
    geometry: List[Point3D] = Field(..., description="Snake body segments coordinates")
    deathCount: int = Field(..., description="Number of times snake died", example=16)
    status: str = Field(..., description="Current snake status", enum=["alive", "dead"], example="alive")
    reviveRemainMs: int = Field(..., description="Milliseconds remaining until revival if dead", example=0)

# Определяем класс для Enemy
class Enemy(BaseModel):
    geometry: List[Point3D] = Field(..., description="Enemy body segments coordinates")
    status: str = Field(..., enum=["alive", "dead"], example="alive")
    kills: int = Field(..., description="Number of kills by this enemy", example=0)

# Определяем класс для Food
class Food(BaseModel):
    c: Point3D = Field(...)
    points: int = Field(..., description="Points value of this food", example=6)

# Определяем класс для SpecialFood
class SpecialFood(BaseModel):
    golden: List[Point3D] = Field(..., description="Array of golden food items")
    suspicious: List[Point3D] = Field(..., description="Array of suspicious food items")

# Определяем класс для GameState
class GameState(BaseModel):
    mapSize: List[int] = Field(..., description="Map dimensions [width, height, depth]", example=[180, 180, 30])
    name: str = Field(..., description="Game instance name", example="CleanCrib envious")
    points: int = Field(..., description="Current score", example=275)
    fences: List[Point3D] = Field(..., description="Array of fence coordinates")
    snakes: List[Snake] = Field(..., description="Array of snakes in the game")
    enemies: List[Enemy] = Field(..., description="Array of enemies in the game")
    food: List[Food] = Field(..., description="Array of regular food items")
    specialFood: SpecialFood = Field(...)
    turn: int = Field(..., description="Current game turn number", example=1548)
    reviveTimeoutSec: int = Field(..., description="Seconds until snake revival", example=5)
    tickRemainMs: int = Field(..., description="Milliseconds remaining in current turn", example=60)
    errors: List[str] = Field(..., description="Array of error messages if any", example=[])

# Определяем класс для Round
class Round(BaseModel):
    name: str = Field(..., description="Name of the game round", example="final-3")
    startAt: datetime = Field(..., description="Round start time in ISO 8601 format", example="2024-10-12T16:00:00Z")
    endAt: datetime = Field(..., description="Round end time in ISO 8601 format", example="2024-10-12T16:55:00Z")
    duration: int = Field(..., description="Duration of the round in seconds", example=3300)
    status: str = Field(..., description="Current status of the round", enum=["not started", "active", "ended"], example="ended")
    repeat: int = Field(..., description="Number of times the round repeats (0 for no repeat)", example=0)

# Определяем класс для GameRoundsResponse
class GameRoundsResponse(BaseModel):
    gameName: str = Field(..., description="Name of the game", example="snake3d")
    rounds: List[Round] = Field(..., description="List of game rounds")
    now: datetime = Field(..., description="Current server time in ISO 8601 format", example="2024-12-19T10:45:45.632269185Z")