import pygame
import sys

# 初始化Pygame
pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_BLUE = (100, 150, 255)
DARK_BLUE = (50, 100, 200)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Game list configuration
GAMES = [
    {
        'name': 'Tank Battle',
        'description': 'Classic tank combat game',
        'module': 'games.tank',
        'function': 'start_game'
    },
    {
        'name': 'Breakout',
        'description': 'Break bricks with a bouncing ball',
        'module': 'games.breakout',
        'function': 'start_game'
    },
    # Add more games here in the future
    # {
    #     'name': 'Other Game',
    #     'description': 'Game description',
    #     'module': 'games.other',
    #     'function': 'start_game'
    # },
]


class GamePlatform:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Platform")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.desc_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)

        self.selected_index = 0
        self.games = GAMES

    def draw_menu(self):
        self.screen.fill(BLACK)

        # Draw title
        title_text = self.title_font.render("GAME PLATFORM", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        # Draw subtitle
        subtitle_text = self.desc_font.render("Select a game to play", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle_text, subtitle_rect)

        # 绘制游戏列表
        start_y = 220
        spacing = 120

        for i, game in enumerate(self.games):
            y_pos = start_y + i * spacing

            # 绘制游戏选项背景
            is_selected = (i == self.selected_index)
            bg_color = LIGHT_BLUE if is_selected else DARK_BLUE

            # 游戏卡片
            card_rect = pygame.Rect(100, y_pos - 10, SCREEN_WIDTH - 200, 100)
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, card_rect, 2, border_radius=10)

            # 选中标记
            if is_selected:
                marker_text = self.menu_font.render("►", True, GREEN)
                self.screen.blit(marker_text, (60, y_pos + 10))

            # 游戏名称
            name_text = self.menu_font.render(game['name'], True, WHITE)
            name_rect = name_text.get_rect(left=130, centery=y_pos + 20)
            self.screen.blit(name_text, name_rect)

            # 游戏描述
            desc_text = self.desc_font.render(game['description'], True, GRAY)
            desc_rect = desc_text.get_rect(left=130, top=y_pos + 50)
            self.screen.blit(desc_text, desc_rect)

        # Draw control hints
        hint_y = SCREEN_HEIGHT - 60
        hints = [
            "UP/DOWN - Select",
            "ENTER - Start",
            "ESC - Quit"
        ]

        hint_text = self.small_font.render(" | ".join(hints), True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, hint_y))
        self.screen.blit(hint_text, hint_rect)

        # Draw game count
        count_text = self.small_font.render(f"Available Games: {len(self.games)}", True, GRAY)
        count_rect = count_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(count_text, count_rect)

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.games)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.games)
            elif event.key == pygame.K_RETURN:
                return True  # Start game
            elif event.key == pygame.K_ESCAPE:
                return False  # Quit program
        return None

    def launch_game(self, game_info):
        """Launch the selected game"""
        try:
            # Dynamically import game module
            module = __import__(game_info['module'], fromlist=[game_info['function']])
            start_function = getattr(module, game_info['function'])

            # Start game with screen object
            return_to_menu = start_function(self.screen)

            # Restore platform title
            pygame.display.set_caption("Game Platform")

            return return_to_menu
        except Exception as e:
            print(f"Failed to start game: {e}")
            import traceback
            traceback.print_exc()
            return True  # Return to menu on error

    def run(self):
        running = True
        in_menu = True

        while running:
            self.clock.tick(FPS)

            if in_menu:
                # Menu interface
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    else:
                        result = self.handle_menu_input(event)
                        if result is True:
                            # Start game
                            in_menu = False
                            return_to_menu = self.launch_game(self.games[self.selected_index])
                            if return_to_menu:
                                in_menu = True
                            else:
                                running = False
                        elif result is False:
                            # Quit
                            running = False

                self.draw_menu()
                pygame.display.flip()

        pygame.quit()
        sys.exit()


def main():
    platform = GamePlatform()
    platform.run()


if __name__ == "__main__":
    main()
