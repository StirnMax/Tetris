# game.py
import pygame
import sys
import os
import random

from settings import *
from tetromino import Tetromino, ShapeGenerator
from board import Board
from leaderboard import Leaderboard
from ui import Button
from fx import FXManager


class AudioPath:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}

        # Dynamisch den genauen Pfad zum assets-Ordner finden
        base_dir = os.path.dirname(__file__)
        assets_dir = os.path.join(base_dir, 'assets')

        # 1. Kurze Soundeffekte laden
        sound_files = {
            'move': 'move.wav',
            'rotate': 'rotate.wav',
            'drop': 'drop.wav',
            'clear': 'clear.wav',
            'level_up': 'level_up.wav'
        }
        for name, filename in sound_files.items():
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
            else:
                self.sounds[name] = None

        # 2. Hintergrundmusik (Soundtrack) laden
        music_file = os.path.join(assets_dir, 'Tetris.mp3')

        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                print(f"Erfolg: Musik geladen von {music_file}")
            except pygame.error as e:
                print(f"Pygame Fehler beim Musikladen: {e}")
        else:
            print(f"Fehler: Musikdatei nicht gefunden unter {music_file}")
            if os.path.exists(assets_dir):
                print(f"Diese Dateien liegen in deinem assets-Ordner: {os.listdir(assets_dir)}")

    def play(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.title_font = pygame.font.SysFont("arial", 50, bold=True)

        self.leaderboard = Leaderboard()
        self.audio = AudioPath()
        self.fx = FXManager()
        self.generator = ShapeGenerator()

        self.state = "MENU"

        center_x = SCREEN_WIDTH // 2 - 100
        self.btn_start_menu = Button(center_x, SCREEN_HEIGHT // 2, 200, 50, "START GAME", self.font)
        self.btn_quit_menu = Button(center_x, SCREEN_HEIGHT // 2 + 70, 200, 50, "QUIT GAME", self.font)

        sidebar_center = PLAY_WIDTH + (SIDEBAR_WIDTH // 2) - 80
        self.btn_pause = Button(sidebar_center, SCREEN_HEIGHT - 140, 160, 45, "PAUSE", self.font)
        self.btn_quit = Button(sidebar_center, SCREEN_HEIGHT - 70, 160, 45, "QUIT", self.font)

        self.reset_game()

    def reset_game(self):
        self.board = Board()
        self.generator = ShapeGenerator()
        self.current_piece = Tetromino(self.generator.get_shape())
        self.next_piece = Tetromino(self.generator.get_shape())

        self.score = 0
        self.level = 1

        self.fall_time = 0
        self.fall_speed = self.get_fall_speed()
        self.space_held = False

        self.lock_timer = 0
        self.lock_delay_ms = 500
        self.lock_resets = 0

    def get_fall_speed(self):
        return max(50, 800 - (self.level - 1) * 50)

    def add_score(self, points, x_pos=None, y_pos=None):
        if points <= 0: return
        self.score += points
        new_level = (self.score // 500) + 1

        if x_pos and y_pos:
            self.fx.spawn_text(x_pos, y_pos, f"+{points}", self.font, (255, 255, 0))

        if new_level > self.level:
            self.level = new_level
            self.fall_speed = self.get_fall_speed()
            self.audio.play('level_up')
            self.fx.spawn_text(PLAY_WIDTH // 2 - 50, PLAY_HEIGHT // 2, "LEVEL UP!", self.title_font, WHITE)

    def attempt_rotate(self):
        self.current_piece.rotate()
        if self.board.is_valid_position(self.current_piece):
            return True

        kicks = [(1, 0), (-1, 0), (0, -1), (2, 0), (-2, 0)]
        for dx, dy in kicks:
            if self.board.is_valid_position(self.current_piece, offset_x=dx, offset_y=dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                return True

        self.current_piece.rotate_back()
        return False

    def handle_lock_delay_reset(self):
        if self.lock_timer > 0 and self.lock_resets < 15:
            self.lock_timer = pygame.time.get_ticks()
            self.lock_resets += 1

    def process_events(self):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_start_menu.check_hover(mouse_pos)
        self.btn_quit_menu.check_hover(mouse_pos)
        self.btn_pause.check_hover(mouse_pos)
        self.btn_quit.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == "MENU":
                if self.btn_start_menu.is_clicked(event):
                    self.reset_game()
                    self.state = "PLAYING"
                if self.btn_quit_menu.is_clicked(event):
                    pygame.quit()
                    sys.exit()

            elif self.state in ["PLAYING", "PAUSED", "GAME_OVER"]:
                if self.btn_quit.is_clicked(event):
                    pygame.quit()
                    sys.exit()

                if self.state in ["PLAYING", "PAUSED"]:
                    if self.btn_pause.is_clicked(event):
                        if self.state == "PLAYING":
                            self.state = "PAUSED"
                            self.btn_pause.text = "RESUME"
                        else:
                            self.state = "PLAYING"
                            self.btn_pause.text = "PAUSE"

            if self.state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.board.is_valid_position(self.current_piece, offset_x=-1):
                            self.current_piece.x -= 1
                            self.audio.play('move')
                            self.handle_lock_delay_reset()
                    elif event.key == pygame.K_RIGHT:
                        if self.board.is_valid_position(self.current_piece, offset_x=1):
                            self.current_piece.x += 1
                            self.audio.play('move')
                            self.handle_lock_delay_reset()
                    elif event.key == pygame.K_UP:
                        if self.attempt_rotate():
                            self.audio.play('rotate')
                            self.handle_lock_delay_reset()
                    elif event.key == pygame.K_DOWN:
                        if self.board.is_valid_position(self.current_piece, offset_y=1):
                            self.current_piece.y += 1
                            self.add_score(1)
                    elif event.key == pygame.K_SPACE:
                        if not self.space_held:
                            self.space_held = True
                            drop_distance = 0
                            while self.board.is_valid_position(self.current_piece, offset_y=1):
                                self.current_piece.y += 1
                                drop_distance += 2

                            px = (self.current_piece.x + len(self.current_piece.matrix[0]) // 2) * BLOCK_SIZE
                            py = self.current_piece.y * BLOCK_SIZE
                            self.fx.spawn_explosion(px, py, self.current_piece.color, 15)

                            self.add_score(drop_distance)
                            self.audio.play('drop')
                            self.lock_and_spawn()

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.space_held = False

            if self.state == "GAME_OVER" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                    self.state = "PLAYING"

    def lock_and_spawn(self):
        self.board.lock_piece(self.current_piece)
        lines = self.board.clear_lines()

        if lines > 0:
            line_scores = {1: 40, 2: 100, 3: 300, 4: 1200}
            points_earned = line_scores.get(lines, 0) * self.level

            self.add_score(points_earned, PLAY_WIDTH // 2, self.current_piece.y * BLOCK_SIZE)
            self.audio.play('clear')

            for _ in range(30):
                px = random.randint(0, PLAY_WIDTH)
                py = self.current_piece.y * BLOCK_SIZE
                self.fx.spawn_explosion(px, py, WHITE, 1)

        self.current_piece = self.next_piece
        self.next_piece = Tetromino(self.generator.get_shape())
        self.lock_timer = 0
        self.lock_resets = 0

        if not self.board.is_valid_position(self.current_piece):
            self.state = "GAME_OVER"
            self.btn_pause.text = "PAUSE"
            self.leaderboard.save_score(self.score)

    def update(self):
        if self.state != "PLAYING":
            return

        self.fx.update()

        if not self.board.is_valid_position(self.current_piece, offset_y=1):
            if self.lock_timer == 0:
                self.lock_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.lock_timer >= self.lock_delay_ms:
                self.lock_and_spawn()
        else:
            self.lock_timer = 0
            self.fall_time += self.clock.get_rawtime()
            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                self.current_piece.y += 1

    def draw_3d_block(self, surface, x, y, color, size, alpha=255):
        rect = pygame.Rect(x, y, size, size)

        if alpha < 255:
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color, alpha), (0, 0, size, size), 2)
            surface.blit(s, (x, y))
            return

        pygame.draw.rect(surface, color, rect)

        light = (min(color[0] + 70, 255), min(color[1] + 70, 255), min(color[2] + 70, 255))
        pygame.draw.polygon(surface, light, [(x, y), (x + size, y), (x + size - 4, y + 4), (x + 4, y + 4)])
        pygame.draw.polygon(surface, light, [(x, y), (x + 4, y + 4), (x + 4, y + size - 4), (x, y + size)])

        dark = (max(color[0] - 70, 0), max(color[1] - 70, 0), max(color[2] - 70, 0))
        pygame.draw.polygon(surface, dark,
                            [(x, y + size), (x + size, y + size), (x + size - 4, y + size - 4), (x + 4, y + size - 4)])
        pygame.draw.polygon(surface, dark,
                            [(x + size, y), (x + size - 4, y + 4), (x + size - 4, y + size - 4), (x + size, y + size)])

    def draw_grid(self):
        for y in range(ROWS):
            for x in range(COLUMNS):
                if self.board.grid[y][x] != 0:
                    px = x * BLOCK_SIZE
                    py = y * BLOCK_SIZE
                    self.draw_3d_block(self.screen, px, py, self.board.grid[y][x], BLOCK_SIZE)
                else:
                    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_ghost_piece(self):
        ghost_y = self.current_piece.y
        while self.board.is_valid_position(self.current_piece, offset_y=(ghost_y - self.current_piece.y + 1)):
            ghost_y += 1

        for row_idx, row in enumerate(self.current_piece.matrix):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = (self.current_piece.x + col_idx) * BLOCK_SIZE
                    y = (ghost_y + row_idx) * BLOCK_SIZE
                    self.draw_3d_block(self.screen, x, y, self.current_piece.color, BLOCK_SIZE, alpha=100)

    def draw_piece(self, piece, offset_x=0, offset_y=0):
        for row_idx, row in enumerate(piece.matrix):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = (piece.x + col_idx) * BLOCK_SIZE + offset_x
                    y = (piece.y + row_idx) * BLOCK_SIZE + offset_y
                    self.draw_3d_block(self.screen, x, y, piece.color, BLOCK_SIZE)

    def draw_sidebar(self):
        sidebar_x = PLAY_WIDTH + 20

        next_text = self.font.render("NEXT PIECE:", True, WHITE)
        self.screen.blit(next_text, (sidebar_x, 30))

        preview_offset_x = sidebar_x + 60 - (self.next_piece.x * BLOCK_SIZE)
        preview_offset_y = 80 - (self.next_piece.y * BLOCK_SIZE)
        self.draw_piece(self.next_piece, offset_x=preview_offset_x, offset_y=preview_offset_y)

        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (sidebar_x, 260))

        level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(level_text, (sidebar_x, 310))

        board_text = self.font.render("HIGH SCORES:", True, WHITE)
        self.screen.blit(board_text, (sidebar_x, 400))

        top_scores = self.leaderboard.get_top_scores()
        for i, sc in enumerate(top_scores):
            sc_text = self.small_font.render(f"{i + 1}. {sc}", True, GRAY)
            self.screen.blit(sc_text, (sidebar_x, 440 + (i * 30)))

        self.btn_pause.draw(self.screen)
        self.btn_quit.draw(self.screen)

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "MENU":
            title_text = self.title_font.render("TETRIS", True, (0, 255, 255))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
            self.btn_start_menu.draw(self.screen)
            self.btn_quit_menu.draw(self.screen)

        else:
            pygame.draw.rect(self.screen, DARK_GRAY, (PLAY_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
            pygame.draw.line(self.screen, WHITE, (PLAY_WIDTH, 0), (PLAY_WIDTH, SCREEN_HEIGHT), 2)

            self.draw_grid()

            if self.state != "GAME_OVER":
                self.draw_ghost_piece()
                self.draw_piece(self.current_piece)

            self.fx.draw(self.screen)
            self.draw_sidebar()

            if self.state == "PAUSED":
                s = pygame.Surface((PLAY_WIDTH, SCREEN_HEIGHT))
                s.set_alpha(180)
                s.fill(BLACK)
                self.screen.blit(s, (0, 0))
                pause_text = self.title_font.render("PAUSED", True, WHITE)
                self.screen.blit(pause_text, (PLAY_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))

            if self.state == "GAME_OVER":
                s = pygame.Surface((PLAY_WIDTH, SCREEN_HEIGHT))
                s.set_alpha(180)
                s.fill(BLACK)
                self.screen.blit(s, (0, 0))

                game_over_text = self.title_font.render("GAME OVER", True, (255, 50, 50))
                restart_text = self.small_font.render("Press 'R' to Restart", True, WHITE)
                self.screen.blit(game_over_text,
                                 (PLAY_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
                self.screen.blit(restart_text,
                                 (PLAY_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()

    def run(self):
        while True:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)