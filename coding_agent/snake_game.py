
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BLOCK_SIZE = 20
SNAKE_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

def draw_grid():
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH, y))

def show_score(score):
    font = pygame.font.Font(None, 35)
    score_surface = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surface, (10, 10))

def game_over_screen(score):
    screen.fill(WHITE)
    font_large = pygame.font.Font(None, 70)
    font_small = pygame.font.Font(None, 35)

    title_surface = font_large.render("Game Over", True, RED)
    score_surface = font_small.render(f"Final Score: {score}", True, BLACK)
    restart_surface = font_small.render("Press R to Restart or Q to Quit", True, BLACK)

    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))

    screen.blit(title_surface, title_rect)
    screen.blit(score_surface, score_rect)
    screen.blit(restart_surface, restart_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    return # Restart the game

def main():
    snake_x = SCREEN_WIDTH // 2
    snake_y = SCREEN_HEIGHT // 2
    snake_body = [(snake_x, snake_y), (snake_x - BLOCK_SIZE, snake_y), (snake_x - 2 * BLOCK_SIZE, snake_y)]
    direction = "RIGHT"
    change_to = direction

    food_x = random.randrange(0, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE
    food_y = random.randrange(0, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE

    score = 0
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    change_to = "UP"
                if event.key == pygame.K_DOWN and direction != "UP":
                    change_to = "DOWN"
                if event.key == pygame.K_LEFT and direction != "RIGHT":
                    change_to = "LEFT"
                if event.key == pygame.K_RIGHT and direction != "LEFT":
                    change_to = "RIGHT"

        # Update direction
        direction = change_to

        # Move snake
        if direction == "UP":
            snake_y -= BLOCK_SIZE
        if direction == "DOWN":
            snake_y += BLOCK_SIZE
        if direction == "LEFT":
            snake_x -= BLOCK_SIZE
        if direction == "RIGHT":
            snake_x += BLOCK_SIZE

        # Check for wall collision
        if snake_x < 0 or snake_x >= SCREEN_WIDTH or snake_y < 0 or snake_y >= SCREEN_HEIGHT:
            game_over = True

        # Check for self collision
        for segment in snake_body[1:]:
            if snake_body[0] == segment:
                game_over = True
                break

        if game_over:
            break

        # Add new head to snake body
        snake_body.insert(0, (snake_x, snake_y))

        # Check if snake eats food
        if snake_x == food_x and snake_y == food_y:
            score += 1
            food_x = random.randrange(0, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE
            food_y = random.randrange(0, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
        else:
            # Remove tail if no food eaten
            snake_body.pop()

        # Drawing
        screen.fill(WHITE)
        draw_grid()
        
        # Draw snake
        for segment in snake_body:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw food
        pygame.draw.rect(screen, RED, (food_x, food_y, BLOCK_SIZE, BLOCK_SIZE))

        show_score(score)

        # Update the display
        pygame.display.flip()

        # Control frame rate
        clock.tick(SNAKE_SPEED)

    # Game over
    game_over_screen(score)
    main() # Restart the game

if __name__ == "__main__":
    main()
