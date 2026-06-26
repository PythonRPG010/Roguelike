import pygame
import random
import os


class GameMap:
    TILE_SIZE = 32
    WIDTH = 128
    HEIGHT = 64

    WALL = "#"
    FLOOR = "."

    # =========================
    # ROOM STRUCTURE
    # =========================

    class Room:
        def __init__(self, x, y, w, h):
            self.x = x
            self.y = y
            self.w = w
            self.h = h

        def center(self):
            return (
                self.x + self.w // 2,
                self.y + self.h // 2
            )

        def intersects(self, other):
            return not (
                self.x + self.w < other.x or
                self.x > other.x + other.w or
                self.y + self.h < other.y or
                self.y > other.y + other.h
            )

    # =========================
    # INIT
    # =========================

    def __init__(self):

        BASE_DIR = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.ASSET_FOLDER = os.path.join(
            BASE_DIR,
            "assets"
        )

        self.tiles = {}
        self.load_textures()

        self.MAP = [
            [self.WALL for _ in range(self.WIDTH)]
            for _ in range(self.HEIGHT)
        ]

        self.walls = []

        self.rooms = []

        self.generate_map()
        self.generate_collisions()

    # =========================
    # SPAWNS
    # =========================

    def get_random_spawn_position(self, entity_size=30):

        floor_tiles = []

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.MAP[y][x] == self.FLOOR:
                    floor_tiles.append((x, y))

        random.shuffle(floor_tiles)

        for tile_x, tile_y in floor_tiles:

            px = tile_x * self.TILE_SIZE + (
                self.TILE_SIZE - entity_size
            ) // 2

            py = tile_y * self.TILE_SIZE + (
                self.TILE_SIZE - entity_size
            ) // 2

            test_rect = pygame.Rect(
                px,
                py,
                entity_size,
                entity_size
            )

            collision = False

            for wall in self.walls:
                if test_rect.colliderect(wall):
                    collision = True
                    break

            if not collision:
                return px, py

        return 64, 64

    def get_random_item_position(self, item_size=24):

        floor_tiles = []

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.MAP[y][x] == self.FLOOR:
                    floor_tiles.append((x, y))

        tile_x, tile_y = random.choice(floor_tiles)

        return (
            tile_x * self.TILE_SIZE +
            (self.TILE_SIZE - item_size) // 2,

            tile_y * self.TILE_SIZE +
            (self.TILE_SIZE - item_size) // 2
        )

    # =========================
    # TEXTURES
    # =========================

    def load_textures(self):
        self.tiles = {
            self.WALL: self.load_texture("wall.png"),
            self.FLOOR: self.load_texture("floor.png")
        }

    def load_texture(self, filename):
        path = os.path.join(
            self.ASSET_FOLDER,
            filename
        )

        try:
            texture = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(
                texture,
                (self.TILE_SIZE, self.TILE_SIZE)
            )
        except Exception:
            surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            surf.fill((30, 30, 30))
            return surf

    # =========================
    # BSP GENERATION
    # =========================

    def generate_map(self):
        self.rooms = []
        self._init_walls()

        root = self._bsp_partition(
            1, 1,
            self.WIDTH - 2,
            self.HEIGHT - 2,
            depth=5
        )

        leaves = []
        self._collect_leaves(root, leaves)

        for leaf in leaves:
            room = self._create_room_in_leaf(leaf)
            if room:
                self._carve_room(room)
                self.rooms.append(room)

        self._connect_rooms()

        room = self._create_room_in_leaf(leaf)
        if room:
            self._carve_room(room)
            self.rooms.append(room)
        if not self.rooms:
            self._force_simple_room()

    # =========================
    # BSP NODE
    # =========================

    class Node:
        def __init__(self, x, y, w, h):
            self.x = x
            self.y = y
            self.w = w
            self.h = h
            self.left = None
            self.right = None
            self.room = None

    def _bsp_partition(self, x, y, w, h, depth):

        node = self.Node(x, y, w, h)

        if depth <= 0 or w < 10 or h < 10:
            return node

        split_h = random.choice([True, False])

        if w > h and w / h >= 1.25:
            split_h = False
        elif h > w and h / w >= 1.25:
            split_h = True

        if split_h:
            split = random.randint(int(h * 0.3), int(h * 0.7))
            node.left = self._bsp_partition(x, y, w, split, depth - 1)
            node.right = self._bsp_partition(x, y + split, w, h - split, depth - 1)
        else:
            split = random.randint(int(w * 0.3), int(w * 0.7))
            node.left = self._bsp_partition(x, y, split, h, depth - 1)
            node.right = self._bsp_partition(x + split, y, w - split, h, depth - 1)

        return node

    def _collect_leaves(self, node, leaves):
        if node is None:
            return
        if node.left is None and node.right is None:
            leaves.append(node)
        else:
            self._collect_leaves(node.left, leaves)
            self._collect_leaves(node.right, leaves)

    # =========================
    # ROOMS
    # =========================

    def _create_room_in_leaf(self, leaf):

        min_room_size = 4

        # ensure leaf is big enough
        if leaf.w < min_room_size + 2 or leaf.h < min_room_size + 2:
            return None

        max_w = leaf.w - 2
        max_h = leaf.h - 2

        if max_w < min_room_size or max_h < min_room_size:
            return None

        rw = random.randint(min_room_size, max_w)
        rh = random.randint(min_room_size, max_h)

        max_rx = leaf.x + leaf.w - rw - 1
        max_ry = leaf.y + leaf.h - rh - 1

        min_rx = leaf.x + 1
        min_ry = leaf.y + 1

        if max_rx < min_rx or max_ry < min_ry:
            return None

        rx = random.randint(min_rx, max_rx)
        ry = random.randint(min_ry, max_ry)

        return self.Room(rx, ry, rw, rh)

    def _carve_room(self, room):
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                self.MAP[y][x] = self.FLOOR

    # =========================
    # CONNECTIONS
    # =========================

    def _connect_rooms(self):

        if not self.rooms:
            return

        for i in range(len(self.rooms) - 1):
            x1, y1 = self.rooms[i].center()
            x2, y2 = self.rooms[i + 1].center()

            if random.random() < 0.5:
                self._carve_h_corridor(x1, x2, y1)
                self._carve_v_corridor(y1, y2, x2)
            else:
                self._carve_v_corridor(y1, y2, x1)
                self._carve_h_corridor(x1, x2, y2)

    def _carve_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.MAP[y][x] = self.FLOOR

    def _carve_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.MAP[y][x] = self.FLOOR

    # =========================
    # COLLISIONS
    # =========================

    def generate_collisions(self):
        self.walls.clear()

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.MAP[y][x] == self.WALL:
                    self.walls.append(
                        pygame.Rect(
                            x * self.TILE_SIZE,
                            y * self.TILE_SIZE,
                            self.TILE_SIZE,
                            self.TILE_SIZE
                        )
                    )

    # =========================
    # DRAW
    # =========================

    def draw(self, screen, camera_x=0, camera_y=0):

        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):

                tile = self.MAP[y][x]
                tex = self.tiles.get(tile)

                if tex:
                    screen.blit(
                        tex,
                        (
                            x * self.TILE_SIZE - camera_x,
                            y * self.TILE_SIZE - camera_y
                        )
                    )

    # =========================
    # UTILS
    # =========================

    def _init_walls(self):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self.MAP[y][x] = self.WALL

    def _in_bounds(self, x, y):
        return 0 < x < self.WIDTH - 1 and 0 < y < self.HEIGHT - 1
