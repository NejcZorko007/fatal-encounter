import random
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import os
import configparser

class Story:
    def __init__(self, root, main_instance):
        self.root = root
        self.pref_path = os.path.join(os.path.dirname(__file__),"./saves/story.save")
        self.config = configparser.ConfigParser()
        self.init_pref_file()

    def init_pref_file(self):
        # file exsisting check
        if not os.path.exists(self.pref_path):
            self.config['story_active'] = {'story_active': 'False'}
            self.config['position'] = {'position': '0, 0'}
            self.config['enemy_dead_block'] = {'enemy_dead_block': ''}
            with open(self.pref_path, 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read(self.pref_path)
            changed = False
            if 'story_active' not in self.config:
                self.config['story_active'] = {}
                changed = True
            if 'position' not in self.config:
                self.config['position'] = {'position': '0, 0'}
                changed = True
            if 'enemy_dead_block' not in self.config:
                self.config['enemy_dead_block'] = {'enemy_dead_block': ''}
                changed = True
            if changed:
                with open(self.pref_path, 'w') as configfile:
                    self.config.write(configfile)
            
    #def back(self):
    #    import main
    #    self.main = main.BattleGame(self.root)
    #    self.story_welcome.destroy()

    def start_story(self):
    # New story window
        self.story_welcome = tk.Toplevel(self.root)
        self.story_welcome.title("Story Mode")
        self.story_welcome.geometry("300x350")

        tk.Label(self.story_welcome, text="Welcome to Story Mode!", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.story_welcome, text="Enter your character's name:").pack()

        self.player_name = tk.Entry(self.story_welcome)
        self.player_name.pack(pady=5)

        tk.Button(self.story_welcome, text="Start Game", command="").pack(pady=10)
        tk.Button(self.story_welcome, text="Back", command=self.story_welcome.destroy).pack(pady=15)

        