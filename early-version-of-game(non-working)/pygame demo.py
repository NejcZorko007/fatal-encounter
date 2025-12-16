import random
import os
import configparser
import pygame
import sys


version = "b1.1.6"


class BattleGame:
    hits = 0

    def __init__(self):
        self.pref_path = os.path.join(os.path.dirname(__file__), "pref.save")
        self.config = configparser.ConfigParser()
        self.init_pref_file()
        pygame.init()
        pygame.font.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fatal Encounter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 28)
        self.running = True
        self.state = "start"
        self.player_name = ""
        self.enemy_name = ""
        self.input_active = None
        self.player = None
        self.enemy = None
        self.message = ""
        self.message_end_time = 0
        self.selected_resolution = "800x600"
        self.run()

    def init_pref_file(self):
        if not os.path.exists(self.pref_path):
            self.config['buyed_items'] = {}
            self.config['coins'] = {'coins': '0'}
            self.config['upgrades'] = {'Sharpness Upgrade': '0', 'Shield Upgrade': '0'}
            with open(self.pref_path, 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read(self.pref_path)
            changed = False
            if 'buyed_items' not in self.config:
                self.config['buyed_items'] = {}
                changed = True
            if 'coins' not in self.config:
                self.config['coins'] = {'coins': '0'}
                changed = True
            if 'upgrades' not in self.config:
                self.config['upgrades'] = {'Sharpness Upgrade': '0', 'Shield Upgrade': '0'}
                changed = True
            if changed:
                with open(self.pref_path, 'w') as configfile:
                    self.config.write(configfile)

    def save_coins(self):
        self.config.read(self.pref_path)
        if hasattr(self, 'player') and self.player is not None:
            self.config['coins']['coins'] = str(self.player.coins)
        with open(self.pref_path, 'w') as configfile:
            self.config.write(configfile)


    def set_message(self, text, duration=2000):
        self.message = text
        self.message_end_time = pygame.time.get_ticks() + duration

    def draw_text(self, text, x, y, font=None, color=(255, 255, 255)):
        if font is None:
            font = self.font
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def button(self, rect, text):
        mx, my = pygame.mouse.get_pos()
        clicked = False
        r = pygame.Rect(rect)
        color = (70, 130, 180) if r.collidepoint(mx, my) else (100, 149, 237)
        pygame.draw.rect(self.screen, color, r)
        self.draw_text(text, rect[0] + 10, rect[1] + 8)
        if r.collidepoint(mx, my) and pygame.mouse.get_pressed()[0]:
            clicked = True
        return clicked


    def render_start_screen(self):
        self.screen.fill((30, 30, 30))
        self.draw_text("Fatal Encounter", 300, 30, self.large_font)
        self.draw_text("Enter Player Name:", 50, 120)
        self.draw_text("Enter Enemy Name:", 50, 200)
        pygame.draw.rect(self.screen, (255, 255, 255), (250, 115, 400, 30), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (250, 195, 400, 30), 2)
        self.draw_text(self.player_name, 255, 118)
        self.draw_text(self.enemy_name, 255, 198)
        start_rect = (300, 280, 200, 40)
        if self.button(start_rect, "Start Game"):
            if self.player_name.strip() == "" or self.enemy_name.strip() == "":
                self.set_message("Please enter both names!", 1500)
            else:
                self.start_game_pygame(self.player_name.strip(), self.enemy_name.strip())
        self.draw_text("Click the boxes to type. Press Enter to confirm.", 50, 350)


    def render_game_screen(self):
        self.screen.fill((20, 20, 40))
        self.draw_text(f"{self.player.name}'s HP: {self.player.health}", 50, 30)
        self.draw_text(f"{self.enemy.name}'s HP: {self.enemy.health}", 50, 60)
        self.draw_text(f"Coins: {self.player.coins}", 600, 30)
        if self.button((120, 500, 150, 50), "Attack"):
            self.attack()
        if self.button((320, 500, 150, 50), "Heal"):
            self.heal()
        if self.button((520, 500, 150, 50), "Defend"):
            self.defend()
        if self.message and pygame.time.get_ticks() < self.message_end_time:
            self.draw_text(self.message, 50, 540, self.font, (255, 255, 0))
        elif pygame.time.get_ticks() >= self.message_end_time:
            self.message = ""


    def start_game_pygame(self, player_name, enemy_name):
        self.config.read(self.pref_path)
        coins = 0
        try:
            coins = int(self.config.get('coins', 'coins', fallback='0'))
        except Exception:
            coins = 0
        upgrades = self.config['upgrades'] if 'upgrades' in self.config else {}
        sharpness_level = int(upgrades.get('Sharpness Upgrade', 0))
        shield_level = int(upgrades.get('Shield Upgrade', 0))
        self.state = "game"
        self.set_message("Battle started!", 1200)
        BattleGame.hits = 0


    def update_health_labels(self):
        pass


    def attack(self):
        if not self.player.is_alive() or not self.enemy.is_alive():
            return
        damage = random.randint(self.player.attack - 2, self.player.attack + 2) - self.enemy.defense
        if damage < 0:
            damage = 0
        self.enemy.take_damage(damage)
        BattleGame.hits += 1
        self.set_message(f"{self.player.name} attacks {self.enemy.name} for {damage} damage!", 1500)
        damagechance = random.randint(1, 5)
        if damagechance == 2:
            criticaldamage = random.randint(5, 15)
            self.enemy.take_damage(criticaldamage)
            total_damage = criticaldamage + damage
            self.set_message(f"Critical! +{criticaldamage} damage (total {total_damage})", 1800)
        if not self.enemy.is_alive():
            self.end_game(winner=self.player.name)
            return
        pygame.time.set_timer(pygame.USEREVENT + 1, 300)


    def heal(self):
        if not self.player.is_alive() or not self.enemy.is_alive():
            return
        superheal = random.randint(1, 3)
        if superheal == 3:
            superhealing_amount = random.randint(20, 30)
            self.player.health += superhealing_amount
            if self.player.health > 100:
                self.player.health = 100
            self.set_message(f"{self.player.name} super heals for {superhealing_amount}!", 1500)
        healing_amount = self.player.heal_player()
        self.set_message(f"{self.player.name} heals for {healing_amount} health!", 1500)
        pygame.time.set_timer(pygame.USEREVENT + 1, 300)


    def defend(self):
        if not self.player.is_alive() or not self.enemy.is_alive():
            return
        if self.immunity_rounds > 0:
            self.set_message(f"{self.player.name} already immune for {self.immunity_rounds} rounds!", 1500)
            return
        immunity_chance = random.randint(1, 20)
        if immunity_chance == 20:
            self.immunity_rounds = 3
            self.set_message(f"{self.player.name} is immune for 3 rounds!", 1500)
        else:
            self.player.defense += 5
            self.set_message(f"{self.player.name} is defending this turn!", 1200)
        pygame.time.set_timer(pygame.USEREVENT + 1, 300)


    def enemy_turn(self):
        if not self.player.is_alive() or not self.enemy.is_alive():
            return
        if self.immunity_rounds > 0:
            self.immunity_rounds -= 1
            self.set_message(f"{self.enemy.name} attacks, but {self.player.name} is immune!", 1400)
            return
        damage = max(0, random.randint(self.enemy.attack - 2, self.enemy.attack + 2) - self.player.defense)
        self.player.take_damage(damage)
        self.set_message(f"{self.enemy.name} attacks {self.player.name} for {damage} damage!", 1400)
        if self.player.defense > 10 and self.immunity_rounds == 0:
            self.player.defense = max(0, self.player.defense - 5)
        if not self.player.is_alive():
            self.end_game(winner=self.enemy.name)


    def end_game(self, winner):
        bonusreward = 0
        if winner == self.player.name:
            reward = random.randint(200, 400)
            if BattleGame.hits == 1:
                bonusreward = random.randint(500, 1000)
            self.player.coins += reward
            self.player.coins += bonusreward
            self.save_coins()
            self.set_message(f"{self.player.name} wins! +{reward} coins (bonus {bonusreward})", 2500)
        else:
            self.set_message(f"{self.player.name} has been defeated. {self.enemy.name} wins.", 2500)
        self.save_coins()
        pygame.time.set_timer(pygame.USEREVENT + 2, 2000)


    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if self.state == "start":
                        if event.key == pygame.K_TAB:
                            if self.input_active == "player":
                                self.input_active = "enemy"
                            else:
                                self.input_active = "player"
                        elif event.key == pygame.K_RETURN:
                            if self.player_name.strip() and self.enemy_name.strip():
                                self.start_game_pygame(self.player_name.strip(), self.enemy_name.strip())
                            else:
                                self.set_message("Both names required", 1200)
                        elif event.key == pygame.K_BACKSPACE:
                            if self.input_active == "player":
                                self.player_name = self.player_name[:-1]
                            elif self.input_active == "enemy":
                                self.enemy_name = self.enemy_name[:-1]
                        else:
                            char = event.unicode
                            if self.input_active == "player" and len(self.player_name) < 20:
                                self.player_name += char
                            elif self.input_active == "enemy" and len(self.enemy_name) < 20:
                                self.enemy_name += char
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "start":
                        mx, my = event.pos
                        if 250 <= mx <= 650 and 115 <= my <= 145:
                            self.input_active = "player"
                        elif 250 <= mx <= 650 and 195 <= my <= 225:
                            self.input_active = "enemy"
                if event.type == pygame.USEREVENT + 1:
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    self.enemy_turn()
                if event.type == pygame.USEREVENT + 2:
                    pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                    self.state = "start"
                    self.player_name = ""
                    self.enemy_name = ""
                    self.player = None
                    self.enemy = None
            if self.state == "start":
                self.render_start_screen()
            elif self.state == "game":
                self.render_game_screen()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()



if __name__ == "__main__":
    game = BattleGame()
