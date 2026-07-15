# fx.py
import pygame
import random

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, -1)
        self.life = 255
        self.decay = random.uniform(5, 10)
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(self.life)), (self.size//2, self.size//2), self.size//2)
            surface.blit(surf, (self.x, self.y))

class FloatingText:
    def __init__(self, x, y, text, font, color):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color
        self.life = 255
        self.vy = -1.5

    def update(self):
        self.y += self.vy
        self.life -= 3

    def draw(self, surface):
        if self.life > 0:
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(int(max(0, self.life)))
            surface.blit(text_surf, (self.x, self.y))

class FXManager:
    def __init__(self):
        self.particles = []
        self.texts = []

    def spawn_explosion(self, x, y, color, amount=10):
        for _ in range(amount):
            self.particles.append(Particle(x, y, color))

    def spawn_text(self, x, y, text, font, color):
        self.texts.append(FloatingText(x, y, text, font, color))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        self.texts = [t for t in self.texts if t.life > 0]
        for p in self.particles: p.update()
        for t in self.texts: t.update()

    def draw(self, surface):
        for p in self.particles: p.draw(surface)
        for t in self.texts: t.draw(surface)