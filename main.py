# main.py
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from game import Game


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("Modern Tetris")

    pygame.key.set_repeat(200, 50)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    tetris_game = Game(screen)
    tetris_game.run()


if __name__ == "__main__":
    main()