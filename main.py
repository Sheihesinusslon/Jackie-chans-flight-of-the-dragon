import os

import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
ASSETS = "assets"
SOUNDS = "sounds"
WIDTH, HEIGHT = 1280, 960
FPS = 60
INITIAL_OBSTACLE_SPEED = 1
OBSTACLE_GENERATION_INTERVAL = 1000
IS_PAUSED = False
RECORD_NUMBER = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Game screen
icon = pygame.image.load(f"{ASSETS}/icon.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jackie Chan's Flight of the Dragon")
clock = pygame.time.Clock()

# Music
pygame.mixer.music.load(os.path.join(ASSETS, SOUNDS, 'soundtrack.mp3'))
pygame.mixer.music.play(-1,0.0)
menu_sound = pygame.mixer.Sound(os.path.join(ASSETS, SOUNDS, 'menu_sound.mp3'))
win_sound = pygame.mixer.Sound(os.path.join(ASSETS, SOUNDS, 'win.wav'))
lose_sound = pygame.mixer.Sound(os.path.join(ASSETS, SOUNDS, 'lose.wav'))

# Load resources
jackie_sprites = [
    pygame.image.load(f"{ASSETS}/jackie/jackie{i}.png").convert_alpha()
    for i in range(1, 3)
]
bird_sprites_right = [
    pygame.image.load(f"{ASSETS}/bird/bird{i}.png").convert_alpha()
    for i in range(1, 6)
]
bird_sprites_left = [
    pygame.image.load(f"{ASSETS}/bird/bird{i}.png").convert_alpha()
    for i in range(6, 11)
]
balloon_image = pygame.image.load(os.path.join(ASSETS, "baloon.png"))
gas_sprites = [
    pygame.image.load(f"{ASSETS}/gas/gas{i}.png").convert_alpha()
    for i in range(1, 5)
]

# Load background images
main_menu_image_asset = pygame.image.load(os.path.join(ASSETS, "main.jpg"))
main_menu_image = pygame.transform.scale(main_menu_image_asset, (WIDTH, HEIGHT))
lose_menu_image_asset = pygame.image.load(os.path.join(ASSETS, "lose.jpg"))
lose_menu_image = pygame.transform.scale(lose_menu_image_asset, (WIDTH, HEIGHT))
next_round_image_asset = pygame.image.load(os.path.join(ASSETS, "next_round.jpg"))
next_round_image = pygame.transform.scale(next_round_image_asset, (WIDTH, HEIGHT))
sky_image_asset = pygame.image.load(os.path.join(ASSETS, "sky.png"))
sky_image = pygame.transform.scale(sky_image_asset, (WIDTH, HEIGHT))

FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font(None, 30)


def draw_menu(cursor_pos=None):
    """Draws the menu and highlights the option under the cursor."""
    screen.blit(main_menu_image, (0, 0))
    title = FONT.render("Jackie Chan's Flight of the Dragon", True, BLACK)
    play_option = FONT.render("1. Play", True, BLACK)
    task_option = FONT.render("2. Task", True, BLACK)
    exit_option = FONT.render("3. Exit", True, BLACK)

    options = [play_option, task_option, exit_option]
    y_title_position = HEIGHT // 2 - title.get_height()
    y_positions = [y_title_position + 50, y_title_position + 100, y_title_position + 150]

    # Draw title
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - title.get_height()))

    # Draw options with cursor if hovered
    for i, (option, y) in enumerate(zip(options, y_positions)):
        if cursor_pos and y <= cursor_pos[1] <= y + option.get_height():
            # Highlight the option with a cursor (triangle) to the left
            pygame.draw.polygon(screen, BLACK, [(WIDTH // 2 - 100, y + 15),
                                                (WIDTH // 2 - 85, y + 5),
                                                (WIDTH // 2 - 85, y + 25)])
        screen.blit(option, (WIDTH // 2 - option.get_width() // 2, y))

    pygame.display.flip()


def draw_task():
    """Displays the task/rules screen with an option to return to the menu."""
    running = True
    while running:
        screen.blit(main_menu_image, (0, 0))

        # Title and description
        title = FONT.render("Game Task", True, BLACK)
        description1 = FONT.render("1. Use Arrow Keys to Move Jackie Left and Right", True, BLACK)
        description2 = FONT.render("2. Avoid Carbon Dioxide Emissions and Birds on the way", True, BLACK)
        description3 = FONT.render("3. Land Jackie on the Balloon to Win!", True, BLACK)
        back_option = FONT.render("Press ESC to return to the menu", True, BLACK)

        # Display text
        y_title_position = HEIGHT // 2 - title.get_height()
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y_title_position))
        screen.blit(description1, (WIDTH // 2 - description1.get_width() // 2, y_title_position + 100))
        screen.blit(description2, (WIDTH // 2 - description2.get_width() // 2, y_title_position + 150))
        screen.blit(description3, (WIDTH // 2 - description3.get_width() // 2, y_title_position + 200))
        screen.blit(back_option, (WIDTH // 2 - back_option.get_width() // 2, y_title_position + 300))

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_sound.play()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Return to menu
                    menu_sound.play()
                    running = False


def draw_message(text, subtext, screen_image, color=WHITE):
    """Displays a message on the screen and waits for a click to proceed."""
    screen.blit(screen_image, (0, 0))
    message = FONT.render(text, True, color)
    sub_message = FONT.render(subtext, True, color)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 3))
    screen.blit(sub_message, (WIDTH // 2 - sub_message.get_width() // 2, HEIGHT // 3 + 50))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return


# Game logic
def game_loop():
    """Main game loop where Jackie plays through multiple rounds."""
    round_number = 1
    running = True

    while running:
        jackie_x = WIDTH // 2
        jackie_y = 0
        jackie_width, jackie_height = 20, 20
        jackie_fall_speed = 1
        jackie_max_speed = 10
        jackie_vel = 0
        jackie_acc = 0.5
        jackie_fri = 0.1
        jackie_frame = 0
        jackie_animation_speed = 0.2  # Speed at which frames change
        jackie_timer = 0

        balloon_x = WIDTH // 2 - 50
        balloon_y = HEIGHT - 100
        balloon_width, balloon_height = 100, 50
        balloon_speed = 3

        max_obstacles = round_number * 2
        obstacles = []
        birds = []

        while True:
            global IS_PAUSED, RECORD_NUMBER
            screen.blit(sky_image, (0, 0))

            # Display round number
            round_text = FONT.render(f"Round {round_number}", True, BLACK)
            record_text = SMALL_FONT.render(f"Record {RECORD_NUMBER}", True, BLACK) if RECORD_NUMBER else None
            screen.blit(round_text, (WIDTH - round_text.get_width() - 10, 10))
            if record_text:
                screen.blit(record_text, (WIDTH - record_text.get_width() - 12, 50))

            # Create obstacles
            if len(obstacles) <= max_obstacles:
                for i in range(random.randint(0, max_obstacles - len(obstacles))):
                    obstacles.append(create_obstacle(round_number))

            # Create birds
            if round_number >= 3:
                num_birds = round_number // 2
                for i in range(random.randint(0, num_birds - len(birds))):
                    birds.append(create_bird(jackie_y))

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Toggle pause on ESC key
                        if not IS_PAUSED:
                            IS_PAUSED = True
                            menu_sound.play()
                        else:
                            IS_PAUSED = False
                            menu_sound.play()


                    elif IS_PAUSED:
                        IS_PAUSED = False
                        menu_sound.play()

            # If the game is paused
            if IS_PAUSED:
                screenshot = screen.copy()
                screenshot.set_alpha(128)
                screenshot.fill(WHITE)
                screen.blit(screenshot, (0, 0))

                # Display the "Press any key" message
                pause_text = FONT.render("Press any key to continue", True, BLACK)
                text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(pause_text, text_rect)

                pygame.display.flip()
                clock.tick(FPS // 2)
                continue

            # Get keys for horizontal movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and jackie_x > 0:
                # jackie_x -= JACKIE_SPEED
                jackie_vel -= jackie_acc
            if keys[pygame.K_RIGHT] and jackie_x < WIDTH - jackie_width:
                # jackie_x += JACKIE_SPEED
                jackie_vel += jackie_acc

            if not keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                if jackie_vel > 0:
                    jackie_vel -= jackie_fri
                    if jackie_vel < 0:  # Stop completely if too slow
                        jackie_vel = 0
                elif jackie_vel < 0:
                    jackie_vel += jackie_fri
                    if jackie_vel > 0:  # Stop completely if too slow
                        jackie_vel = 0

            # Clamp velocity to max_speed
            jackie_vel= max(-jackie_max_speed, min(jackie_vel, jackie_max_speed))

            # Update Jackie's vertical position
            jackie_y += jackie_fall_speed
            jackie_x += jackie_vel

            if jackie_x > WIDTH - jackie_width:
                jackie_x = WIDTH - jackie_width
            elif jackie_x < 0:
                jackie_x = 0

            # Update Jackie's animation
            jackie_timer += jackie_animation_speed
            if jackie_timer >= 1:
                jackie_timer = 0
                jackie_frame = (jackie_frame + 1) % len(jackie_sprites)  # Loop through frames

            # Balloon movement
            balloon_x += balloon_speed
            if balloon_x <= 0 or balloon_x + balloon_width >= WIDTH:
                balloon_speed *= -1

            # Update obstacle positions
            for obstacle in obstacles:
                obstacle["y"] -= obstacle["speed"]
                if obstacle["y"] + 80 < 0:
                    obstacle["x"] = random.randint(30, WIDTH - 30)
                    obstacle["y"] = random.randint(HEIGHT, HEIGHT * 2)

                # Animate obstacle
                obstacle["timer"] += obstacle["animation_speed"]
                if obstacle["timer"] >= 1:
                    obstacle["timer"] = 0
                    obstacle["frame"] = (obstacle["frame"] + 1) % len(gas_sprites)

            # Update bird positions
            for bird in birds:
                if bird["direction"] == "left":
                    bird["x"] -= bird["speed"]
                    if bird["x"] < -30:
                        bird["x"] = random.randint(WIDTH, WIDTH + WIDTH // 3)
                        bird["y"] = random.randint(50, HEIGHT - 150)
                else:
                    bird["x"] += bird["speed"]
                    if bird["x"] > WIDTH + 30:
                        bird["x"] = random.randint(0 - WIDTH // 3, 0)
                        bird["y"] = random.randint(50, HEIGHT - 150)

                # Update bird animation frame
                bird["timer"] += bird["animation_speed"]
                if bird["timer"] >= 1:
                    bird["timer"] = 0
                    bird["frame"] = (bird["frame"] + 1) % len(bird["sprites"])

            # Check collisions with obstacles
            for obstacle in obstacles:
                if (
                        jackie_x < obstacle["x"] + 40
                        and jackie_x + jackie_width > obstacle["x"]
                        and jackie_y < obstacle["y"] + 40
                        and jackie_y + jackie_height > obstacle["y"]
                ):
                    RECORD_NUMBER = round_number
                    lose_sound.play()
                    draw_message(
                        text="You lost, but Jackie never loses!",
                        subtext="Click to return to the main menu.",
                        screen_image=lose_menu_image,
                    )
                    return

            # Check collisions with birds
            for bird in birds:
                if (
                        jackie_x < bird["x"] + 30
                        and jackie_x + jackie_width > bird["x"]
                        and jackie_y < bird["y"] + 20
                        and jackie_y + jackie_height > bird["y"]
                ):
                    RECORD_NUMBER = round_number
                    lose_sound.play()
                    draw_message(
                        text="You lost, but Jackie never loses!",
                        subtext="Click to return to the main menu.",
                        screen_image=lose_menu_image,
                    )
                    return

            # Check if Jackie lands on the balloon
            if (
                    jackie_y + jackie_height >= balloon_y
                    and jackie_y + jackie_height <= balloon_y + balloon_height
                    and jackie_x + jackie_width > balloon_x
                    and jackie_x < balloon_x + balloon_width
            ):
                win_sound.play()
                draw_message(
                    text="You win!",
                    subtext=f"Get ready for round {round_number + 1}. Press any key to continue.",
                    screen_image=next_round_image,
                )
                round_number += 1
                break

            # Check if Jackie falls below the screen
            if jackie_y > HEIGHT:
                RECORD_NUMBER = round_number
                lose_sound.play()
                draw_message(
                    text="You lost, but Jackie never loses!",
                    subtext="Click to return to the main menu.",
                    screen_image=lose_menu_image,
                )
                return

            # Draw balloon
            screen.blit(balloon_image, (balloon_x, balloon_y))

            # Draw animated obstacles
            for obstacle in obstacles:
                frame = gas_sprites[obstacle["frame"]]
                screen.blit(frame, (obstacle["x"], obstacle["y"]))

            # Draw animated birds
            for bird in birds:
                screen.blit(bird["sprites"][bird["frame"]], (bird["x"], bird["y"]))

            # Draw animated Jackie
            screen.blit(jackie_sprites[jackie_frame], (jackie_x, jackie_y))

            pygame.display.flip()
            clock.tick(FPS)


def main():
    """Main menu loop with mouse interaction."""
    running = True
    y_title_position = HEIGHT // 2
    current_hovered_option = None
    while running:
        cursor_pos = pygame.mouse.get_pos()
        draw_menu(cursor_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_sound.play()
                pygame.quit()
                sys.exit()

            hovered_option = None
            if y_title_position <= cursor_pos[1] <= y_title_position + 50:  # Play option
                hovered_option = "play"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    game_loop()

            elif y_title_position + 70 <= cursor_pos[1] <= y_title_position + 100:  # Task option
                hovered_option = "task"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    draw_task()


            elif y_title_position + 120 <= cursor_pos[1] <= y_title_position + 150:  # Exit option
                hovered_option = "exit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.quit()
                    sys.exit()

            if hovered_option != current_hovered_option:
                current_hovered_option = hovered_option
                if current_hovered_option:
                    menu_sound.play()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    menu_sound.play()
                    game_loop()
                if event.key == pygame.K_2:
                    menu_sound.play()
                    draw_task()
                if event.key == pygame.K_3:
                    menu_sound.play()
                    pygame.quit()
                    sys.exit()


def create_obstacle(round_number):
    return {
        "x": random.randint(30, WIDTH - 30),
        "y": random.randint(HEIGHT, HEIGHT * 2),
        "frame": random.randint(0, 3),  # Start from a random frame
        "timer": 0,
        "animation_speed": 0.1,  # Speed at which frames change
        "speed": INITIAL_OBSTACLE_SPEED + round_number,
        "spawn_time": time.time() + random.uniform(1, 3),
    }


def create_bird(jackie_y):
    bird = {
        "y": random.randint(int(jackie_y + 20), max(jackie_y, HEIGHT)),
        "speed": 4,
        "frame": 0,  # Current animation frame for this bird
        "timer": 0,  # Timer to manage frame changes
        "animation_speed": 0.1,  # Speed for bird animation
        "direction": random.choice(["left", "right"])
    }
    bird["x"] = random.randint(0 - WIDTH // 3, 0) if bird_sprites_right else random.randint(WIDTH, WIDTH + WIDTH // 3)
    bird["sprites"] = bird_sprites_right if bird["direction"] == "right" else bird_sprites_left
    return bird


if __name__ == "__main__":
    main()
