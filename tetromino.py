# tetromino.py
import random
from settings import SHAPES, COLORS, COLUMNS


class ShapeGenerator:
    def __init__(self):
        self.bag = []

    def get_shape(self):
        if not self.bag:
            self.bag = list(SHAPES.keys())
            random.shuffle(self.bag)
        return self.bag.pop(0)


class Tetromino:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.matrix = [row[:] for row in SHAPES[self.shape_type]]
        self.color = COLORS[self.shape_type]

        self.x = COLUMNS // 2 - len(self.matrix[0]) // 2
        self.y = 0

    def rotate(self):
        self.matrix = [list(row) for row in zip(*self.matrix[::-1])]

    def rotate_back(self):
        self.matrix = [list(row) for row in zip(*self.matrix)][::-1]