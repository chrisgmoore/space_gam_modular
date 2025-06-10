# Environment management for Space Game
import math
import random
import pygame
from .entities import Enemy

screen_width = 1920
screen_height = 1080

class EnvironmentManager:
    def __init__(self):
        self.tile_size = 100
        self.current_room = {"obstacles": []}
        self.rooms = {}
        self.player_start = (50, 1025)
        self.room_enemies = []
        self.generate_random_room()

    def add_block(self, col, row, w_tiles=1, h_tiles=1):
        return pygame.Rect(
            col * self.tile_size,
            row * self.tile_size,
            w_tiles * self.tile_size,
            h_tiles * self.tile_size
        )

    def add_wall_border(self, thickness=10):
        sw, sh = pygame.display.get_surface().get_size()
        return [
            pygame.Rect(0, 0, sw, thickness),
            pygame.Rect(0, 0, thickness, sh),
            pygame.Rect(0, sh - thickness, sw, thickness),
            pygame.Rect(sw - thickness, 0, thickness, sh),
        ]

    def generate_random_obstacles(self, count=10, max_attempts=100):
        obstacles = self.add_wall_border()
        for _ in range(count):
            for _ in range(max_attempts):
                col = random.randint(1, (screen_width // self.tile_size) - 2)
                row = random.randint(1, (screen_height // self.tile_size) - 2)
                new_block = self.add_block(col, row)
                new_rect = pygame.Rect(new_block)
                player_safe_zone = pygame.Rect(
                    self.player_start[0] - 50,
                    self.player_start[1] - 50,
                    100, 100
                )
                if (not new_rect.colliderect(player_safe_zone) and
                        not any(new_rect.colliderect(o) for o in obstacles)):
                    obstacles.append(new_rect)
                    break
        return obstacles

    def generate_random_enemies(self, count=5):
        enemy_list = []
        for _ in range(count):
            for _ in range(100):
                x = random.randint(100, screen_width - 100)
                y = random.randint(100, screen_height - 100)
                dist_to_player = math.hypot(x - self.player_start[0], y - self.player_start[1])
                if dist_to_player < 300:
                    continue
                enemy_types = [
                    ("circle", "dasher"),
                    ("square", "stalker"),
                    ("triangle", "shooter")
                ]
                shape, behavior = random.choice(enemy_types)
                shield_strength = 50 if random.random() < 0.3 else 0
                e = Enemy(x, y, shape=shape, behavior=behavior, shield_strength=shield_strength)
                if not any(e.get_rect().colliderect(o) for o in self.current_room["obstacles"]):
                    enemy_list.append(e)
                    break
        return enemy_list

    def generate_random_room(self):
        self.current_room["obstacles"] = self.generate_random_obstacles()
        self.room_enemies = self.generate_random_enemies()

    def draw(self, screen):
        screen.fill((15, 20, 30))
        for obstacle in self.current_room["obstacles"]:
            pygame.draw.rect(screen, (63,63,63), obstacle)

    def generate_handcrafted_room(self, room_id):
        obstacles = self.add_wall_border()
        enemies = []
        if room_id == "tutorial":
            obstacles.append(self.add_block(4,4))
            obstacles.append(self.add_block(8,8))
            enemies.append(Enemy(600,600, shape="square", behavior="stalker"))
            enemies.append(Enemy(300,300, shape="square", behavior="stalker" ))
        elif room_id == "megaturret":
            obstacles += [self.add_block(4 + i, 8) for i in range(10)]
            enemies.append(Enemy(900, 500, shape="triangle", behavior="shooter"))
            enemies.append(Enemy(950, 550, shape="circle", behavior="dasher"))
            enemies.append(Enemy(850, 550, shape="circle", behavior="dasher"))
        self.current_room["obstacles"] = obstacles
        self.room_enemies = enemies

    def check_collision_rect(self, rect):
        return any(rect.colliderect(o) for o in self.current_room["obstacles"])

    def check_collision_circle(self, center, radius):
        cx, cy = center
        for o in self.current_room["obstacles"]:
            if isinstance(o, pygame.Rect):
                closest_x = max(o.left, min(cx, o.right))
                closest_y = max(o.top, min(cy, o.bottom))
                dist_x = cx - closest_x
                dist_y = cy - closest_y
                if (dist_x ** 2 + dist_y ** 2) < (radius ** 2):
                    return True
        return False
