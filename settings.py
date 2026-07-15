# settings.py

# Display Settings
BLOCK_SIZE = 40
COLUMNS = 10
ROWS = 20
PLAY_WIDTH = COLUMNS * BLOCK_SIZE
PLAY_HEIGHT = ROWS * BLOCK_SIZE
SIDEBAR_WIDTH = 300
SCREEN_WIDTH = PLAY_WIDTH + SIDEBAR_WIDTH
SCREEN_HEIGHT = PLAY_HEIGHT
FPS = 60

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
GRID_COLOR = (50, 50, 50)
BUTTON_COLOR = (70, 70, 150)
BUTTON_HOVER = (100, 100, 200)

# Tetromino Colors
COLORS = {
    'I': (0, 255, 255),
    'J': (0, 0, 255),
    'L': (255, 165, 0),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'T': (128, 0, 128),
    'Z': (255, 0, 0)
}

SHAPES = {
    'I': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    'J': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    'L': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    'T': [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    'Z': [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
}