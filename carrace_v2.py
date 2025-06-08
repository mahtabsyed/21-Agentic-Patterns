# This Python program implements the following use case:
# Write code to create a simple car race game with my car and many other moving cars on different lanes like a real race. Use Pygame library for this. The game should have a simple GUI, a scoreboard with time remaining and lives remaining, and should handle edge cases like collisions and out of bounds. The road should be a simple straight road with lanes, and the player car should be controlled by arrow keys. The game should end when the player runs out of lives or time.

import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
LANE_WIDTH = WIDTH // 4
CAR_WIDTH, CAR_HEIGHT = 50, 100
FPS = 60
GAME_TIME = 60
LIVES = 3

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Race Game")

font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 48)  # Larger font for car numbers

player_car = pygame.Rect(WIDTH // 2 - CAR_WIDTH // 2, HEIGHT - CAR_HEIGHT - 10, CAR_WIDTH, CAR_HEIGHT)
enemy_cars = []  # Now stores dicts: {'rect': pygame.Rect, 'speed': int, 'lane': int, 'number': int}

clock = pygame.time.Clock()

# Load sounds
move_sound = pygame.mixer.Sound("move.wav")
crash_sound = pygame.mixer.Sound("crash.wav")

# Add billboard positions and speed
BILLBOARD_WIDTH = 16
BILLBOARD_HEIGHT = 80
billboard_img = pygame.Surface((BILLBOARD_WIDTH, BILLBOARD_HEIGHT))
billboard_img.fill((200, 200, 0))
billboards = [
    # Leftmost edge of left track
    {'x': 0, 'y': 0},
    {'x': 0, 'y': HEIGHT // 3},
    {'x': 0, 'y': 2 * HEIGHT // 3},
    {'x': 0, 'y': HEIGHT // 2},
    {'x': 0, 'y': HEIGHT // 5},
    {'x': 0, 'y': HEIGHT // 5 * 4},
    # Rightmost edge of right track
    {'x': WIDTH - BILLBOARD_WIDTH, 'y': HEIGHT // 6},
    {'x': WIDTH - BILLBOARD_WIDTH, 'y': HEIGHT // 2},
    {'x': WIDTH - BILLBOARD_WIDTH, 'y': HEIGHT // 3},
    {'x': WIDTH - BILLBOARD_WIDTH, 'y': HEIGHT // 5 * 3},
    {'x': WIDTH - BILLBOARD_WIDTH, 'y': HEIGHT // 5},
    {'x': WIDTH - BILLBOARD_WIDTH, 'y': HEIGHT // 5 * 4},
]

def draw_road():
    screen.fill((50, 50, 50))
    for i in range(1, 4):
        pygame.draw.line(screen, (255, 255, 255), (i * LANE_WIDTH, 0), (i * LANE_WIDTH, HEIGHT), 5)
    # Draw billboards
    for bb in billboards:
        screen.blit(billboard_img, (bb['x'], bb['y']))

def draw_car(car, color, number=None):
    # Draw car body
    pygame.draw.rect(screen, color, car, border_radius=10)
    # Draw windows (front and rear)
    window_color = (200, 255, 255)
    window_rect = pygame.Rect(car.x + 10, car.y + 15, car.width - 20, 25)
    pygame.draw.rect(screen, window_color, window_rect, border_radius=6)
    rear_window_rect = pygame.Rect(car.x + 10, car.y + car.height - 40, car.width - 20, 20)
    pygame.draw.rect(screen, window_color, rear_window_rect, border_radius=6)
    # Draw wheels
    wheel_color = (30, 30, 30)
    wheel_radius = 10
    # Front wheels
    pygame.draw.circle(screen, wheel_color, (car.x + 12, car.y + 18), wheel_radius)
    pygame.draw.circle(screen, wheel_color, (car.x + car.width - 12, car.y + 18), wheel_radius)
    # Rear wheels
    pygame.draw.circle(screen, wheel_color, (car.x + 12, car.y + car.height - 18), wheel_radius)
    pygame.draw.circle(screen, wheel_color, (car.x + car.width - 12, car.y + car.height - 18), wheel_radius)
    # Draw a simple roof stripe
    stripe_color = (255, 255, 255)
    stripe_rect = pygame.Rect(car.x + car.width // 2 - 5, car.y + 30, 10, car.height - 60)
    pygame.draw.rect(screen, stripe_color, stripe_rect, border_radius=3)
    # Draw car number if provided, centered vertically and horizontally
    if number is not None:
        num_text = large_font.render(str(number), True, (0, 0, 0))
        center_x = car.x + car.width // 2 - num_text.get_width() // 2
        center_y = car.y + car.height // 2 - num_text.get_height() // 2
        screen.blit(num_text, (center_x, center_y))

def draw_scoreboard(time_remaining, lives_remaining):
    time_text = font.render(f"Time: {time_remaining}s", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives_remaining}", True, (255, 255, 255))
    screen.blit(time_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 150, 10))

def move_enemies():
    # Move cars and remove if out of bounds
    for car in enemy_cars[:]:
        car['rect'].y += car['speed']
        if car['rect'].y > HEIGHT:
            enemy_cars.remove(car)
    # Check for enemy-enemy collisions and remove both if they collide
    for i in range(len(enemy_cars)):
        for j in range(i + 1, len(enemy_cars)):
            if enemy_cars[i]['rect'].colliderect(enemy_cars[j]['rect']):
                # Remove both cars if they collide
                if enemy_cars[i] in enemy_cars:
                    enemy_cars.remove(enemy_cars[i])
                if enemy_cars[j] in enemy_cars:
                    enemy_cars.remove(enemy_cars[j])
                break  # Restart loop as list changed

def check_collisions():
    for car in enemy_cars:
        if player_car.colliderect(car['rect']):
            return True
    return False

def spawn_enemy():
    # Decrease spawn rate: spawn only if random number is 1 out of 40
    if random.randint(1, 40) == 1:
        lane = random.choice([0, 1, 2, 3])
        # Only spawn if no car is in this lane
        lane_occupied = any(car['lane'] == lane for car in enemy_cars)
        if not lane_occupied:
            enemy_rect = pygame.Rect(lane * LANE_WIDTH + (LANE_WIDTH - CAR_WIDTH) // 2, -CAR_HEIGHT, CAR_WIDTH, CAR_HEIGHT)
            speed = random.randint(4, 10)
            car_number = len(enemy_cars) + 1
            # Prevent overlap at spawn (shouldn't happen due to lane check, but extra safety)
            if not any(enemy_rect.colliderect(c['rect']) for c in enemy_cars):
                enemy_cars.append({'rect': enemy_rect, 'speed': speed, 'lane': lane, 'number': car_number})

def move_billboards(accel_speed):
    for bb in billboards:
        bb['y'] += accel_speed
        if bb['y'] > HEIGHT:
            bb['y'] = -BILLBOARD_HEIGHT
            # Keep x at leftmost or rightmost edge

def handle_input():
    keys = pygame.key.get_pressed()
    moving = False
    global car_speed, accelerating
    accelerating = False
    if keys[pygame.K_LEFT] and player_car.x > 0:
        player_car.x -= 5
        moving = True
    if keys[pygame.K_RIGHT] and player_car.x < WIDTH - CAR_WIDTH:
        player_car.x += 5
        moving = True
    if keys[pygame.K_UP]:
        accelerating = True
        moving = True
    # Play move sound only if moving and not already playing
    if moving or accelerating:
        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(move_sound, loops=-1)
    else:
        pygame.mixer.Channel(1).stop()

def game_over_screen():
    screen.fill((0, 0, 0))
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)

# Add car speed and acceleration
car_speed = 5
accelerating = False

def main():
    global car_speed, accelerating
    running = True
    lives_remaining = LIVES
    start_ticks = pygame.time.get_ticks()

    while running:
        clock.tick(FPS)
        draw_road()

        time_remaining = GAME_TIME - (pygame.time.get_ticks() - start_ticks) // 1000
        if time_remaining <= 0:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        handle_input()

        # Accelerate if UP is pressed, else slow down
        if accelerating:
            car_speed = min(car_speed + 0.2, 18)
        else:
            car_speed = max(car_speed - 0.15, 5)

        move_billboards(car_speed)
        spawn_enemy()
        move_enemies()

        if check_collisions():
            pygame.mixer.Channel(2).play(crash_sound)
            lives_remaining -= 1
            if lives_remaining <= 0:
                running = False
            else:
                player_car.x = WIDTH // 2 - CAR_WIDTH // 2
                player_car.y = HEIGHT - CAR_HEIGHT - 10
                enemy_cars.clear()
                car_speed = 5

        draw_car(player_car, (0, 255, 0), "P")
        for car in enemy_cars:
            draw_car(car['rect'], (255, 0, 0), car['number'])

        draw_scoreboard(time_remaining, lives_remaining)
        pygame.display.flip()

    game_over_screen()
    pygame.time.wait(500)
    pygame.quit()

if __name__ == "__main__":
    main()