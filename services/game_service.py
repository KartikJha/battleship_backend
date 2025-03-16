# services/game_service.py
from models.game import Game, Board, Cell, CellType, GameState
from typing import Dict, List, Tuple
import random

class GameService:
    @staticmethod
    def create_ship_configuration(board_size: int) -> List[List[str]]:
        cells = {}
        grid_size = int(board_size ** 0.5)
        ships = GameService._generate_ships(board_size, grid_size)
        
        for ship in ships:
            position = GameService._find_random_position(cells, ship["size"], grid_size)
            for pos in position:
                cells[pos] = Cell(type=ship["type"], health=ship["health"])
        
        # Create a 2D array to represent the board
        board = [["sea" for _ in range(grid_size)] for _ in range(grid_size)]
        
        for row in range(grid_size):
            for col in range(grid_size):
                pos = f"{chr(65 + row)}{col + 1}"
                if pos in cells:
                    cell = cells[pos]
                    board[row][col] = f"{cell.type}{GameService.get_initial_health(cell.type)}0"  # Initial health and hit status
                else:
                    board[row][col] = "sea"
        
        return board
    
    @staticmethod
    def get_initial_health(cell_type: CellType) -> int:
        if cell_type == CellType.Q:
            return 2
        elif cell_type == CellType.P:
            return 1
        else:
            raise ValueError("Invalid cell type")

    @staticmethod
    def _generate_ships(board_size: int, grid_size) -> List[Dict[str, Tuple[int, int]]]:
        # Proportionally determine the number and size of ships based on board size
        num_ships = max(1, board_size // 10)
        ships = []
        for _ in range(num_ships):
            ship_type = random.choice([CellType.P, CellType.Q])
            ship_size = (random.randint(1, grid_size), random.randint(1, grid_size))
            health = 1 if ship_type == CellType.P else 2
            ships.append({"size": ship_size, "type": ship_type, "health": health})
        return ships

    @staticmethod
    def _find_random_position(
        existing_cells: Dict[str, Cell], 
        size: Tuple[int, int],
        grid_size: int
    ) -> List[str]:
        while True:
            start_row = random.randint(0, grid_size - size[0])
            start_col = random.randint(0, grid_size - size[1])
            is_horizontal = random.choice([True, False])
            
            positions = []
            for i in range(size[0]):
                for j in range(size[1]):
                    if is_horizontal:
                        pos = f"{chr(65 + start_row + i)}{start_col + j + 1}"
                    else:
                        pos = f"{chr(65 + start_row + j)}{start_col + i + 1}"
                    
                    if (pos in existing_cells or 
                        not GameService._is_valid_position(pos, grid_size)):
                        break
                    positions.append(pos)
            
            if len(positions) == size[0] * size[1]:
                return positions

    @staticmethod
    def _is_valid_position(pos: str, grid_size: int) -> bool:
        return (
            len(pos) >= 2 and
            'A' <= pos[0] < chr(65 + grid_size) and
            1 <= int(pos[1:]) <= grid_size
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
