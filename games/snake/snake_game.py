import pygame
import random
from enum import Enum
from collections import deque

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# Game states
class GameState(Enum):
    READY = 0
    PLAYING = 1
    GAME_OVER = 2

# Snake class
class Snake:
    def __init__(self):
        # Start in the middle of the screen
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2

        # Body is a deque of (x, y) positions
        self.body = deque([
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ])

        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow_pending = 0

    def get_head(self):
        return self.body[0]

    def change_direction(self, new_direction):
        # Can't reverse direction
        dx1, dy1 = self.direction.value
        dx2, dy2 = new_direction.value

        if (dx1, dy1) != (-dx2, -dy2):
            self.next_direction = new_direction

    def move(self):
        # Update direction
        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.get_head()
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # Add new head
        self.body.appendleft(new_head)

        # Remove tail if not growing
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1

    def check_collision(self):
        head_x, head_y = self.get_head()

        # Check wall collision
        if (head_x < 0 or head_x >= GRID_WIDTH or
            head_y < 0 or head_y >= GRID_HEIGHT):
            return True

        # Check self collision
        if self.get_head() in list(self.body)[1:]:
            return True

        return False

    def draw(self, screen):
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

            if i == 0:
                # Head - brighter green
                pygame.draw.rect(screen, GREEN, rect)
                pygame.draw.rect(screen, DARK_GREEN, rect, 2)

                # Draw eyes on head
                eye_size = 3
                if self.direction == Direction.UP:
                    eye1_pos = (x * GRID_SIZE + 5, y * GRID_SIZE + 5)
                    eye2_pos = (x * GRID_SIZE + GRID_SIZE - 8, y * GRID_SIZE + 5)
                elif self.direction == Direction.DOWN:
                    eye1_pos = (x * GRID_SIZE + 5, y * GRID_SIZE + GRID_SIZE - 8)
                    eye2_pos = (x * GRID_SIZE + GRID_SIZE - 8, y * GRID_SIZE + GRID_SIZE - 8)
                elif self.direction == Direction.LEFT:
                    eye1_pos = (x * GRID_SIZE + 5, y * GRID_SIZE + 5)
                    eye2_pos = (x * GRID_SIZE + 5, y * GRID_SIZE + GRID_SIZE - 8)
                else:  # RIGHT
                    eye1_pos = (x * GRID_SIZE + GRID_SIZE - 8, y * GRID_SIZE + 5)
                    eye2_pos = (x * GRID_SIZE + GRID_SIZE - 8, y * GRID_SIZE + GRID_SIZE - 8)

                pygame.draw.circle(screen, BLACK, eye1_pos, eye_size)
                pygame.draw.circle(screen, BLACK, eye2_pos, eye_size)
            else:
                # Body - darker green
                pygame.draw.rect(screen, DARK_GREEN, rect)
                pygame.draw.rect(screen, GREEN, rect, 2)

    def reset(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2

        self.body = deque([
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ])

        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow_pending = 0

# Food class
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self, snake_body=None):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)

            # Make sure food doesn't spawn on snake
            if snake_body is None or (x, y) not in snake_body:
                self.position = (x, y)
                break

    def draw(self, screen):
        x, y = self.position
        center_x = x * GRID_SIZE + GRID_SIZE // 2
        center_y = y * GRID_SIZE + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2

        # Draw apple
        pygame.draw.circle(screen, RED, (center_x, center_y), radius)
        pygame.draw.circle(screen, DARK_RED, (center_x, center_y), radius, 2)

        # Draw stem
        stem_points = [
            (center_x, center_y - radius),
            (center_x + 2, center_y - radius - 3),
            (center_x + 4, center_y - radius - 2)
        ]
        pygame.draw.lines(screen, DARK_GREEN, False, stem_points, 2)

# Snake game class
class SnakeGame:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.state = GameState.READY
        self.score = 0
        self.high_score = getattr(self, 'high_score', 0)

        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)

        self.move_timer = 0
        self.base_move_delay = 10  # Frames between moves
        self.move_delay = self.base_move_delay

    def update_speed(self):
        # Speed increases with score
        speed_increase = self.score // 5
        self.move_delay = max(3, self.base_move_delay - speed_increase)

    def draw_grid(self):
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))

    def draw_ui(self):
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw high score
        high_score_text = self.tiny_font.render(f"Best: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (10, 50))

        # Draw length
        length_text = self.tiny_font.render(f"Length: {len(self.snake.body)}", True, WHITE)
        self.screen.blit(length_text, (SCREEN_WIDTH - 150, 10))

    def draw_ready_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Ready text
        ready_text = self.font.render("READY", True, GREEN)
        ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(ready_text, ready_rect)

        # Instructions
        instructions = [
            "Use Arrow Keys to move",
            "Eat food to grow",
            "Don't hit walls or yourself!",
            "",
            "Press SPACE to start"
        ]

        y_offset = SCREEN_HEIGHT // 2 + 20
        for instruction in instructions:
            text = self.tiny_font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(game_over_text, text_rect)

        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)

        # High score
        if self.score == self.high_score and self.score > 0:
            new_best = self.tiny_font.render("NEW BEST!", True, YELLOW)
            new_best_rect = new_best.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15))
            self.screen.blit(new_best, new_best_rect)
        else:
            high_text = self.small_font.render(f"Best: {self.high_score}", True, YELLOW)
            high_rect = high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(high_text, high_rect)

        # Instructions
        restart_text = self.tiny_font.render("Press R to Restart", True, GREEN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(restart_text, restart_rect)

        menu_text = self.tiny_font.render("Press ESC to Menu", True, YELLOW)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(menu_text, menu_rect)

    def run(self):
        running = True

        while running:
            self.clock.tick(FPS)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.KEYDOWN:
                    # ESC - return to menu
                    if event.key == pygame.K_ESCAPE:
                        return True

                    # Arrow keys - change direction
                    if self.state == GameState.PLAYING:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.snake.change_direction(Direction.UP)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.snake.change_direction(Direction.DOWN)
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.snake.change_direction(Direction.LEFT)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.snake.change_direction(Direction.RIGHT)

                    # Space - start game
                    if self.state == GameState.READY and event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING

                    # R - restart game
                    if self.state == GameState.GAME_OVER and event.key == pygame.K_r:
                        self.reset_game()

            # Game logic
            if self.state == GameState.PLAYING:
                self.move_timer += 1

                if self.move_timer >= self.move_delay:
                    self.move_timer = 0

                    # Move snake
                    self.snake.move()

                    # Check collision with walls/self
                    if self.snake.check_collision():
                        self.state = GameState.GAME_OVER
                        if self.score > self.high_score:
                            self.high_score = self.score

                    # Check food collision
                    if self.snake.get_head() == self.food.position:
                        self.snake.grow()
                        self.score += 10
                        self.food.spawn(self.snake.body)
                        self.update_speed()

            # Rendering
            self.screen.fill(BLACK)

            # Draw grid
            self.draw_grid()

            # Draw game objects
            self.food.draw(self.screen)
            self.snake.draw(self.screen)

            # Draw UI
            self.draw_ui()

            # Draw state overlays
            if self.state == GameState.READY:
                self.draw_ready_screen()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()

            pygame.display.flip()

        return False

def start_game(screen):
    """Entry point for Snake game"""
    game = SnakeGame(screen)
    return game.run()
