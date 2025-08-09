import random
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import os
from story_mode.field import Field
import configparser

# Field class
class Map:
    #Map initialization
    def __init__(self, fields):
        water = Field("Water", passable=False)
        dirt = Field("Dirt", passable=True)
        coin_field = Field("Coin Field", passable=True)
        enemy_field = Field("Enemy Field", passable=True)

        self.map = [
            [fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7]]
            [fields[8], fields[9], fields[10], fields[11], fields[12], fields[13], fields[14], fields[15]],
            [fields[16], fields[17], fields[18], fields[19], fields[20], fields[21], fields[22], fields[23]],
            [fields[24], fields[25], fields[26], fields[27], fields[28], fields[29], fields[30], fields[31]],
            [fields[32], fields[33], fields[34], fields[35], fields[36], fields[37], fields[38], fields[39]],
            [fields[40], fields[41], fields[42], fields[43], fields[44], fields[45], fields[46], fields[47]],
            [fields[48], fields[49], fields[50], fields[51], fields[52], fields[53], fields[54], fields[55]],
            [fields[56], fields[57], fields[58], fields[59], fields[60], fields[61], fields[62], fields[63]]
        ]
        self.current_position = (0, 0)
        self.width = len(self.map[0])
        self.height = len(self.map)
    #Movement
    def move(self, direction):
        x, y = self.current_position
        if direction == "up" and x > 0:
            self.current_position = (x - 1, y)
        elif direction == "down" and x < self.height - 1:
            self.current_position = (x + 1, y)
        elif direction == "left" and y > 0:
            self.current_position = (x, y - 1)
        elif direction == "right" and y < self.width - 1:
            self.current_position = (x, y + 1)
    #Current field
    def get_current_field(self):
        x, y = self.current_position
        return self.map[x][y]
    #Field Limit Check (FLC)
    def field_limit(self, x, y):
        if 0 <= x < self.height and 0 <= y < self.width:
            return self.map[x][y]
        else:
            raise IndexError("Field coordinates out of bounds")
    #Field block description get
    def get_field_description(self):
        x, y = self.current_position
        return self.map[x][y].description if self.map[x][y] else "No field description available"
    #Get Field Enemies
    def get_field_enemies(self):
        x, y = self.current_position
        return self.map[x][y].enemies if self.map[x][y] else []
    
    #def field_shop(self):
    #   x, y = self.current_position
    #  return self.map[x][y].shop if self.map[x][y] else None

    def get_field_items(self):
        x, y = self.current_position
        return self.map[x][y].items if self.map[x][y] else []
