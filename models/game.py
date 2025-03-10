# models/game.py
from .base import MongoBaseModel
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import Field

class GameState(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class CellType(str, Enum):
    P = "P"  # 1 hit to destroy
    Q = "Q"  # 2 hits to destroy

class Cell(MongoBaseModel):
    type: CellType
    hits: int = 0
    destroyed: bool = False

class Board(MongoBaseModel):
    cells: Dict[str, Cell]  # position -> cell
    missile_count: int
    is_berserk: bool = False

class Game(MongoBaseModel):
    grid_id: str
    state: GameState = GameState.WAITING
    players: List[str]  # player ids
    boards: Dict[str, Board]  # player_id -> board
    current_turn: Optional[str]  # player_id
    winner: Optional[str]  # player_id
    score: Optional[int]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
