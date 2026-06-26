import pygame
import os


class Item:

    SIZE = 8
    TEXTURE_CACHE = {}

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    ASSET_FOLDER = os.path.join(BASE_DIR, "assets")

    def __init__(
        self,
        x,
        y,
        item_type,
        amount=1,
        rarity="common",
        stackable=True
    ):

        self.x = x
        self.y = y

        self.item_type = item_type.lower()

        self.amount = amount

        self.rarity = rarity

        self.stackable = stackable

        self.collected = False

        self.rect = pygame.Rect(
            x,
            y,
            self.SIZE,
            self.SIZE
        )

        self.texture = self.load_texture()

    def update(self, player_rect, player):

        if self.collected:
            return False

        if not self.rect.colliderect(player_rect):
            return False

        self.collect(player)

        return True

    def collect(self, player):

        item_type = self.item_type

        # -------------------------
        # MONEY
        # -------------------------

        if item_type in ("money", "coin", "coins", "gold"):

            player.add_money(self.amount)

        # -------------------------
        # XP
        # -------------------------

        elif item_type in ("xp", "experience"):

            player.add_xp(self.amount)

        # -------------------------
        # INVENTORY ITEM
        # -------------------------

        else:

            player.add_item(
                item_id=item_type,
                item_name=item_type.replace("_", " ").title(),
                quantity=self.amount
            )

        player.save()

        self.collected = True

    def draw(
        self,
        screen,
        camera_x=0,
        camera_y=0
    ):

        if self.collected:
            return

        screen.blit(
        self.texture,
            (
                self.x - camera_x,
                self.y - camera_y
            )
        )

    def load_texture(self):

        filename = f"{self.item_type}.png"

        if filename in self.TEXTURE_CACHE:
            return self.TEXTURE_CACHE[filename]

        path = os.path.join(
            self.ASSET_FOLDER,
            filename
        )

        try:

            texture = pygame.image.load(
                path
            ).convert_alpha()

            texture = pygame.transform.scale(
                texture,
                (self.SIZE, self.SIZE)
            )

        except Exception as e:
            print(f"[ITEM LOAD ERROR] {path} -> {e}")

            texture = pygame.Surface(
                (self.SIZE, self.SIZE),
                pygame.SRCALPHA
            )
            texture.fill((255, 0, 255))

        self.TEXTURE_CACHE[filename] = texture

        return texture

    def to_dict(self):

        return {
            "x": self.x,
            "y": self.y,
            "item_type": self.item_type,
            "amount": self.amount,
            "rarity": self.rarity,
            "stackable": self.stackable
        }
