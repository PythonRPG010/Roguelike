import os
import json
import uuid
import hashlib


class Player:
    SAVE_VERSION = 1

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    PLAYER_FOLDER = os.path.join(
        BASE_DIR,
        "data"
    )

    INVENTORY_FOLDER = os.path.join(
        BASE_DIR,
        "data"
    )

    DEFAULT_STATS = {
        "health": 100,
        "max_health": 100,

        "mana": 50,
        "max_mana": 50,

        "armor": 10,
        "attack": 10,

        "luck": 0,
        "agility": 0
    }

    def __init__(
        self,
        nickname,
        password,
        player_id=None,
        level=1,
        xp=0,
        money=0,
        stats=None
    ):
        self.create_folders()

        self.id = player_id or str(uuid.uuid4())

        self.nickname = nickname

        self.password_hash = self.hash_password(password)

        self.level = level
        self.xp = xp

        self.money = money

        self.stats = stats or self.DEFAULT_STATS.copy()

        self.inventory = []

        self.equipment = {
            "weapon": None,
            "helmet": None,
            "chestplate": None,
            "boots": None
        }

    # --------------------------------------------------
    # FOLDERS
    # --------------------------------------------------

    @classmethod
    def create_folders(cls):
        os.makedirs(cls.PLAYER_FOLDER, exist_ok=True)
        os.makedirs(cls.INVENTORY_FOLDER, exist_ok=True)

    # --------------------------------------------------
    # PASSWORDS
    # --------------------------------------------------

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(
            password.encode()
        ).hexdigest()

    def verify_password(self, password):
        return (
            self.hash_password(password)
            == self.password_hash
        )

    # --------------------------------------------------
    # PATHS
    # --------------------------------------------------

    @property
    def save_path(self):
        return os.path.join(
            self.PLAYER_FOLDER,
            f"{self.nickname}.json"
        )

    @property
    def inventory_path(self):
        return os.path.join(
            self.INVENTORY_FOLDER,
            f"{self.nickname}_inventory.json"
        )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    def save(self):

        player_data = {
            "save_version": self.SAVE_VERSION,

            "id": self.id,

            "nickname": self.nickname,

            "password_hash": self.password_hash,

            "level": self.level,
            "xp": self.xp,

            "money": self.money,

            "stats": self.stats
        }

        with open(
            self.save_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                player_data,
                file,
                indent=4
            )

        inventory_data = {
            "inventory": self.inventory,
            "equipment": self.equipment
        }

        with open(
            self.inventory_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                inventory_data,
                file,
                indent=4
            )

    # --------------------------------------------------
    # LOAD
    # --------------------------------------------------

    @classmethod
    def load(cls, nickname):

        player_path = os.path.join(
            cls.PLAYER_FOLDER,
            f"{nickname}.json"
        )

        if not os.path.exists(player_path):
            raise FileNotFoundError(
                f"Player '{nickname}' does not exist."
            )

        with open(
            player_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        player = cls(
            nickname=data["nickname"],
            password="temporary",
            player_id=data["id"],
            level=data["level"],
            xp=data["xp"],
            money=data["money"],
            stats=data["stats"]
        )

        player.password_hash = data["password_hash"]

        inventory_path = os.path.join(
            cls.INVENTORY_FOLDER,
            f"{nickname}_inventory.json"
        )

        if os.path.exists(inventory_path):

            with open(
                inventory_path,
                "r",
                encoding="utf-8"
            ) as file:

                inventory_data = json.load(file)

            player.inventory = inventory_data.get(
                "inventory",
                []
            )

            player.equipment = inventory_data.get(
                "equipment",
                {}
            )

        return player

    # --------------------------------------------------
    # INVENTORY
    # --------------------------------------------------

    def add_item(
        self,
        item_id,
        item_name,
        quantity=1
    ):

        for item in self.inventory:

            if item["id"] == item_id:

                item["quantity"] += quantity
                return

        self.inventory.append({
            "id": item_id,
            "name": item_name,
            "quantity": quantity
        })

    def remove_item(
        self,
        item_id,
        quantity=1
    ):

        for item in self.inventory:

            if item["id"] == item_id:

                item["quantity"] -= quantity

                if item["quantity"] <= 0:
                    self.inventory.remove(item)

                return True

        return False

    def has_item(
        self,
        item_id,
        quantity=1
    ):

        for item in self.inventory:

            if (
                item["id"] == item_id
                and item["quantity"] >= quantity
            ):
                return True

        return False

    # --------------------------------------------------
    # MONEY
    # --------------------------------------------------

    def add_money(self, amount):
        self.money += amount

    def spend_money(self, amount):

        if self.money >= amount:

            self.money -= amount
            return True

        return False

    # --------------------------------------------------
    # HEALTH
    # --------------------------------------------------

    def take_damage(self, damage):

        armor = self.stats["armor"]

        final_damage = max(
            damage - armor,
            0
        )

        self.stats["health"] -= final_damage

        if self.stats["health"] < 0:
            self.stats["health"] = 0

    def heal(self, amount):

        self.stats["health"] = min(
            self.stats["health"] + amount,
            self.stats["max_health"]
        )

    # --------------------------------------------------
    # MANA
    # --------------------------------------------------

    def use_mana(self, amount):

        if self.stats["mana"] >= amount:

            self.stats["mana"] -= amount
            return True

        return False

    def restore_mana(self, amount):

        self.stats["mana"] = min(
            self.stats["mana"] + amount,
            self.stats["max_mana"]
        )

    # --------------------------------------------------
    # XP
    # --------------------------------------------------

    def xp_to_next_level(self):
        return self.level * 100

    def add_xp(self, amount):

        self.xp += amount

        while self.xp >= self.xp_to_next_level():

            self.xp -= self.xp_to_next_level()

            self.level_up()

    def level_up(self):

        self.level += 1

        self.stats["max_health"] += 10
        self.stats["health"] += 10

        self.stats["max_mana"] += 5
        self.stats["mana"] += 5

        self.stats["attack"] += 2
        self.stats["armor"] += 1

        print(
            f"{self.nickname} reached level {self.level}!"
        )

    # --------------------------------------------------
    # MULTIPLAYER READY
    # --------------------------------------------------

    def to_dict(self):

        return {
            "id": self.id,
            "nickname": self.nickname,

            "level": self.level,
            "xp": self.xp,

            "money": self.money,

            "stats": self.stats,

            "inventory": self.inventory,

            "equipment": self.equipment
        }

    @classmethod
    def from_dict(cls, data):

        player = cls(
            nickname=data["nickname"],
            password="temporary",
            player_id=data["id"],
            level=data["level"],
            xp=data["xp"],
            money=data["money"],
            stats=data["stats"]
        )

        player.inventory = data["inventory"]
        player.equipment = data["equipment"]

        return player
