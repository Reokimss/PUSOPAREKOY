import math
import random

import pygame

GRID = 12            
FPS = 60
FLIGHT = 150        
FADE_IN = 90         
LEVELS = 8           
SIZES = [12, 14, 16, 18, 20]

PALETTE = [
    (255, 0, 0),       
    (255, 255, 255),   
    (150, 70, 230),    
]
WEIGHTS = [10, 2, 2]    
BACKGROUND = (8, 0, 16)  


def rand(a, b):
    return random.uniform(a, b)


def heart_curve(n):
    pts = []
    for s in range(n):
        t = s / n * math.tau
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x, y))
    return pts


UNIT = heart_curve(40)
BIG = heart_curve(140)


class Angle:

    def __init__(self, a):
        self.a = a
        self.rad = math.radians(a)

    def inc_dec(self, num):
        self.a += num
        self.rad = math.radians(self.a)


_sprites = {}


def glow_sprite(color_idx, size, level):
    key = (color_idx, size, level)
    s = _sprites.get(key)
    if s is not None:
        return s
    base = PALETTE[color_idx]
    hot = (255, 0, 0) if color_idx == 0 else tuple(min(255, c + 90) for c in base)    # brighter centre
    s = pygame.Surface((size, size))
    s.fill((0, 0, 0))
    c = size / 2
    k = (size / 2) / 17.0
    steps = 6
    for st in range(steps):
        f = 1 - st / steps
        m = st / (steps - 1)
        col = tuple(int(min(255, (base[i] * 0.5 * (1 - m) + hot[i] * m) * level / LEVELS)) for i in range(3))
        pygame.draw.polygon(s, col, [(c + x * k * f, c + (y - 2.5) * k * f) for x, y in UNIT])
    _sprites[key] = s
    return s


class Heart:
    def __init__(self, x, y, index):
        self.x = self.xi = x
        self.y = self.yi = y
        self.i = index * 0.5 + 200          
        self.l = self.i
        self.color_idx = random.choices(range(len(PALETTE)), weights=WEIGHTS)[0]
        self.size = random.choice(SIZES)
        self.a = Angle(rand(0, 360))
        self.vx, self.vy = random.random(), -random.random()
        self.ga = random.random()
        self.ox = self.oy = 0.0              
        self.fly = 0
        self.fade = 0

    def reset(self):
        self.x, self.y = self.xi, self.yi
        self.i = self.l
        self.fly = 0
        self.fade = 0
        self.ox = self.oy = 0.0

    @property
    def done(self):
        return self.fly >= FLIGHT

    def update(self, mouse):
        self.a.inc_dec(2)
        if self.fade < FADE_IN:
            self.fade += 1
        if self.i > 0:
            self.i -= 1
        elif self.fly < FLIGHT:
            speed = 2.2 + self.fly * 0.025
            self.x += self.vx * speed + math.sin(self.a.rad) * 0.25
            self.y += self.vy * speed + math.cos(self.a.rad) * 0.25
            self.fly += 1

        if mouse is not None:
            dx, dy = self.x - mouse[0], self.y - mouse[1]
            d = math.hypot(dx, dy)
            if 0 < d < 90:
                push = (1 - d / 90) * 6
                self.ox += dx / d * push
                self.oy += dy / d * push
        self.ox *= 0.92
        self.oy *= 0.92

    def render(self, screen, t):
        shimmer = 0.6 + 0.4 * math.sin(t * 0.05 + self.a.rad)
        b = (0.35 + 0.65 * self.ga) * shimmer * 0.85
        b *= min(1.0, self.fade / FADE_IN) * (1 - self.fly / FLIGHT)
        if b < 0.06:
            return
        level = max(1, min(LEVELS, int(b * LEVELS) + 1))
        img = glow_sprite(self.color_idx, self.size, level)
        wobble = 0 if self.i <= 0 else 1.5
        px = self.x + self.ox + math.cos(self.a.rad) * wobble - self.size / 2
        py = self.y + self.oy + math.sin(self.a.rad) * wobble - self.size / 2
        screen.blit(img, (px, py), special_flags=pygame.BLEND_RGB_ADD)


def build(width, height):
    heart_size = 180 if width < 768 else 250
    k = heart_size / 19.0
    cx, cy = width / 2, height / 2.3
    mask = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), [(cx + x * k, cy + (y - 2.5) * k) for x, y in BIG])
    hearts = []
    index = 0
    for y in range(0, height, GRID):
        for x in range(0, width, GRID):
            if mask.get_at((x, y)).a > 0:
                index += 1
                hearts.append(Heart(x + rand(-3, 3), y + rand(-3, 3), index))
    return hearts


def main():
    pygame.init()
    size = (1000, 720)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption("Heart of hearts")
    clock = pygame.time.Clock()
    hearts = build(*size)
    t = 0

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
            elif e.type == pygame.VIDEORESIZE:        
                size = (max(200, e.w), max(200, e.h))
                screen = pygame.display.set_mode(size, pygame.RESIZABLE)
                hearts = build(*size)

        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else None

        screen.fill(BACKGROUND)
        for h in hearts:
            h.update(mouse)
            h.render(screen, t)

        if hearts and all(h.done for h in hearts):      
            for h in hearts:
                h.reset()

        t += 1
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()