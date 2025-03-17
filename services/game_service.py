# services/game_service.py
from models.game import Game, Board, Cell, CellType, GameState
from typing import Dict, List, Tuple
import random

class GameService:
    @staticmethod
    def are_all_ships_destroyed(board: Dict) -> bool:
        for row in board['cells']:
            for cell in row:
                if cell.startswith('P') or cell.startswith('Q'):
                    health = int(cell[1])
                    if health > 0:
                        return False
        return True
    
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
    def calculate_missile_count(board_size: int, is_berserk: bool) -> int:
        base_count = board_size  # Proportional to board size
        return base_count // 2 if is_berserk else base_count

    @staticmethod
    def process_shot(board: Dict, position: str) -> Tuple[bool, bool]:
        row = ord(position[0]) - 65  # Convert 'A' to 0, 'B' to 1, etc.
        col = int(position[1:]) - 1  # Convert '1' to 0, '2' to 1, etc.
        
        if row < 0 or row >= len(board['cells']) or col < 0 or col >= len(board['cells'][0]):
            return False, False  # Invalid position

        # board['missile_count'] -= 1
        
        cell = board['cells'][row][col]
        
        if cell == 'sea' or cell == 'sea1':
            board['cells'][row][col] = 'sea1'  # Mark sea as hit
            return False, False

        cell_type = cell[0]
        health = int(cell[1])
        hit_flag = int(cell[2])

        if health == 0 and hit_flag == 1:
            return False, False  # Already hit

        health -= 1
        hit_flag = 1
        new_cell = f"{cell_type}{health}{hit_flag}"
        board['cells'][row][col] = new_cell
        # board['missile_count'] += 1
        
        cell_destroyed = health == 0
        
        return True, cell_destroyed