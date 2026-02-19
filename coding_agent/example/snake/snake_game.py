'''
A classic Snake game implemented in Python using the Pygame library.

 The game features:
 - A snake that grows longer as it eats food.
 - A score that increases with each food item eaten.
 - Different food types (regular, bonus, bad) with unique effects.
 - Game over conditions when the snake hits the screen boundaries or itself.
 - Options to restart or quit the game after a game over.
'''

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
INITIAL_SNAKE_LENGTH = 3 # Minimum length for the snake

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)     # Snake color
RED = (255, 0, 0)       # Regular Food color
BLUE = (0, 0, 255)      # Bonus Food color
PURPLE = (128, 0, 128)  # Bad Food color

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Fonts for tutorial and game
font_title = pygame.font.Font(None, 70)
font_header = pygame.font.Font(None, 40)
font_body = pygame.font.Font(None, 30)
font_food_desc = pygame.font.Font(None, 28) # Slightly smaller for food descriptions
font_medium = pygame.font.Font(None, 35) # Correctly defined font for prompts/medium text

# --- Tutorial Functions ---
def display_tutorial():
    """Displays the improved tutorial screen and waits for a key press to start the game."""
    screen.fill(WHITE)

    title_text = font_title.render("Snake Adventure", True, BLACK) # Changed title for flair
    header_text = font_header.render("Controls & Food Types", True, BLACK)

    instructions = [
        ("Use ARROW KEYS to move", font_body, BLACK),
        ("", font_body, BLACK), # Spacer
        ("Food Types:", font_header, BLACK),
        ("RED (Regular):", font_body, RED),
        ("  +1 point, snake grows.", font_food_desc, BLACK),
        ("BLUE (Bonus):", font_body, BLUE),
        ("  +3 points, snake grows.", font_food_desc, BLACK),
        ("PURPLE (Bad):", font_body, PURPLE),
        ("  -1 point, snake shrinks.", font_food_desc, BLACK),
        ("", font_body, BLACK), # Spacer
        ("Avoid hitting walls or yourself!", font_body, BLACK),
        ("", font_body, BLACK), # Spacer
        # Using font_medium for the final prompt, ensuring it's defined
        ("Press any key to begin...", font_medium, BLACK)
    ]

    # Positioning elements
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))
    header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5 + 40))
    screen.blit(title_text, title_rect)
    screen.blit(header_text, header_rect)

    y_offset = SCREEN_HEIGHT // 5 + 80 # Starting Y position for instructions
    for i, (text, font, color) in enumerate(instructions):
        if text == "":
            # Determine spacer height based on the font of the *next* line for better consistency
            spacer_height = 35 # Default spacer height
            if i + 1 < len(instructions):
                next_font = instructions[i+1][1] # Get font of the next line
                if next_font == font_food_desc:
                    spacer_height = 25
                elif next_font == font_body:
                    spacer_height = 35
                elif next_font == font_header:
                    spacer_height = 40
            elif i > 0: # Fallback for spacers near the end
                 prev_font = instructions[i-1][1]
                 if prev_font == font_food_desc:
                     spacer_height = 25
                 elif prev_font == font_body:
                     spacer_height = 35
                 elif prev_font == font_header:
                     spacer_height = 40
            
            y_offset += spacer_height
            continue

        # Render text with its specific color
        rendered_text = font.render(text, True, color)
        
        # Center text horizontally. Adjust offset for colors to make them align visually.
        text_rect = rendered_text.get_rect(midleft=(SCREEN_WIDTH // 2 - 150, y_offset))
        if color in [RED, BLUE, PURPLE]: # Slightly indent food color descriptions
            text_rect = rendered_text.get_rect(midleft=(SCREEN_WIDTH // 2 - 130, y_offset))
        
        screen.blit(rendered_text, text_rect)
        y_offset += 25 # Move to the next line

    pygame.display.flip()

    # Wait for a key press to start the game
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

# --- Game Helper Functions ---
def draw_grid():
    """Draws the grid lines on the game screen."""
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH, y))

def show_score(score):
    """Displays the current score on the screen."""
    font = pygame.font.Font(None, 35)
    score_surface = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surface, (10, 10))

def game_over_screen(score):
    """Displays the game over screen with final score and options to restart or quit."""
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

# --- Main Game Logic ---
def main():
    """Main function to run the Snake game."""
    # Initialize game state variables
    snake_x = SCREEN_WIDTH // 2
    snake_y = SCREEN_HEIGHT // 2
    snake_body = [(snake_x, snake_y - i * BLOCK_SIZE) for i in range(INITIAL_SNAKE_LENGTH)] # Initialize snake body
    direction = "RIGHT"
    change_to = direction

    # Food properties
    food_x, food_y = 0, 0
    food_color = RED
    food_probabilities = {'regular': 0.6, 'bonus': 0.2, 'bad': 0.2} # Adjust probabilities as needed
    food_types = list(food_probabilities.keys())
    food_weights = list(food_probabilities.values())

    def spawn_food():
        """Spawns food at a random location with a random type."""
        nonlocal food_x, food_y, food_color, food_type # Declare nonlocals to modify them
        
        # Ensure food spawns within the grid boundaries and not on the snake
        occupied_positions = snake_body[:]
        while True:
            food_x = random.randrange(0, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE
            food_y = random.randrange(0, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
            if (food_x, food_y) not in occupied_positions:
                break
        
        # Determine food type and color
        food_type = random.choices(food_types, weights=food_weights, k=1)[0]
        if food_type == 'regular':
            food_color = RED
        elif food_type == 'bonus':
            food_color = BLUE
        else: # bad food
            food_color = PURPLE
        return food_x, food_y, food_color, food_type

    food_x, food_y, food_color, food_type = spawn_food() # Initial food spawn

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

        # Add new head to snake body
        # Insert the new head position at the beginning of the snake's body list
        snake_body.insert(0, (snake_x, snake_y))

        # Check for wall collision
        if snake_x < 0 or snake_x >= SCREEN_WIDTH or snake_y < 0 or snake_y >= SCREEN_HEIGHT:
            game_over = True

        # Check for self collision
        # Check if the new head position is already in the rest of the snake's body
        for segment in snake_body[1:]:
            if snake_body[0] == segment:
                game_over = True
                break

        if game_over:
            break

        # Handle food eating
        if snake_x == food_x and snake_y == food_y:
            # Food is eaten, apply effects based on type
            if food_type == 'regular':
                score += 1
            elif food_type == 'bonus':
                score += 3 # More points for bonus food
                # Optional: Implement a temporary effect here later if desired
            elif food_type == 'bad':
                score -= 1 # Lose points for bad food
                # Shrink snake if its length is greater than the minimum
                if len(snake_body) > INITIAL_SNAKE_LENGTH:
                    snake_body.pop() # Remove the tail segment

            # Spawn new food after eating
            food_x, food_y, food_color, food_type = spawn_food()
        else:
            # If no food was eaten, remove the tail segment to keep snake length consistent
            snake_body.pop()

        # --- Drawing ---
        screen.fill(WHITE)
        draw_grid()

        # Draw snake
        for segment in snake_body:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw food
        pygame.draw.rect(screen, food_color, (food_x, food_y, BLOCK_SIZE, BLOCK_SIZE))

        show_score(score)

        # Update the display
        pygame.display.flip()

        # Control frame rate
        clock.tick(SNAKE_SPEED)

    # Game over sequence
    game_over_screen(score)
    # After game over, the program will exit. User needs to re-run script to play again.

# Entry point of the script
if __name__ == "__main__":
    display_tutorial() # Show tutorial first
    main() # Then start the main game logic
