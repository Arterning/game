import pygame
import random
import sys
from enum import Enum

# 初始化Pygame
pygame.init()

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)

# 方向枚举
class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

# 游戏状态
class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    LEVEL_COMPLETE = 2

# 墙壁类型
class WallType(Enum):
    BRICK = 1  # 可破坏
    STONE = 2  # 不可破坏
    GRASS = 3  # 草丛，不阻挡

# 子弹类
class Bullet:
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner  # 'player' 或 'enemy'
        self.speed = 8
        self.width = 6
        self.height = 6
        self.active = True

    def update(self):
        if self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed

        # 检查是否出界
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, screen):
        if self.active:
            color = YELLOW if self.owner == 'player' else RED
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.width // 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)

# 墙壁类
class Wall:
    def __init__(self, x, y, wall_type):
        self.x = x
        self.y = y
        self.wall_type = wall_type
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.active = True

    def draw(self, screen):
        if self.active:
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            if self.wall_type == WallType.BRICK:
                pygame.draw.rect(screen, BROWN, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                # 绘制砖块纹理
                pygame.draw.line(screen, BLACK, (self.x, self.y + TILE_SIZE // 2),
                               (self.x + TILE_SIZE, self.y + TILE_SIZE // 2))
            elif self.wall_type == WallType.STONE:
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
            elif self.wall_type == WallType.GRASS:
                pygame.draw.rect(screen, DARK_GREEN, rect)
                # 绘制草丛纹理
                for i in range(5):
                    x_offset = random.randint(0, TILE_SIZE)
                    y_offset = random.randint(0, TILE_SIZE)
                    pygame.draw.line(screen, GREEN,
                                   (self.x + x_offset, self.y + y_offset),
                                   (self.x + x_offset, self.y + y_offset + 5), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# 坦克基类
class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.color = color
        self.direction = Direction.UP
        self.speed = 3
        self.health = 1
        self.shoot_cooldown = 0
        self.shoot_delay = 30  # 射击冷却时间（帧）

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.health > 0:
            # 绘制坦克主体
            pygame.draw.rect(screen, self.color, self.get_rect())
            pygame.draw.rect(screen, BLACK, self.get_rect(), 2)

            # 绘制炮管
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            barrel_length = 20

            if self.direction == Direction.UP:
                end_x, end_y = center_x, center_y - barrel_length
            elif self.direction == Direction.DOWN:
                end_x, end_y = center_x, center_y + barrel_length
            elif self.direction == Direction.LEFT:
                end_x, end_y = center_x - barrel_length, center_y
            elif self.direction == Direction.RIGHT:
                end_x, end_y = center_x + barrel_length, center_y

            pygame.draw.line(screen, BLACK, (center_x, center_y), (end_x, end_y), 4)

    def shoot(self):
        if self.shoot_cooldown <= 0:
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2

            # 根据方向调整子弹起始位置
            if self.direction == Direction.UP:
                bullet_x, bullet_y = center_x, center_y - 20
            elif self.direction == Direction.DOWN:
                bullet_x, bullet_y = center_x, center_y + 20
            elif self.direction == Direction.LEFT:
                bullet_x, bullet_y = center_x - 20, center_y
            elif self.direction == Direction.RIGHT:
                bullet_x, bullet_y = center_x + 20, center_y

            self.shoot_cooldown = self.shoot_delay
            return Bullet(bullet_x, bullet_y, self.direction, 'player')
        return None

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

# 玩家坦克类
class PlayerTank(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN)
        self.health = 3
        self.lives = 3

    def move(self, keys, walls):
        old_x, old_y = self.x, self.y

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction = Direction.UP
            self.y -= self.speed
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction = Direction.DOWN
            self.y += self.speed
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction = Direction.LEFT
            self.x -= self.speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction = Direction.RIGHT
            self.x += self.speed

        # 检查边界
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        if self.y < 0:
            self.y = 0
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height

        # 检查墙壁碰撞（草丛除外）
        for wall in walls:
            if wall.active and wall.wall_type != WallType.GRASS:
                if self.get_rect().colliderect(wall.get_rect()):
                    self.x, self.y = old_x, old_y
                    break

# 敌人坦克类
class EnemyTank(Tank):
    def __init__(self, x, y, level=1):
        super().__init__(x, y, RED)
        self.speed = 2 + (level - 1) * 0.5  # 随关卡提升速度
        self.move_timer = 0
        self.move_interval = 120  # 每2秒（120帧）换方向
        self.shoot_timer = 0
        self.shoot_interval = random.randint(60, 180)  # 随机射击间隔
        self.direction = random.choice(list(Direction))

    def update_ai(self, walls):
        self.move_timer += 1
        self.shoot_timer += 1

        # 随机改变方向
        if self.move_timer >= self.move_interval:
            self.direction = random.choice(list(Direction))
            self.move_timer = 0
            self.move_interval = random.randint(60, 180)

        # 移动
        old_x, old_y = self.x, self.y

        if self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed

        # 检查边界
        if self.x < 0 or self.x > SCREEN_WIDTH - self.width or \
           self.y < 0 or self.y > SCREEN_HEIGHT - self.height:
            self.x, self.y = old_x, old_y
            self.direction = random.choice(list(Direction))

        # 检查墙壁碰撞
        for wall in walls:
            if wall.active and wall.wall_type != WallType.GRASS:
                if self.get_rect().colliderect(wall.get_rect()):
                    self.x, self.y = old_x, old_y
                    self.direction = random.choice(list(Direction))
                    break

        # 更新射击冷却
        super().update()

    def try_shoot(self):
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            self.shoot_interval = random.randint(60, 180)
            if self.shoot_cooldown <= 0:
                center_x = self.x + self.width // 2
                center_y = self.y + self.height // 2

                if self.direction == Direction.UP:
                    bullet_x, bullet_y = center_x, center_y - 20
                elif self.direction == Direction.DOWN:
                    bullet_x, bullet_y = center_x, center_y + 20
                elif self.direction == Direction.LEFT:
                    bullet_x, bullet_y = center_x - 20, center_y
                elif self.direction == Direction.RIGHT:
                    bullet_x, bullet_y = center_x + 20, center_y

                self.shoot_cooldown = self.shoot_delay
                return Bullet(bullet_x, bullet_y, self.direction, 'enemy')
        return None

# 游戏类
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.state = GameState.PLAYING
        self.level = 1
        self.player = PlayerTank(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.enemies = []
        self.bullets = []
        self.walls = []
        self.enemies_killed = 0
        self.enemies_per_level = 3

        self.create_level()

    def create_level(self):
        self.enemies = []
        self.bullets = []
        self.walls = []

        # 创建敌人
        num_enemies = self.enemies_per_level + (self.level - 1)
        for i in range(num_enemies):
            x = random.randint(50, SCREEN_WIDTH - 100)
            y = random.randint(50, 200)
            self.enemies.append(EnemyTank(x, y, self.level))

        # 创建地图元素
        self.create_walls()

    def create_walls(self):
        # 创建一些随机墙壁
        for i in range(15):
            x = random.randint(1, SCREEN_WIDTH // TILE_SIZE - 2) * TILE_SIZE
            y = random.randint(3, SCREEN_HEIGHT // TILE_SIZE - 3) * TILE_SIZE
            wall_type = random.choice([WallType.BRICK, WallType.BRICK, WallType.STONE])
            self.walls.append(Wall(x, y, wall_type))

        # 添加一些草丛
        for i in range(10):
            x = random.randint(1, SCREEN_WIDTH // TILE_SIZE - 2) * TILE_SIZE
            y = random.randint(3, SCREEN_HEIGHT // TILE_SIZE - 3) * TILE_SIZE
            self.walls.append(Wall(x, y, WallType.GRASS))

        # 创建边界墙
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            self.walls.append(Wall(x, 0, WallType.STONE))
            self.walls.append(Wall(x, SCREEN_HEIGHT - TILE_SIZE, WallType.STONE))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            self.walls.append(Wall(0, y, WallType.STONE))
            self.walls.append(Wall(SCREEN_WIDTH - TILE_SIZE, y, WallType.STONE))

    def handle_collisions(self):
        # 子弹与墙壁碰撞
        for bullet in self.bullets[:]:
            if not bullet.active:
                continue

            for wall in self.walls:
                if not wall.active or wall.wall_type == WallType.GRASS:
                    continue

                if bullet.get_rect().colliderect(wall.get_rect()):
                    bullet.active = False
                    if wall.wall_type == WallType.BRICK:
                        wall.active = False
                    break

        # 子弹与坦克碰撞
        for bullet in self.bullets[:]:
            if not bullet.active:
                continue

            # 玩家子弹打敌人
            if bullet.owner == 'player':
                for enemy in self.enemies[:]:
                    if bullet.get_rect().colliderect(enemy.get_rect()):
                        bullet.active = False
                        enemy.health -= 1
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.enemies_killed += 1
                        break

            # 敌人子弹打玩家
            elif bullet.owner == 'enemy':
                if bullet.get_rect().colliderect(self.player.get_rect()):
                    bullet.active = False
                    self.player.health -= 1
                    if self.player.health <= 0:
                        self.player.lives -= 1
                        if self.player.lives > 0:
                            # 重置玩家位置和生命
                            self.player.x = SCREEN_WIDTH // 2
                            self.player.y = SCREEN_HEIGHT - 80
                            self.player.health = 3
                        else:
                            self.state = GameState.GAME_OVER

        # 移除不活跃的子弹
        self.bullets = [b for b in self.bullets if b.active]

        # 检查关卡完成
        if len(self.enemies) == 0:
            self.state = GameState.LEVEL_COMPLETE

    def draw_ui(self):
        # 绘制生命值
        lives_text = self.small_font.render(f"Lives: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 10))

        # 绘制血量
        health_text = self.small_font.render(f"Health: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (10, 35))

        # 绘制关卡
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, 10))

        # 绘制敌人数量
        enemies_text = self.small_font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 120, 35))

    def draw_game_over(self):
        # 半透明黑色背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文本
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        # 统计信息
        stats_text = self.small_font.render(f"Level Reached: {self.level}", True, WHITE)
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(stats_text, stats_rect)

        kills_text = self.small_font.render(f"Enemies Killed: {self.enemies_killed}", True, WHITE)
        kills_rect = kills_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(kills_text, kills_rect)

        # 按钮提示
        restart_text = self.small_font.render("Press R to Restart", True, GREEN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)

        quit_text = self.small_font.render("Press Q to Quit", True, RED)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        self.screen.blit(quit_text, quit_rect)

    def draw_level_complete(self):
        # 半透明绿色背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 50, 0))
        self.screen.blit(overlay, (0, 0))

        # 关卡完成文本
        complete_text = self.font.render("LEVEL COMPLETE!", True, YELLOW)
        text_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(complete_text, text_rect)

        # 提示文本
        next_text = self.small_font.render("Press SPACE for Next Level", True, WHITE)
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(next_text, next_rect)

    def run(self):
        running = True

        while running:
            self.clock.tick(FPS)

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == GameState.PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            bullet = self.player.shoot()
                            if bullet:
                                self.bullets.append(bullet)

                elif self.state == GameState.GAME_OVER:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False

                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.level += 1
                            self.create_level()
                            self.state = GameState.PLAYING

            # 游戏逻辑更新
            if self.state == GameState.PLAYING:
                keys = pygame.key.get_pressed()
                self.player.move(keys, self.walls)
                self.player.update()

                # 更新敌人
                for enemy in self.enemies:
                    enemy.update_ai(self.walls)
                    bullet = enemy.try_shoot()
                    if bullet:
                        self.bullets.append(bullet)

                # 更新子弹
                for bullet in self.bullets:
                    bullet.update()

                # 处理碰撞
                self.handle_collisions()

            # 渲染
            self.screen.fill(BLACK)

            # 绘制墙壁（先绘制非草丛）
            for wall in self.walls:
                if wall.wall_type != WallType.GRASS:
                    wall.draw(self.screen)

            # 绘制坦克和子弹
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)

            # 绘制草丛（在坦克之后，实现遮挡效果）
            for wall in self.walls:
                if wall.wall_type == WallType.GRASS:
                    wall.draw(self.screen)

            # 绘制UI
            self.draw_ui()

            # 绘制游戏状态
            if self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.draw_level_complete()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
