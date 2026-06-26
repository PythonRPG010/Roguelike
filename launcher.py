import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
from entities.player import Player
import sys


class Launcher:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Roguelike Game")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        title = tk.Label(
            self.root,
            text="ROGUELIKE",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        tk.Button(
            self.root,
            text="Play",
            width=20,
            command=self.play_game
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Create Character",
            width=20,
            command=self.create_character
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Settings",
            width=20,
            command=self.settings
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Exit",
            width=20,
            command=self.root.destroy
        ).pack(pady=5)

    def get_character_list(self):

        Player.create_folders()

        characters = []

        for file in os.listdir(Player.PLAYER_FOLDER):

            if (
                file.endswith(".json")
                and not file.endswith("_inventory.json")
            ):
                characters.append(
                    file.replace(".json", "")
                )

        return sorted(characters)

    def create_character(self):

        nickname = simpledialog.askstring(
            "Create Character",
            "Nickname:"
        )

        if not nickname:
            return

        password = simpledialog.askstring(
            "Create Character",
            "Password:",
            show="*"
        )

        if not password:
            return

        path = os.path.join(
            Player.PLAYER_FOLDER,
            f"{nickname}.json"
        )

        if os.path.exists(path):

            messagebox.showerror(
                "Error",
                "Character already exists."
            )
            return

        player = Player(
            nickname=nickname,
            password=password
        )

        player.save()

        messagebox.showinfo(
            "Success",
            f"Character '{nickname}' created."
        )

    def play_game(self):

        nickname = simpledialog.askstring(
            "Login",
            "Character nickname:"
        )

        if not nickname:
            return

        password = simpledialog.askstring(
            "Login",
            "Password:",
            show="*"
        )

        if not password:
            return

        try:

            player = Player.load(nickname)

            if not player.verify_password(password):

                messagebox.showerror(
                    "Login Failed",
                    "Incorrect password."
                )
                return

            self.launch_game(player)

        except FileNotFoundError:

            messagebox.showerror(
                "Login Failed",
                "Character does not exist."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )
    def launch_game(self, player):

        self.root.destroy()

        game_path = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "main.py"
        )

        subprocess.Popen(
            [
                sys.executable,
                game_path,
                player.nickname
            ]
        )

    def settings(self):

        messagebox.showinfo(
            "Settings",
            "Settings menu coming soon."
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Launcher().run()
