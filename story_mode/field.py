import random
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import os
import configparser

# Field class
class Field:
    def __init__(self, description, passable=True, enemies=None, coins=0):
        self.description = description
        self.enemies = enemies if enemies is not None else []
        self.coins = coins
        self.passable = passable


    def coin_field(self):
        self.description = "You found a coin field!"
        self.coins = random.randint(1, 10)  # Random coins between 1 and 10
        return self.coins
    
    def enemy_field(self, enemy):
        self.description = f"You encountered a {enemy.name}!"
        self.enemies.append(enemy)
        return self.enemies