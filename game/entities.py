# Entities module for Space Game
import math
import pygame
from .utils import draw_hp_bar

DEBUG_DRAW_HITBOXES = True

class Shield:
    def __init__(self, enemy, max_strength, radius=40, strength=0):
        self.strength = strength
        self.max_strength = max_strength
        self.radius = radius
        self.enemy = enemy

    def take_damage(self, amount):
        absorbed = min(amount, self.strength)
        self.strength -= absorbed
        return amount - absorbed

    def draw(self, surface, center):
        if self.strength > 0:
            pygame.draw.circle(surface, (0, 120, 255), (int(center[0])-2, int(center[1])), self.radius, width=3)

    def recharge(self, rate=0.1):
        self.strength = min(self.max_strength, self.strength + rate)

class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.angle = 5
        self.radius = 10
        scale = 0.5
        self.health = 100
        self.max_health = 100
        self.dead = False
        self.cooldown = 0
        self.regular_fire_cooldown = 5
        self.alt_fire_cooldown = 3
        self.clip_size = 50
        self.ammo_in_clip = self.clip_size
        self.reloading = False
        self.reload_time = 120
        self.reload_timer = 0
        self.shield = Shield(self, max_strength=50, strength=0)
        self.shield_radius = 30
        self.triangle = [
            (int(25 * scale), int(0 * scale)),
            (int(0 * scale), int(50 * scale)),
            (int(50 * scale), int(50 * scale))
        ]

    def take_damage(self, amount):
        if self.shield is not None:
            amount = self.shield.take_damage(amount)
        self.health -= amount
        self.health = max(0, self.health)

    def get_hitbox(self):
        x1, y1 = self.triangle[0]
        x2, y2 = self.triangle[1]
        x3, y3 = self.triangle[2]
        cx_local = (x1 + x2 + x3) / 3
        cy_local = (y1 + y2 + y3) / 3
        pivot_x, pivot_y = 0, 25
        tx = cx_local - pivot_x
        ty = cy_local - pivot_y
        radians = math.radians(self.angle)
        rx = tx * math.cos(radians) - ty * math.sin(radians)
        ry = tx * math.sin(radians) + ty * math.cos(radians)
        world_x = rx + self.x
        world_y = ry + self.y
        return (world_x, world_y), self.radius

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def get_tip(self):
        tip_x, tip_y = self.triangle[0]
        radians = math.radians(self.angle)
        tx = tip_x - 0
        ty = tip_y - 20
        rx = tx * math.cos(radians) - ty * math.sin(radians)
        ry = tx * math.sin(radians) + ty * math.cos(radians)
        world_x = rx + self.x
        world_y = ry + self.y
        return (world_x, world_y)

    def draw(self, surface):
        rotated = []
        radians = math.radians(self.angle)
        rotation_origin_x = 0
        rotation_origin_y = 25
        for px, py in self.triangle:
            tx = px - rotation_origin_x
            ty = py - rotation_origin_y
            rx = tx * math.cos(radians) - ty * math.sin(radians)
            ry = tx * math.sin(radians) + ty * math.cos(radians)
            rotated.append((rx + self.x, ry + self.y))
        pygame.draw.polygon(surface, (255, 150, 100), rotated)
        draw_hp_bar(surface, 10, 90, 100, 20, self.health, self.max_health, color=(255,0,0))
        center, _ = self.get_hitbox()
        if self.shield and self.shield.strength > 0:
            self.shield.draw(surface, center)
        if DEBUG_DRAW_HITBOXES:
            center, radius = self.get_hitbox()
            pygame.draw.circle(surface, (0, 255, 0), (int(center[0]), int(center[1])), radius, 1)

    def rotate_toward_mouse(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        self.angle = +math.degrees(math.atan2(dy, dx)) + 90

    def fire(self, target_x, target_y, color=(0,0,255), speed=20, clearing=False):
        bullet_x, bullet_y = self.get_tip()
        bullet = Bullet(bullet_x, bullet_y, target_x, target_y, color=color, speed=speed)
        bullet.is_clearing = clearing
        return bullet

    def regular_fire(self, target_x, target_y):
        if self.reloading:
            return None
        if self.ammo_in_clip <= 0:
            self.start_reload()
            return None
        bullet = self.fire(target_x, target_y, color=(0, 0, 255), speed=20, clearing=False)
        self.ammo_in_clip -= 1
        self.cooldown = self.regular_fire_cooldown
        if self.ammo_in_clip == 0:
            self.start_reload()
        return bullet

    def alt_fire(self, target_x, target_y):
        if self.reloading:
            return None
        if self.ammo_in_clip <= 0:
            self.start_reload()
            return None
        tip_x, tip_y = self.get_tip()
        bullet = Bullet(tip_x, tip_y, target_x, target_y, speed=0,
                        color=(255, 80, 0), bullet_type="laser_line")
        self.ammo_in_clip -= 1
        self.cooldown = self.alt_fire_cooldown
        if self.ammo_in_clip == 0:
            self.start_reload()
        return bullet

    def start_reload(self):
        self.reloading = True
        self.reload_timer = self.reload_time

    def update_reload(self):
        if self.reloading:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.reloading = False
                self.ammo_in_clip = self.clip_size

class Enemy:
    def __init__(self, x, y, shape="square", behavior=None, shield_strength=10):
        self.x = x
        self.y = y
        self.shape = shape
        self.health = 100
        self.max_health = 100
        self.cooldown = 0
        self.radial_offset = 0
        self.dead = False
        self.dashing = False
        self.dash_timer = 0
        self.dash_vector = (0, 0)
        self.dash_cooldown = 0
        self.behavior = behavior
        if shield_strength > 0:
            self.shield = Shield(self, max_strength=shield_strength, strength=shield_strength)
        else:
            self.shield = None
        if self.shape == "square":
            self.rect = [(0, 0), (0, 30), (30, 30), (30, 0)]
        elif self.shape == "circle":
            self.radius = 15

    def take_damage(self, amount):
        if self.shield is not None and self.shield.strength > 0:
            amount = self.shield.take_damage(amount)
        self.health -= amount

    def auto_behavior(self):
        if self.shape == "circle":
            return "dasher"
        elif self.shape == "square":
            return "stalker"
        else:
            return "shooter"

    def draw(self, surface):
        color = (255,0,0)
        if self.behavior == "dasher" and self.dash_cooldown <= 10:
            color = (255, 255, 0)
        elif self.behavior == "stalker":
            color = (200, 50, 50)
        if self.shape == "square":
            points = [(px + self.x, py + self.y) for (px, py) in self.rect]
            pygame.draw.polygon(surface, color, points)
        elif self.shape == "circle":
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        elif self.shape == "triangle":
            points = [
                (self.x, self.y - 15),
                (self.x - 15, self.y + 15),
                (self.x + 15, self.y + 15)
            ]
            pygame.draw.polygon(surface, color, points)
        center, _ = self.get_hitbox()
        if self.shield and self.shield.strength > 0:
            self.shield.draw(surface, center)
        draw_hp_bar(surface, self.x - 20, self.y - 30, 40, 5, self.health, self.max_health)
        center, radius = self.get_hitbox()
        pygame.draw.circle(surface, (0, 255, 0), (int(center[0]), int(center[1])), radius, 1)

    def move_toward(self, target_x, target_y, env, speed=1):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        move_x = (dx / distance) * speed
        move_y = (dy / distance) * speed
        if not env.check_collision_rect(pygame.Rect(self.x + move_x - 5, self.y - 5, 10, 10)):
            self.x += move_x
        if not env.check_collision_rect(pygame.Rect(self.x - 5, self.y + move_y - 5, 10, 10)):
            self.y += move_y

    def update_behavior(self, target_x, target_y, env):
        if self.behavior == "dasher":
            if self.dashing:
                self.x += self.dash_vector[0] * 10
                self.y += self.dash_vector[1] * 10
                self.dash_timer -= 1
                if self.dash_timer <= 0:
                    self.dashing = False
                    self.dash_cooldown = 90
            else:
                if self.dash_cooldown <= 0:
                    dx = target_x - self.x
                    dy = target_y - self.y
                    distance = math.hypot(dx, dy)
                    if distance != 0:
                        self.dash_vector = (dx / distance, dy / distance)
                        self.dash_timer = 10
                        self.dashing = True
                else:
                    self.dash_cooldown -= 1
        elif self.behavior == "stalker":
            self.move_toward(target_x, target_y, env, speed=2)
        elif self.behavior == "shooter":
            if self.shape == "circle":
                self.move_toward(target_x, target_y, env, speed=0.8)

    def move(self):
        pass

    def fire(self, target_x, target_y, color=(130, 130, 130)):
        center, _ = self.get_hitbox()
        return Bullet(center[0], center[1], target_x, target_y, speed=10,
                      color=(255, 0, 255) if self.shape == "circle" else color,
                      bullet_type="large_rectangle" if self.shape == "circle" else "circle")

    def spread_fire(self, target_x, target_y, num_bullets=5, spread_angle=30, speed=5, color=(255, 165, 0)):
        bullets = []
        center, _ = self.get_hitbox()
        base_angle = math.atan2(target_y - center[1], target_x - center[0])
        half_spread = math.radians(spread_angle) / 2
        for i in range(num_bullets):
            angle = base_angle - half_spread + (i / (num_bullets - 1)) * math.radians(spread_angle)
            dx = math.cos(angle) * 100
            dy = math.sin(angle) * 100
            bullets.append(Bullet(center[0], center[1], center[0] + dx, center[1] + dy, speed, color=(170, 140, 40), bullet_type="large_rectangle"))
        return bullets

    def predictive_fire(self, target_x, target_y, target_dx, target_dy, speed):
        center, _ = self.get_hitbox()
        predicted_x = target_x + target_dx * 10
        predicted_y = target_y + target_dy * 10
        return Bullet(center[0], center[1], predicted_x, predicted_y, speed, color=(255, 0, 255))

    def radial_fire(self, num_bullets=10, speed=10, color=(255, 100, 0)):
        bullets = []
        center, _ = self.get_hitbox()
        for i in range(num_bullets):
            angle = 2 * math.pi * i / num_bullets
            dx = math.cos(angle) * 50
            dy = math.sin(angle) * 50
            bullets.append(Bullet(center[0], center[1], center[0] + dx, center[1] + dy, speed, color=color))
        return bullets

    def get_rect(self):
        if self.shape == "square":
            return pygame.Rect(self.x + 3, self.y + 3, 24, 24)
        elif self.shape == "circle":
            return pygame.Rect(self.x - 13, self.y - 13, 26, 26)
        elif self.shape == "triangle":
            return pygame.Rect(self.x - 12, self.y - 10, 24, 26)
        else:
            return pygame.Rect(self.x, self.y, 12, 12)

    def get_hitbox(self):
        if self.shape == "circle":
            return (self.x, self.y), self.radius
        elif self.shape == "square":
            return (self.x + 15, self.y + 15), 15
        elif self.shape == "triangle":
            return (self.x, self.y), 15
        else:
            return (self.x, self.y), 10

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed, color=(255, 0, 0), bullet_type="circle"):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.bullet_type = bullet_type
        if self.bullet_type == "laser_line":
            self.duration = 5
            self.laser_length = 2000
            angle = math.atan2(target_y - y, target_x - x)
            self.laser_dx = math.cos(angle)
            self.laser_dy = math.sin(angle)
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1
        self.dx = (dx / distance) * speed
        self.dy = (dy / distance) * speed
        if self.bullet_type == "circle":
            self.radius = 5
        elif self.bullet_type == "large_rectangle":
            self.width = 10
            self.height = 5

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.bullet_type == "laser_line":
            self.duration -= 1

    def draw(self, surface):
        if self.bullet_type == "circle":
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        elif self.bullet_type == "large_rectangle":
            rect = pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)
            pygame.draw.rect(surface, self.color, rect)
        elif self.bullet_type == "laser_line":
            end_x = self.x + self.laser_dx * self.laser_length
            end_y = self.y + self.laser_dy * self.laser_length
            pygame.draw.line(surface, (255, 80, 0), (self.x, self.y), (end_x, end_y), 6)

    def get_rect(self):
        if self.bullet_type == "circle":
            return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)
        elif self.bullet_type == "large_rectangle":
            return pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height / 2), self.width, self.height)
        elif self.bullet_type == "laser_line":
            end_x = self.x + self.laser_dx * self.laser_length
            end_y = self.y + self.laser_dy * self.laser_length
            min_x = min(self.x, end_x)
            min_y = min(self.y, end_y)
            width = max(abs(end_x - self.x), 1)
            height = max(abs(end_y - self.y), 1)
            return pygame.Rect(min_x, min_y, width, height)
