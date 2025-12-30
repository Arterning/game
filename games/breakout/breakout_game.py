import pygame
import random
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (160, 32, 240)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)

# Game states
class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    LEVEL_COMPLETE = 2
    WAITING = 3  # Waiting for player to launch ball

# Paddle class
class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 8
        self.color = BLUE

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        # Keep paddle within screen bounds
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, screen):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Ball class
class Ball:
    def __init__(self, paddle):
        self.radius = 8
        self.reset(paddle)
        self.max_speed = 10

    def reset(self, paddle):
        self.x = paddle.x + paddle.width // 2
        self.y = paddle.y - self.radius - 5
        self.vel_x = 0
        self.vel_y = 0
        self.attached = True
        self.color = YELLOW

    def launch(self):
        if self.attached:
            self.attached = False
            angle = random.uniform(-60, 60)  # Launch angle in degrees
            import math
            self.vel_x = 5 * math.sin(math.radians(angle))
            self.vel_y = -5 * math.cos(math.radians(angle))

    def update(self, paddle):
        if self.attached:
            self.x = paddle.x + paddle.width // 2
            self.y = paddle.y - self.radius - 5
        else:
            self.x += self.vel_x
            self.y += self.vel_y

            # Wall collisions
            if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
                self.vel_x = -self.vel_x
                self.x = max(self.radius, min(self.x, SCREEN_WIDTH - self.radius))

            if self.y - self.radius <= 0:
                self.vel_y = -self.vel_y
                self.y = self.radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)

    def check_paddle_collision(self, paddle):
        if self.attached:
            return False

        paddle_rect = paddle.get_rect()
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                               self.radius * 2, self.radius * 2)

        if ball_rect.colliderect(paddle_rect) and self.vel_y > 0:
            # Calculate hit position on paddle (-1 to 1)
            hit_pos = (self.x - paddle.x) / paddle.width
            hit_pos = (hit_pos - 0.5) * 2  # Convert to -1 to 1 range

            # Adjust horizontal velocity based on hit position
            import math
            angle = hit_pos * 60  # Max 60 degrees deflection
            speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
            speed = min(speed * 1.05, self.max_speed)  # Slight speed increase

            self.vel_x = speed * math.sin(math.radians(angle))
            self.vel_y = -abs(speed * math.cos(math.radians(angle)))

            self.y = paddle.y - self.radius
            return True
        return False

    def is_out_of_bounds(self):
        return self.y - self.radius > SCREEN_HEIGHT

# Brick class
class Brick:
    def __init__(self, x, y, width, height, color, hits=1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hits = hits
        self.max_hits = hits
        self.active = True

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.active = False
            return True  # Brick destroyed
        # Change color based on remaining hits
        if self.hits == 2:
            self.color = ORANGE
        elif self.hits == 1:
            self.color = RED
        return False  # Brick still alive

    def draw(self, screen):
        if self.active:
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

            # Draw hit counter for multi-hit bricks
            if self.max_hits > 1:
                font = pygame.font.Font(None, 20)
                text = font.render(str(self.hits), True, WHITE)
                text_rect = text.get_rect(center=(self.x + self.width // 2,
                                                  self.y + self.height // 2))
                screen.blit(text, text_rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Breakout game class
class BreakoutGame:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Breakout")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.state = GameState.WAITING
        self.level = 1
        self.score = 0
        self.lives = 3
        self.paddle = Paddle()
        self.ball = Ball(self.paddle)
        self.bricks = []

        self.create_level()

    def create_level(self):
        self.bricks = []
        self.state = GameState.WAITING
        self.ball.reset(self.paddle)

        # Brick dimensions
        brick_width = 70
        brick_height = 25
        padding = 5
        offset_x = 35
        offset_y = 80

        # Create brick layout based on level
        rows = min(5 + self.level // 2, 10)
        cols = 10

        colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]

        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (brick_width + padding)
                y = offset_y + row * (brick_height + padding)

                # Color based on row
                color = colors[row % len(colors)]

                # Add harder bricks in higher levels
                hits = 1
                if self.level >= 3 and row < 2:
                    hits = 2
                if self.level >= 5 and row < 1:
                    hits = 3

                self.bricks.append(Brick(x, y, brick_width, brick_height, color, hits))

    def handle_collisions(self):
        # Ball and brick collisions
        for brick in self.bricks:
            if not brick.active:
                continue

            brick_rect = brick.get_rect()
            ball_rect = pygame.Rect(self.ball.x - self.ball.radius,
                                   self.ball.y - self.ball.radius,
                                   self.ball.radius * 2, self.ball.radius * 2)

            if ball_rect.colliderect(brick_rect):
                # Determine collision side
                ball_center_x = self.ball.x
                ball_center_y = self.ball.y

                # Calculate overlap on each side
                left_overlap = (ball_center_x + self.ball.radius) - brick.x
                right_overlap = (brick.x + brick.width) - (ball_center_x - self.ball.radius)
                top_overlap = (ball_center_y + self.ball.radius) - brick.y
                bottom_overlap = (brick.y + brick.height) - (ball_center_y - self.ball.radius)

                # Find minimum overlap
                min_overlap = min(left_overlap, right_overlap, top_overlap, bottom_overlap)

                # Bounce based on collision side
                if min_overlap == left_overlap or min_overlap == right_overlap:
                    self.ball.vel_x = -self.ball.vel_x
                else:
                    self.ball.vel_y = -self.ball.vel_y

                # Hit the brick
                destroyed = brick.hit()
                if destroyed:
                    self.score += 10 * self.level
                else:
                    self.score += 5 * self.level

                break

        # Check if all bricks destroyed
        if all(not brick.active for brick in self.bricks):
            self.state = GameState.LEVEL_COMPLETE

    def draw_ui(self):
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw lives
        lives_text = self.small_font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 35))

        # Draw level
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, 10))

        # Draw launch hint when waiting
        if self.state == GameState.WAITING:
            hint_text = self.small_font.render("Press SPACE to launch ball", True, YELLOW)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            self.screen.blit(hint_text, hint_rect)

    def draw_game_over(self):
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        # Final score
        score_text = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        level_text = self.small_font.render(f"Level Reached: {self.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(level_text, level_rect)

        # Button hints
        restart_text = self.small_font.render("Press R to Restart", True, GREEN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)

        menu_text = self.small_font.render("Press ESC to Menu", True, YELLOW)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        self.screen.blit(menu_text, menu_rect)

    def draw_level_complete(self):
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 50, 0))
        self.screen.blit(overlay, (0, 0))

        # Level complete text
        complete_text = self.font.render("LEVEL COMPLETE!", True, YELLOW)
        text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(complete_text, text_rect)

        # Score bonus
        bonus_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(bonus_text, bonus_rect)

        # Next level hint
        next_text = self.small_font.render("Press SPACE for Next Level", True, WHITE)
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(next_text, next_rect)

    def run(self):
        running = True

        while running:
            self.clock.tick(FPS)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False  # Exit program

                if event.type == pygame.KEYDOWN:
                    # ESC key - return to menu (works in any state)
                    if event.key == pygame.K_ESCAPE:
                        return True

                    # State-specific key handling
                    if self.state == GameState.WAITING and event.key == pygame.K_SPACE:
                        self.ball.launch()
                        self.state = GameState.PLAYING

                    if self.state == GameState.GAME_OVER and event.key == pygame.K_r:
                        self.reset_game()

                    if self.state == GameState.LEVEL_COMPLETE and event.key == pygame.K_SPACE:
                        self.level += 1
                        self.lives += 1  # Bonus life for completing level
                        self.create_level()

            # Game logic
            if self.state == GameState.PLAYING or self.state == GameState.WAITING:
                keys = pygame.key.get_pressed()
                self.paddle.move(keys)
                self.ball.update(self.paddle)
                self.ball.check_paddle_collision(self.paddle)

                if self.state == GameState.PLAYING:
                    self.handle_collisions()

                    # Check if ball fell off screen
                    if self.ball.is_out_of_bounds():
                        self.lives -= 1
                        if self.lives <= 0:
                            self.state = GameState.GAME_OVER
                        else:
                            self.ball.reset(self.paddle)
                            self.state = GameState.WAITING

            # Rendering
            self.screen.fill(BLACK)

            # Draw game elements
            for brick in self.bricks:
                brick.draw(self.screen)

            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)

            # Draw UI
            self.draw_ui()

            # Draw game state overlays
            if self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.draw_level_complete()

            pygame.display.flip()

        return False

def start_game(screen):
    """Entry point for breakout game"""
    game = BreakoutGame(screen)
    return game.run()
