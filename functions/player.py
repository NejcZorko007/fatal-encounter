import random
class Player:
    def __init__(self, name, health, attack, defense, heal, coins=0):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.heal = heal
        self.coins = coins  # added attribute

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0
    
    def heal_player(self):
        healing_amount = random.randint(5, 15)
        self.health += healing_amount
        if self.health > 100:
            self.health = 100
        return healing_amount