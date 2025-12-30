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
    {
        'name': 'Flappy Bird',
        'description': 'Tap to fly and avoid pipes',
        'module': 'games.flappy',
        'function': 'start_game'
    },
    {
        'name': 'Snake',
        'description': 'Eat food and grow longer',
        'module': 'games.snake',
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
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title_text, title_rect)

        # Draw subtitle
        subtitle_text = self.desc_font.render("Select a game to play", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle_text, subtitle_rect)

        # 卡片配置
        card_width = 170
        card_height = 220
        card_spacing = 25
        start_y = 200

        # 计算总宽度并居中
        total_width = len(self.games) * card_width + (len(self.games) - 1) * card_spacing
        start_x = (SCREEN_WIDTH - total_width) // 2

        # 绘制游戏卡片（横向排列）
        for i, game in enumerate(self.games):
            x_pos = start_x + i * (card_width + card_spacing)

            # 绘制游戏选项背景
            is_selected = (i == self.selected_index)
            bg_color = LIGHT_BLUE if is_selected else DARK_BLUE

            # 游戏卡片
            card_rect = pygame.Rect(x_pos, start_y, card_width, card_height)
            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, card_rect, 3 if is_selected else 2, border_radius=15)

            # 选中标记（在卡片上方）
            if is_selected:
                marker_text = self.menu_font.render("▼", True, GREEN)
                marker_rect = marker_text.get_rect(center=(x_pos + card_width // 2, start_y - 25))
                self.screen.blit(marker_text, marker_rect)

            # 游戏名称（多行处理）
            name_lines = game['name'].split()
            name_y = start_y + 40
            for line in name_lines:
                name_text = self.menu_font.render(line, True, WHITE)
                name_rect = name_text.get_rect(center=(x_pos + card_width // 2, name_y))
                self.screen.blit(name_text, name_rect)
                name_y += 45

            # 游戏描述（多行换行）
            desc_words = game['description'].split()
            desc_lines = []
            current_line = []
            for word in desc_words:
                test_line = ' '.join(current_line + [word])
                test_text = self.desc_font.render(test_line, True, GRAY)
                if test_text.get_width() <= card_width - 20:
                    current_line.append(word)
                else:
                    if current_line:
                        desc_lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                desc_lines.append(' '.join(current_line))

            desc_y = start_y + card_height - 80
            for line in desc_lines[:3]:  # 最多显示3行
                desc_text = self.desc_font.render(line, True, GRAY)
                desc_rect = desc_text.get_rect(center=(x_pos + card_width // 2, desc_y))
                self.screen.blit(desc_text, desc_rect)
                desc_y += 25

        # Draw control hints
        hint_y = SCREEN_HEIGHT - 60
        hints = [
            "LEFT/RIGHT - Select",
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
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.games)
            elif event.key == pygame.K_RIGHT:
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
