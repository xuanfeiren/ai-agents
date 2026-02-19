'''
A classic Snake game implemented in Python using the Pygame library.

 The game features:
 - A snake that grows longer as it eats food.
 - A score that increases with each food item eaten.
 - Different food types (regular, bonus, bad) with unique effects.
 - Game over conditions when the snake hits the screen boundaries or itself.
 - Options to restart or quit the game after a game over.
 - Multiple food items on the screen simultaneously.
 - Eating food spawns two additional food items.
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
MAX_FOOD_ITEMS = 3 # Maximum number of food items on screen at once. This will be a target, may exceed temporarily.

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
    """Displays the game over screen with final score and options to restart or quit.
    Returns True to restart, False to quit."""
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
                return False  # Quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False  # Quit
                elif event.key == pygame.K_r:
                    return True   # Restart

# --- Main Game Logic ---
def main():
    """Main function to run the Snake game."""
    
    # --- Outer loop for restarting the game ---
    while True: 
        # Initialize game state variables for a new game
        snake_x = SCREEN_WIDTH // 2
        snake_y = SCREEN_HEIGHT // 2
        snake_body = [(snake_x, snake_y - i * BLOCK_SIZE) for i in range(INITIAL_SNAKE_LENGTH)] # Initialize snake body
        direction = "RIGHT"
        change_to = direction

        # Food properties
        foods = [] # List to store multiple food items
        food_probabilities = {'regular': 0.6, 'bonus': 0.2, 'bad': 0.2} # Adjust probabilities as needed
        food_types = list(food_probabilities.keys())
        food_weights = list(food_probabilities.values())

        def spawn_food():
            """Spawns food items until MAX_FOOD_ITEMS is reached, and adds two extra if food is eaten."""
            nonlocal foods # Allow modification of the foods list
            occupied_positions = snake_body[:] # Positions occupied by the snake
            # Add existing food positions to occupied_positions to prevent spawning on top of food
            for food_item in foods:
                occupied_positions.append((food_item['x'], food_item['y']))

            # Add food until MAX_FOOD_ITEMS is reached, or until we can't find a spot
            while len(foods) < MAX_FOOD_ITEMS:
                new_food_x = random.randrange(0, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE
                new_food_y = random.randrange(0, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
                
                # Ensure food does not spawn on the snake or on existing food
                if (new_food_x, new_food_y) not in occupied_positions:
                    # Determine food type and color
                    food_type = random.choices(food_types, weights=food_weights, k=1)[0]
                    if food_type == 'regular':
                        food_color = RED
                        score_value = 1
                    elif food_type == 'bonus':
                        food_color = BLUE
                        score_value = 3
                    else: # bad food
                        food_color = PURPLE
                        score_value = -1
                    
                    foods.append({
                        'x': new_food_x,
                        'y': new_food_y,
                        'color': food_color,
                        'type': food_type,
                        'score': score_value
                    })
                    occupied_positions.append((new_food_x, new_food_y)) # Add newly spawned food to occupied positions
                else:
                    # If we can't find a spot, break to avoid infinite loop
                    break

        spawn_food() # Initial food spawn to fill up to MAX_FOOD_ITEMS

        score = 0
        game_over = False

        # --- Inner game loop ---
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    should_restart = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != "DOWN":
                        change_to = "UP"
                    if event.key == pygame.K_DOWN and direction != "UP":
                        change_to = "DOWN"
                    if event.key == pygame.K_LEFT and direction != "RIGHT":
                        change_to = "LEFT"
                    if event.key == pygame.K_RIGHT and direction != "LEFT":
                        change_to = "RIGHT"
            else:
                direction = change_to

                if direction == "UP":
                    snake_y -= BLOCK_SIZE
                if direction == "DOWN":
                    snake_y += BLOCK_SIZE
                if direction == "LEFT":
                    snake_x -= BLOCK_SIZE
                if direction == "RIGHT":
                    snake_x += BLOCK_SIZE

                snake_body.insert(0, (snake_x, snake_y))

                # Wall collision
                if snake_x < 0 or snake_x >= SCREEN_WIDTH or snake_y < 0 or snake_y >= SCREEN_HEIGHT:
                    game_over = True
                    should_restart = False
                    break
                
                # Self collision
                for segment in snake_body[1:]:
                    if snake_body[0] == segment:
                        game_over = True
                        should_restart = False
                        break
                if game_over: break

                # Food eating - check collision with any food item
                eaten_food_index = -1
                for i, food_item in enumerate(foods):
                    if snake_x == food_item['x'] and snake_y == food_item['y']:
                        score += food_item['score']
                        # Apply effects based on food type (e.g., shrinking snake)
                        if food_item['type'] == 'bad':
                            if len(snake_body) > INITIAL_SNAKE_LENGTH:
                                snake_body.pop() # Remove the tail segment
                        
                        eaten_food_index = i
                        break # Exit loop once food is eaten
                
                if eaten_food_index != -1:
                    foods.pop(eaten_food_index) # Remove the eaten food
                    # Add TWO new random food items
                    for _ in range(2):
                        spawn_food() # Call spawn_food twice to add two new items
                    # No need to pop snake tail if food is eaten
                else:
                    # If no food was eaten, remove the tail segment
                    snake_body.pop()

                # After handling eating/spawning, ensure we try to maintain MAX_FOOD_ITEMS if possible
                # This call ensures we add more if current count < MAX_FOOD_ITEMS, and also accounts for the two extras.
                spawn_food()

                # Drawing
                screen.fill(WHITE)
                draw_grid()

                # Draw snake
                for segment in snake_body:
                    pygame.draw.rect(screen, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

                # Draw all food items
                for food_item in foods:
                    pygame.draw.rect(screen, food_item['color'], (food_item['x'], food_item['y'], BLOCK_SIZE, BLOCK_SIZE))

                show_score(score)
                pygame.display.flip()
                clock.tick(SNAKE_SPEED)
        
        if not game_over: # If we broke out of the inner loop due to QUIT event
            break
            
        should_restart = game_over_screen(score)
        
        if not should_restart:
            break

    pygame.quit()
    sys.exit()

# Entry point of the script
if __name__ == "__main__":
    display_tutorial() # Show tutorial first
    main() # Then start the main game logic
