# board.py
from settings import COLUMNS, ROWS


class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

    def is_valid_position(self, tetromino, offset_x=0, offset_y=0):
        for row_idx, row in enumerate(tetromino.matrix):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = tetromino.x + col_idx + offset_x
                    y = tetromino.y + row_idx + offset_y

                    if x < 0 or x >= COLUMNS or y >= ROWS:
                        return False
                    if y >= 0 and self.grid[y][x] != 0:
                        return False
        return True

    def lock_piece(self, tetromino):
        for row_idx, row in enumerate(tetromino.matrix):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = tetromino.x + col_idx
                    y = tetromino.y + row_idx
                    if y >= 0:
                        self.grid[y][x] = tetromino.color

    def clear_lines(self):
        lines_cleared = 0
        row = ROWS - 1

        while row >= 0:
            if 0 not in self.grid[row]:
                lines_cleared += 1
                del self.grid[row]
                self.grid.insert(0, [0 for _ in range(COLUMNS)])
            else:
                row -= 1

        return lines_cleared