# Utility functions for Space Game
import math
import random
import pygame

class PowerUp:
    def __init__(self, name, description, apply_effect, cost):
        self.name = name
        self.description = description
        self.apply_effect = apply_effect
        self.cost = cost

    def activate(self, ship):
        self.apply_effect(ship)

def victory_screen(screen, powerups, ship, game_state):
    font = pygame.font.SysFont(None, 40)
    selected = None
    while selected is None:
        screen.fill((0, 0, 0))
        title_surf = font.render("Choose a power-up:", True, (255, 255, 255))
        screen.blit(title_surf, (100, 50))
        time_left_sec = game_state["room_timer"] // 60
        bonus_text = f"Time Remaining: {time_left_sec:.1f} seconds"
        bonus_surf = font.render(bonus_text, True, (255, 255, 255))
        screen.blit(bonus_surf, (100, 100))
        for i, pu in enumerate(powerups, start=1):
            text = f"{i}: {pu.name} - {pu.description} (Cost: {pu.cost}s)"
            option_surf = font.render(text, True, (255, 255, 255))
            screen.blit(option_surf, (100, 100 + i * 50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and game_state["room_timer"] >= powerups[0].cost * 60:
                    selected = powerups[0]
                elif event.key == pygame.K_2 and game_state["room_timer"] >= powerups[1].cost * 60:
                    selected = powerups[1]
    game_state["room_timer"] -= selected.cost * 60
    return selected

def add_shield(ship):
    ship.shield.strength = min(ship.shield.strength + 50, ship.shield.max_strength)

def generate_random_powerups():
    powerup_pool = [
        PowerUp("Rapid Fire", "Reduces regular fire cooldown", reduce_regular_cooldown, cost=3),
        PowerUp("Max Health Up", "Increase max health by 50", lambda ship: setattr(ship, "max_health", ship.max_health + 50), cost=4),
        PowerUp("Shield", "Adds 50 shield points", add_shield, cost=4)
    ]
    return random.sample(powerup_pool, 2)

def reduce_regular_cooldown(ship):
    ship.regular_fire_cooldown *= 0.75

def reduce_alt_cooldown(ship):
    ship.alt_fire_cooldown *= 0.75

def draw_tile_coordinates(surface, tile_size=25, font=None, color=(120, 120, 120)):
    if font is None:
        font = pygame.font.SysFont(None, 24)
    cols = surface.get_width() // tile_size
    rows = surface.get_height() // tile_size
    for row in range(rows):
        for col in range(cols):
            text = font.render(f"{col},{row}", True, color)
            surface.blit(text, (col * tile_size + 5, row * tile_size + 5))

def draw_grid(surface, tile_size=25, color=(50, 50, 50)):
    for x in range(0, surface.get_width(), tile_size):
        pygame.draw.line(surface, color, (x, 0), (x, surface.get_height()))
    for y in range(0, surface.get_height(), tile_size):
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))

def check_bullet_collisions(clearing_bullet, other_bullets, remove_self=True):
    if clearing_bullet.bullet_type == "laser_line":
        x1 = clearing_bullet.x
        y1 = clearing_bullet.y
        x2 = x1 + clearing_bullet.laser_dx * clearing_bullet.laser_length
        y2 = y1 + clearing_bullet.laser_dy * clearing_bullet.laser_length
        for b in other_bullets[:]:
            bx, by = b.x, b.y
            dist = line_point_distance(x1, y1, x2, y2, bx, by)
            if dist <= 10:
                other_bullets.remove(b)
        return False
    cb_rect = clearing_bullet.get_rect()
    for b in other_bullets[:]:
        if cb_rect.colliderect(b.get_rect()):
            other_bullets.remove(b)
            if remove_self:
                return True
    return False

def line_point_distance(x1, y1, x2, y2, px, py):
    line_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
    if line_len_sq == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len_sq))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return math.hypot(px - proj_x, py - proj_y)

def circle_rect_collision(circle_center, circle_radius, rect):
    cx, cy = circle_center
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    distance_x = cx - closest_x
    distance_y = cy - closest_y
    distance_squared = (distance_x ** 2) + (distance_y ** 2)
    return distance_squared < (circle_radius ** 2)

def draw_hp_bar(surface, x, y, width, height, health, max_health, color=(255, 0, 0)):
    health = max(0, min(health, max_health))
    ratio = health / max_health
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    pygame.draw.rect(surface, color, (x, y, int(width * ratio), height))

def draw_ammo_bar(surface, x, y, width, height, ammo, max_ammo):
    pygame.draw.rect(surface, (100, 100, 100), (x, y, width, height))
    fill_width = int(width * (ammo / max_ammo))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, fill_width, height))
    pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
