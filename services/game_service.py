# services/game_service.py
from models.game import Game, Board, Cell, CellType, GameState
from typing import Dict, List, Tuple
import random

class GameService:
    @staticmethod
    def create_ship_configuration() -> Dict[str, Cell]:
        cells = {}
        ships = [
            {"size": (1, 3), "type": CellType.P},
            {"size": (2, 2), "type": CellType.Q},
            {"size": (1, 4), "type": CellType.P}
        ]
        
        for ship in ships:
            position = GameService._find_random_position(cells, ship["size"])
            for pos in position:
                cells[pos] = Cell(type=ship["type"])
        
        return cells

    @staticmethod
    def _find_random_position(
        existing_cells: Dict[str, Cell], 
        size: Tuple[int, int]
    ) -> List[str]:
        while True:
            start_row = random.randint(0, 8)
            start_col = random.randint(0, 8)
            is_horizontal = random.choice([True, False])
            
            positions = []
            for i in range(size[0]):
                for j in range(size[1]):
                    if is_horizontal:
                        pos = f"{chr(65 + start_row + i)}{start_col + j + 1}"
                    else:
                        pos = f"{chr(65 + start_row + j)}{start_col + i + 1}"
                    
                    if (pos in existing_cells or 
                        not GameService._is_valid_position(pos)):
                        break
                    positions.append(pos)
            
            if len(positions) == size[0] * size[1]:
                return positions

    @staticmethod
    def _is_valid_position(pos: str) -> bool:
        return (
            len(pos) >= 2 and
            'A' <= pos[0] <= 'I' and
            1 <= int(pos[1:]) <= 9
        )

    @staticmethod
    def calculate_missile_count(is_berserk: bool) -> int:
        base_count = 81  # 9x9 grid
        return base_count // 2 if is_berserk else base_count

    @staticmethod
    def process_shot(board: Board, position: str) -> Tuple[bool, bool, bool]:
        cell = board.cells.get(position)
        if not cell:
            return False, False, False
        
        cell.hits += 1
        if cell.type == CellType.P:
            cell.destroyed = cell.hits >= 1
        else:  # CellType.Q
            cell.destroyed = cell.hits >= 2
            
        ship_destroyed = all(
            c.destroyed for c in board.cells.values()
            if c.type == cell.type
        )
        
        return True, cell.destroyed, ship_destroyed
