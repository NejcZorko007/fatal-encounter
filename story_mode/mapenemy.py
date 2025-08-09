# Map enemy class
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import os
import configparser

class Enemy:
    def __init__(self, name, health, attack, defense,):
        enemy_names = ["Goblin", "Orc", "Troll", "Dragon", "Vampire"]
        self.name = enemy_names[random.randint(0, len(enemy_names) - 1)]
        self.health = health
        self.attack = attack
        self.defense = defense

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0