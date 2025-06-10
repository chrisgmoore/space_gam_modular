import pygame
from game.entities import Ship, Bullet
from game.environment import EnvironmentManager
from game.utils import (generate_random_powerups, victory_screen, draw_grid,
                        draw_tile_coordinates, draw_ammo_bar, circle_rect_collision,
                        check_bullet_collisions)

pygame.init()
screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Spaceman Survivor")
pygame.mixer.init()

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
        if dy != 0:
            new_center = (ship.x, ship.y + dy)
            radius = ship.radius
            if not env.check_collision_circle(new_center, radius):
                ship.move(0, dy)

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
                    enemy_bullets.append(e.fire(target_x, target_y, color=(255,0,0)))
                elif e.shape == "circle":
                    enemy_bullets.extend(e.spread_fire(target_x, target_y, spread_angle=45, num_bullets=5,color = (129, 133, 137)))
                elif e.shape == "triangle":
                    enemy_bullets.extend(e.radial_fire(num_bullets=10, speed=10, color=(255, 0, 255)))
                e.cooldown = 10
            else:
                e.cooldown -= 1
            for b in player_bullets[:]:
                if hasattr(b, "bullet_type") and b.bullet_type == "laser_line":
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
                    if ship.health <= 0:
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
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        screen.blit(pause_text, (
            screen.get_width() // 2 - pause_text.get_width() // 2,
            screen.get_height() // 2 - pause_text.get_height() // 2))
    if not game_started:
        game_started = True
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
