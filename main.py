import pygame
import sys
from map import GameMap
from entities.item import Item
from entities.player import Player
import os

# =====================
# CONFIG
# =====================

WIDTH = 1280
HEIGHT = 720
FPS = 60

BACKGROUND_COLOR = (20, 20, 25)

# =====================
# GAME
# =====================

class Game:

    def __init__(self):

        pygame.init()

        BASE_DIR = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Roguelike")

        self.clock = pygame.time.Clock()
        self.running = True

        # World
        self.map = GameMap()
        self.walls = self.map.walls

        # Player
        spawn_x, spawn_y = self.map.get_random_spawn_position(30)

        self.player_rect = pygame.Rect(
            spawn_x,
            spawn_y,
            16,
            16
        )

        self.player_speed = 125

        nickname = sys.argv[1]

        self.player = Player.load(nickname)

        # movement smoothing (IMPORTANT FIX)
        self.vel_x = 0
        self.vel_y = 0

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Items
        self.items = []

        for _ in range(15):

            x, y = self.map.get_random_item_position()

            self.items.append(
                Item(
                    x,
                    y,
                    "coin",
                    1
                )
            )

        self.font = pygame.font.SysFont(
            "arial",
            28
        )

        self.coin_icon = pygame.image.load(
            os.path.join(
                BASE_DIR,
                "assets",
                "coin.png"
            )
        ).convert_alpha()

        self.coin_icon = pygame.transform.scale(
            self.coin_icon,
            (32, 32)
        )

        self.xp_icon = pygame.image.load(
            os.path.join(
                BASE_DIR,
                "assets",
                "xp.png"
            )
        ).convert_alpha()

        self.xp_icon = pygame.transform.scale(
            self.xp_icon,
            (32, 32)
        )

        self.hud_panel = pygame.image.load(
            os.path.join(BASE_DIR, "assets", "hud_panel.png")
        ).convert_alpha()

        self.hud_panel = pygame.transform.scale(
            self.hud_panel,
            (250, 80)
        )

    # =====================
    # INPUT
    # =====================

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    # =====================
    # MOVEMENT + COLLISION FIX
    # =====================

    def update_player(self, dt):

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.player_speed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.player_speed * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.player_speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.player_speed * dt

        # accumulate float movement safely
        self.vel_x += dx
        self.vel_y += dy

        mx = int(self.vel_x)
        my = int(self.vel_y)

        self.vel_x -= mx
        self.vel_y -= my

        self.move_player(mx, my)

    def move_player(self, dx, dy):

        # X axis
        self.player_rect.x += dx
        for wall in self.walls:
            if self.player_rect.colliderect(wall):
                if dx > 0:
                    self.player_rect.right = wall.left
                elif dx < 0:
                    self.player_rect.left = wall.right
                break

        # Y axis
        self.player_rect.y += dy
        for wall in self.walls:
            if self.player_rect.colliderect(wall):
                if dy > 0:
                    self.player_rect.bottom = wall.top
                elif dy < 0:
                    self.player_rect.top = wall.bottom
                break

    # =====================
    # CAMERA FIX
    # =====================

    def update_camera(self):

        self.camera_x = self.player_rect.centerx - WIDTH // 2
        self.camera_y = self.player_rect.centery - HEIGHT // 2

        max_x = self.map.WIDTH * self.map.TILE_SIZE - WIDTH
        max_y = self.map.HEIGHT * self.map.TILE_SIZE - HEIGHT

        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

    # =====================
    # UPDATE
    # =====================

    def update(self, dt):

        self.update_player(dt)

        for item in self.items[:]:

            if item.update(
                self.player_rect,
                self.player
            ):
                self.items.remove(item)

        self.update_camera()

    # =====================
    # DRAW
    # =====================

    def draw(self):

        self.screen.fill(BACKGROUND_COLOR)

        self.map.draw(self.screen, self.camera_x, self.camera_y)

        pygame.draw.rect(
            self.screen,
            (200, 50, 50),
            pygame.Rect(
                self.player_rect.x - self.camera_x,
                self.player_rect.y - self.camera_y,
                self.player_rect.width,
                self.player_rect.height
            )
        )

        for item in self.items:
            item.draw(
                self.screen,
                self.camera_x,
                self.camera_y
            )

        self.draw_hud()

        pygame.display.flip()

    def draw_hud(self):

        # Background panel

        self.screen.blit(
            self.hud_panel,
            (10, 10)
        )

        # Coin icon

        self.screen.blit(
            self.coin_icon,
            (20, 20)
        )

        # Coin amount

        money_text = self.font.render(
            str(self.player.money),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            money_text,
            (60, 25)
        )

        # XP icon

        self.screen.blit(
            self.xp_icon,
            (20, 55)
        )

        # XP amount

        xp_text = self.font.render(
            str(self.player.xp),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            xp_text,
            (60, 60)
        )

    # =====================
    # LOOP
    # =====================

    def run(self):

        while self.running:

            dt = self.clock.tick(FPS) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
