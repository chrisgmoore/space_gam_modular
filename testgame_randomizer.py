import pygame
import math
import random

pygame.init()

DEBUG_DRAW_HITBOXES = True

screen_width = 1920  
screen_height = 1080
tile_size = 25
cols = screen_width // tile_size
rows = screen_height // tile_size

screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Spaceman Survivor")

# ship_image = pygame.image.load("C:/Users/anton/Desktop/spaceship.png").convert_alpha()
pygame.mixer.init()



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
    return(selected)
class Shield:
    def __init__(self, enemy, max_strength, radius=40, strength = 0):
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
class PowerUp:
    def __init__(self, name, description, apply_effect, cost):
        self.name = name
        self.description = description
        self.apply_effect = apply_effect
        self.cost = cost
    def add_shield(ship):
        ship.shield.strength += 50
        ship.shield.strength = min(ship.shield.strength, 100) 
    def reduce_regular_cooldown(ship):
        ship.regular_fire_cooldown *= 0.75  

    def reduce_alt_cooldown(ship):
        ship.alt_fire_cooldown *= 0.75    
    def activate(self, ship):
        self.apply_effect(ship)
    
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
    for x in range(0, screen.get_width(), tile_size):
        pygame.draw.line(surface, color, (x, 0), (x, screen.get_height()))
    for y in range(0, screen.get_height(), tile_size):
        pygame.draw.line(surface, color, (0, y), (screen.get_width(), y))
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
    color = color
def draw_ammo_bar(surface, x, y, width, height, ammo, max_ammo):
    
    pygame.draw.rect(surface, (100, 100, 100), (x, y, width, height))

    
    fill_width = int(width * (ammo / max_ammo))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, fill_width, height))

    
    pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)

class Ship:
    
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
        #  self.image = ship_image
        self.shield = Shield(self,max_strength=50, strength=0)
        self.shield_radius = 30
        self.triangle = [
            (int(25 * scale), int(0 * scale)),    
            (int(0 * scale), int(50 * scale)),    
            (int(50 * scale), int(50 * scale))   
        ]
    

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
    def draw(self, surface,):
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
           
        # rotated_image = pygame.transform.rotate(self.image, -self.angle)
    
   
        # rotated_rect = rotated_image.get_rect(center=(self.x, self.y))
        # pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), 3)
    
        # surface.blit(rotated_image, rotated_rect.topleft)
       
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
    def fire(self, target_x, target_y, color= (0,0,255), speed = 20, clearing = False):
            bullet_x, bullet_y = self.get_tip()  
            bullet = Bullet(bullet_x, bullet_y, target_x, target_y, color= color, speed=speed)

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
    def __init__(self, x, y, shape="square", behavior = None, shield_strength = 10):
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
        self.dash_cooldown  = 0
        self.behavior = behavior 
        if shield_strength > 0:
            print("Shield initialized!")
            self.shield = Shield(self, max_strength=shield_strength, strength=shield_strength)
        else:
            print("No shield.")
            self.shield = None



        if self.shape == "square":
            self.rect = [(0, 0), (0, 30), (30, 30), (30, 0)]
        elif self.shape == "circle":
            self.radius = 15
    def take_damage(self, amount):
        print("Enemy.take_damage called")

        if self.shield is not None:
            print(f"Shield exists with strength: {self.shield.strength}")
        else:
            print("No shield on this enemy")

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
            pygame.draw.polygon(surface, color , points)


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
    def fire(self, target_x, target_y, color= (130, 130, 130)):
        color = color
        center, _ = self.get_hitbox()
        return Bullet(center[0], center[1], target_x, target_y, speed=10, color=(255, 0, 255) if self.shape == "circle" else color, bullet_type="large_rectangle" if self.shape == "circle" else "circle")
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
            return (self.x, self.y), 15  # or whatever fits triangle
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
        sw, sh = screen.get_size()
        return [
            pygame.Rect(0, 0, sw, thickness),  
            pygame.Rect(0, 0, thickness, sh),  
            pygame.Rect(0, sh - thickness, sw, thickness),  
            pygame.Rect(sw - thickness, 0, thickness, sh),  
        ]
    def generate_random_obstacles(self, count = 10, max_attempts = 100):
        obstacles = self.add_wall_border()
        for _ in range(count):
            for _ in range(max_attempts):
                col = random.randint(1, (screen_width // self.tile_size) - 2)
                row = random.randint(1, (screen_height // self.tile_size) - 2)

                new_block = self.add_block(col,row)

                new_rect = pygame.Rect(new_block)

                player_safe_zone = pygame.Rect(
                    self.player_start[0] - 50,
                    self.player_start[1] - 50,
                    100,100
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
            enemies.append(Enemy(600,600, shape = "square", behavior = "stalker"))
            enemies.append(Enemy(300,300, shape = "square", behavior = "stalker" ))

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


env = EnvironmentManager()  

clock = pygame.time.Clock()
ship = Ship(*env.player_start)

enemy_bullets = []
player_bullets = []
player_bullets = [b for b in player_bullets if isinstance(b, Bullet)]
font = pygame.font.SysFont(None, 30) 
victory_shown = False

game_state = {"room_timer": 60*100}
selecting_powerup = False
fire_cooldown = 0
paused = False
font_pause = pygame.font.SysFont(None, 60)

room_count = 0
game_started = False
room_just_advanced = False

env.generate_handcrafted_room("tutorial")
ship = Ship(*env.player_start)

enemies = env.room_enemies

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused
    if not paused:           
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w]:
            dy = -ship.speed
        if keys[pygame.K_s]:
            dy = ship.speed
        if keys[pygame.K_a]:
            dx = -ship.speed
        if keys[pygame.K_d]:
            dx = ship.speed
        if keys[pygame.K_r]:
            if not ship.reloading and ship.ammo_in_clip < ship.clip_size:
                ship.start_reload()


        env.room_enemies = [e for e in env.room_enemies if not e.dead]
      

        if not env.room_enemies and not victory_shown and game_started and not room_just_advanced:
            victory_shown = True
            selecting_powerup = True
            powerup1, powerup2 = generate_random_powerups()
            
            selecting_powerup = False
            
            room_count += 1
            
            if room_count % 3 == 0:
                env.generate_handcrafted_room("megaturret") 
                
            else:
                env.generate_random_room()
        
           
            ship = Ship(*env.player_start)
            enemies = env.room_enemies
            selected = victory_screen(screen, [powerup1, powerup2], ship, game_state)
            selected.activate(ship)
            saved_shield_strength = ship.shield.strength
            room_just_advanced = True
            selecting_powerup = False

        if room_just_advanced and env.room_enemies:
            victory_shown = False
            room_just_advanced = False

        
        screen.fill((0, 0, 0))
        env.draw(screen)
    
        draw_grid(screen, tile_size=25)
        draw_tile_coordinates(screen, tile_size=100)
        ship.rotate_toward_mouse()
        ship.draw(screen)
      
        draw_ammo_bar(screen, 10, 70, 150, 20, ship.ammo_in_clip, ship.clip_size)
        ship.update_reload()  

        for e in env.room_enemies:              
            e.draw(screen)
    
    
        center, radius = ship.get_hitbox()


        if dx != 0:
  
            new_center = (ship.x + dx, ship.y)
            radius = ship.radius  

            if not env.check_collision_circle(new_center, radius):
                ship.move(dx, 0)
            else:
       
                pass


        if dy != 0:
   
            new_center = (ship.x, ship.y + dy)
            radius = ship.radius

            if not env.check_collision_circle(new_center, radius):
                ship.move(0, dy)
            else:
       
                pass

    
    

        if pygame.mouse.get_pressed()[0] and ship.cooldown <= 0:
            mx, my = pygame.mouse.get_pos()
            bullet = ship.regular_fire(mx, my)
            if bullet is not None:
                player_bullets.append(bullet)

        if pygame.mouse.get_pressed()[2] and ship.cooldown <= 0:
            mx, my = pygame.mouse.get_pos()
            bullet = ship.alt_fire(mx, my)
            if bullet is not None:
                player_bullets.append(bullet)
                
        if ship.cooldown > 0:
            ship.cooldown -= 1
        for e in env.room_enemies:
            e.update_behavior(ship.x, ship.y, env)
       
            if e.cooldown <= 0:
                target_x, target_y = ship.get_tip()

                if e.shape == "square":
                    enemy_bullets.append(e.fire(target_x, target_y, color=(255, 0, 0)))

                elif e.shape == "circle":
                    enemy_bullets.extend(e.spread_fire(target_x, target_y, spread_angle=45, num_bullets=5,color = (129, 133, 137)))
            
                elif e.shape == "triangle":
                    enemy_bullets.extend(e.radial_fire(num_bullets=10, speed=10, color=(255, 0, 255)))
                e.cooldown = 10 
            else:
                e.cooldown -= 1


  
            for b in player_bullets[:]:
                if hasattr(b,"bullet_type") and b.bullet_type == "laser_line":
                    check_bullet_collisions(b, enemy_bullets, remove_self=False)
                    if getattr(b, "duration") <= 0:
                        player_bullets.remove(b)
            for b in player_bullets[:]:
                if hasattr(b, "color") and b.color == (0, 0, 255):  
                    for e in env.room_enemies[:]:      
                        if b.get_rect().colliderect(e.get_rect()):
                            e.take_damage(10)
                            player_bullets.remove(b)
                            if e.health <= 0:
                                e.dead = True
                                env.room_enemies.remove(e)
                            break
            center, radius = ship.get_hitbox()
            for b in enemy_bullets[:]:
                if circle_rect_collision(center, radius, b.get_rect()):
                
                    ship.take_damage(10)
               
                    enemy_bullets.remove(b)
                    if ship.health <=0:
                        ship.dead = True
               
        for b in enemy_bullets[:]:
            b.move()
            if env.check_collision_rect(pygame.Rect(b.x - 2, b.y - 2, 5, 5)):
                enemy_bullets.remove(b)
                continue
            if not screen.get_rect().collidepoint(b.x, b.y):
                enemy_bullets.remove(b)
                continue
            b.draw(screen)
        for b in player_bullets[:]:
            b.move()
            if env.check_collision_rect(pygame.Rect(b.x - 2, b.y - 2, 5, 5)):
                player_bullets.remove(b)
            b.draw(screen) 
       

        if ship.reloading:
            reload_text = font.render(f"Reloading...", True, (255, 255, 0))
            screen.blit(reload_text, (10, 100))
   
        if ship.dead:
            print("Player died!")
            running = False 


        if not ship.dead and len(env.room_enemies) > 0 and not selecting_powerup:
            game_state["room_timer"] -= 1

        seconds_left = max(game_state["room_timer"] // 60, 0)
        timer_text = font.render(f"Time: {seconds_left}s", True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))

        enemy_count_text = font.render(f"Enemies Left: {len(env.room_enemies)}", True, (255, 100, 100))
        screen.blit(enemy_count_text, (10, 40))

        
        room_number = font.render(f"Room: {room_count}", True, (255, 100, 100))
        screen.blit(room_number, (1800,10))
    else:
        
        pause_text = font_pause.render("PAUSED", True, (255, 255, 255))
        ship.draw(screen)
        env.draw(screen)
        for e in env.room_enemies:              
            e.draw(screen)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # RGBA: 150 alpha for transparency
        screen.blit(overlay, (0, 0))
        screen.blit(pause_text, (
            screen.get_width() // 2 - pause_text.get_width() // 2,
            screen.get_height() // 2 - pause_text.get_height() // 2))
        
    if not game_started:
        game_started = True
    pygame.display.flip()
    clock.tick(60)
     

    
    
    
pygame.quit()