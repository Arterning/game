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
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
YELLOW = (255, 223, 0)
ORANGE = (255, 140, 0)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)

# Game states
class GameState(Enum):
    READY = 0
    PLAYING = 1
    GAME_OVER = 2

# Bird class
class Bird:
    def __init__(self):
        self.width = 34
        self.height = 24
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.rotation = 0

    def jump(self):
        self.velocity = self.jump_strength

    def update(self):
        # Apply gravity
        self.velocity += self.gravity
        self.y += self.velocity

        # Update rotation based on velocity
        if self.velocity < 0:
            self.rotation = min(25, -self.velocity * 3)
        else:
            self.rotation = max(-90, -self.velocity * 2)

        # Limit velocity
        if self.velocity > 10:
            self.velocity = 10

    def draw(self, screen):
        # Draw bird body (circle)
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)

        # Body
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), self.width // 2)
        pygame.draw.circle(screen, ORANGE, (center_x, center_y), self.width // 2, 2)

        # Eye
        eye_x = center_x + 8
        eye_y = center_y - 3
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 5)
        pygame.draw.circle(screen, BLACK, (eye_x + 2, eye_y), 3)

        # Beak
        beak_points = [
            (center_x + self.width // 2, center_y),
            (center_x + self.width // 2 + 10, center_y - 3),
            (center_x + self.width // 2 + 10, center_y + 3)
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)

        # Wing
        wing_y_offset = int(abs(pygame.time.get_ticks() / 100 % 10 - 5))
        wing_rect = pygame.Rect(center_x - 10, center_y + 5 + wing_y_offset, 12, 8)
        pygame.draw.ellipse(screen, ORANGE, wing_rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def reset(self):
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.rotation = 0

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 60
        self.gap = 150
        self.speed = 3

        # Random gap position
        min_height = 100
        max_height = SCREEN_HEIGHT - self.gap - 100
        self.gap_y = random.randint(min_height, max_height)

        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        # Top pipe
        top_pipe_height = self.gap_y
        top_pipe_rect = pygame.Rect(self.x, 0, self.width, top_pipe_height)
        pygame.draw.rect(screen, GREEN, top_pipe_rect)
        pygame.draw.rect(screen, DARK_GREEN, top_pipe_rect, 3)

        # Top pipe cap
        cap_height = 25
        top_cap_rect = pygame.Rect(self.x - 5, top_pipe_height - cap_height,
                                    self.width + 10, cap_height)
        pygame.draw.rect(screen, GREEN, top_cap_rect)
        pygame.draw.rect(screen, DARK_GREEN, top_cap_rect, 3)

        # Bottom pipe
        bottom_pipe_y = self.gap_y + self.gap
        bottom_pipe_height = SCREEN_HEIGHT - bottom_pipe_y
        bottom_pipe_rect = pygame.Rect(self.x, bottom_pipe_y, self.width, bottom_pipe_height)
        pygame.draw.rect(screen, GREEN, bottom_pipe_rect)
        pygame.draw.rect(screen, DARK_GREEN, bottom_pipe_rect, 3)

        # Bottom pipe cap
        bottom_cap_rect = pygame.Rect(self.x - 5, bottom_pipe_y,
                                       self.width + 10, cap_height)
        pygame.draw.rect(screen, GREEN, bottom_cap_rect)
        pygame.draw.rect(screen, DARK_GREEN, bottom_cap_rect, 3)

    def get_rects(self):
        # Return collision rectangles for top and bottom pipes
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap,
                                  self.width, SCREEN_HEIGHT - (self.gap_y + self.gap))
        return [top_rect, bottom_rect]

    def is_off_screen(self):
        return self.x + self.width < 0

# Ground class
class Ground:
    def __init__(self):
        self.height = 100
        self.y = SCREEN_HEIGHT - self.height
        self.x1 = 0
        self.x2 = SCREEN_WIDTH
        self.speed = 3

    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 <= -SCREEN_WIDTH:
            self.x1 = self.x2 + SCREEN_WIDTH
        if self.x2 <= -SCREEN_WIDTH:
            self.x2 = self.x1 + SCREEN_WIDTH

    def draw(self, screen):
        # Draw ground tiles
        rect1 = pygame.Rect(self.x1, self.y, SCREEN_WIDTH, self.height)
        rect2 = pygame.Rect(self.x2, self.y, SCREEN_WIDTH, self.height)

        pygame.draw.rect(screen, BROWN, rect1)
        pygame.draw.rect(screen, BROWN, rect2)

        # Draw grass on top
        grass_height = 10
        pygame.draw.rect(screen, GREEN, (self.x1, self.y, SCREEN_WIDTH, grass_height))
        pygame.draw.rect(screen, GREEN, (self.x2, self.y, SCREEN_WIDTH, grass_height))

        # Draw some texture lines
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, DARK_GREEN,
                           (self.x1 + i, self.y),
                           (self.x1 + i, self.y + self.height), 2)
            pygame.draw.line(screen, DARK_GREEN,
                           (self.x2 + i, self.y),
                           (self.x2 + i, self.y + self.height), 2)

    def get_rect(self):
        return pygame.Rect(0, self.y, SCREEN_WIDTH, self.height)

# Flappy Bird game class
class FlappyGame:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 36)
        self.tiny_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.state = GameState.READY
        self.score = 0
        self.high_score = getattr(self, 'high_score', 0)

        self.bird = Bird()
        self.pipes = []
        self.ground = Ground()

        self.pipe_spawn_timer = 0
        self.pipe_spawn_interval = 90  # Spawn pipe every 1.5 seconds

    def spawn_pipe(self):
        self.pipes.append(Pipe(SCREEN_WIDTH))

    def handle_collisions(self):
        bird_rect = self.bird.get_rect()

        # Check collision with ground
        if bird_rect.colliderect(self.ground.get_rect()):
            return True

        # Check collision with ceiling
        if self.bird.y <= 0:
            return True

        # Check collision with pipes
        for pipe in self.pipes:
            for pipe_rect in pipe.get_rects():
                if bird_rect.colliderect(pipe_rect):
                    return True

        return False

    def update_score(self):
        for pipe in self.pipes:
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score

    def draw_background(self):
        # Sky gradient
        self.screen.fill(SKY_BLUE)

        # Draw clouds
        cloud_positions = [(100, 100), (300, 80), (500, 120), (700, 90)]
        for x, y in cloud_positions:
            offset = int((pygame.time.get_ticks() / 50) % SCREEN_WIDTH)
            cloud_x = (x + offset) % (SCREEN_WIDTH + 100) - 50
            self.draw_cloud(cloud_x, y)

    def draw_cloud(self, x, y):
        # Draw a simple cloud
        pygame.draw.circle(self.screen, WHITE, (x, y), 20)
        pygame.draw.circle(self.screen, WHITE, (x + 20, y), 25)
        pygame.draw.circle(self.screen, WHITE, (x + 40, y), 20)
        pygame.draw.circle(self.screen, WHITE, (x + 20, y - 15), 20)

    def draw_ui(self):
        # Draw score
        score_text = self.font.render(str(self.score), True, WHITE)
        score_outline = self.font.render(str(self.score), True, BLACK)

        text_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))

        # Draw outline
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_rect = text_rect.copy()
            outline_rect.x += dx
            outline_rect.y += dy
            self.screen.blit(score_outline, outline_rect)

        self.screen.blit(score_text, text_rect)

    def draw_ready_screen(self):
        # Draw "Ready" message
        ready_text = self.font.render("READY", True, WHITE)
        ready_outline = self.font.render("READY", True, BLACK)
        ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_rect = ready_rect.copy()
            outline_rect.x += dx
            outline_rect.y += dy
            self.screen.blit(ready_outline, outline_rect)

        self.screen.blit(ready_text, ready_rect)

        # Draw instruction
        instruction_text = self.tiny_font.render("Press SPACE to start", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(instruction_text, instruction_rect)

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        game_over_outline = self.font.render("GAME OVER", True, BLACK)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))

        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_rect = text_rect.copy()
            outline_rect.x += dx
            outline_rect.y += dy
            self.screen.blit(game_over_outline, outline_rect)

        self.screen.blit(game_over_text, text_rect)

        # Score display
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)

        # High score
        high_score_text = self.small_font.render(f"Best: {self.high_score}", True, YELLOW)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(high_score_text, high_score_rect)

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

                    # Space - jump or start game
                    if event.key == pygame.K_SPACE:
                        if self.state == GameState.READY:
                            self.state = GameState.PLAYING
                            self.bird.jump()
                        elif self.state == GameState.PLAYING:
                            self.bird.jump()

                    # R - restart game
                    if self.state == GameState.GAME_OVER and event.key == pygame.K_r:
                        self.reset_game()

            # Game logic
            if self.state == GameState.PLAYING:
                # Update bird
                self.bird.update()

                # Update ground
                self.ground.update()

                # Update pipes
                for pipe in self.pipes:
                    pipe.update()

                # Remove off-screen pipes
                self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]

                # Spawn new pipes
                self.pipe_spawn_timer += 1
                if self.pipe_spawn_timer >= self.pipe_spawn_interval:
                    self.spawn_pipe()
                    self.pipe_spawn_timer = 0

                # Update score
                self.update_score()

                # Check collisions
                if self.handle_collisions():
                    self.state = GameState.GAME_OVER

            elif self.state == GameState.READY:
                # Gentle floating animation
                self.bird.y = SCREEN_HEIGHT // 2 + int(10 * __import__('math').sin(pygame.time.get_ticks() / 200))
                self.ground.update()

            # Rendering
            self.draw_background()

            # Draw pipes
            for pipe in self.pipes:
                pipe.draw(self.screen)

            # Draw ground
            self.ground.draw(self.screen)

            # Draw bird
            self.bird.draw(self.screen)

            # Draw UI based on state
            if self.state == GameState.READY:
                self.draw_ready_screen()
            elif self.state == GameState.PLAYING:
                self.draw_ui()
            elif self.state == GameState.GAME_OVER:
                self.draw_ui()
                self.draw_game_over()

            pygame.display.flip()

        return False

def start_game(screen):
    """Entry point for Flappy Bird game"""
    game = FlappyGame(screen)
    return game.run()
