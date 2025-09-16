import random
class Enemy:
    def __init__(self, name, health, attack, defense, enemy_heal):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.enemy_heal = enemy_heal

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0: #heatl below 0 prevention
            self.health = 0

    def is_alive(self):
        return self.health > 0
    
    def heal_enemy(self):
        heal_amount = random.randint(5, 15)
        self.health += heal_amount
        if self.health > 400:
            self.health = 400
        return heal_amount