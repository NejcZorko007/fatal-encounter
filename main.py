import random
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import os
import configparser

#Main game Modules
from functions.shop import Shop
from freeplay.enemy import Enemy
from functions.player import Player
from story import Story

version = "b1.1.6"
#Removed time and pygame
    
#Main game Class
class BattleGame:
    hits = 0  #hit counter
    def __init__(self, root):
        self.immunity_rounds = 0
        self.root = root
        self.story = Story(root, self)  # Pass main instance to Story
        self.root.withdraw()


        self.pref_path = os.path.join(os.path.dirname(__file__), "./saves/pref.save")
        self.config = configparser.ConfigParser()
        self.init_pref_file()

        self.player_name = None
        self.selected_resolution = "800x600"  # Default resolution
        self.create_welcome_window()

    def init_pref_file(self):
        # file exsisting check
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
        # save function
        self.config.read(self.pref_path)
        self.config['coins']['coins'] = str(self.player.coins)
        with open(self.pref_path, 'w') as configfile:
            self.config.write(configfile)

    # Main menu
    def create_welcome_window(self):
        self.welcome_window = tk.Toplevel(self.root)
        self.welcome_window.title("Fatal Encounter")

        # Window Center Position
        window_width = 300
        window_height = 540
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.welcome_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        #Text, Image and Buttons 
        tk.Label(self.welcome_window, text="Fatal Encounter", font=("Arial", 16)).pack(pady=15)
        #self.image = PhotoImage(file="metall.png")
        #self.image = self.image.subsample(9, 9)
        #self.image2 = tk.Label(self.welcome_window, image=self.image)
        #self.image2.pack()
        tk.Label(self.welcome_window, text="Main Menu").pack(pady=20)
        tk.Button(self.welcome_window, text="Start Game", command=self.create_welcome_window2).pack(pady=10)
        tk.Button(self.welcome_window, text="Story Mode", command=self.story.start_story).pack(pady=10)
        tk.Button(self.welcome_window, text="Upgrades Shop", comman=self.shop).pack(pady=15)
        tk.Button(self.welcome_window, text="Settings", command=self.settings).pack(pady=15)
        tk.Button(self.welcome_window, text="Credits", command=self.credits_credits).pack(pady=15)
        tk.Button(self.welcome_window, text="Exit", command=self.root.quit).pack(pady=15)

    def settings(self):
        # Settings window for changing window size
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Fatal Encounter - Settings")
        self.settings_window.geometry("300x250")
        tk.Label(self.settings_window, text="Settings", font=("Arial", 14)).pack(pady=10)
        # Button for showing change notes
        tk.Button(self.settings_window, text="Change Notes", command=self.note_release).pack(pady=12)

    #Move active instantcs to story.py
    def story_mode(self):
        self.story = Story(self.root, self)  # Pass main instance to Story
        self.story.start_story()
        self.root.withdraw()  # Hide the main window while in story mode
        self.welcome_window.destroy()  # Close the welcome window

    def coming_soon(self): #Temporary function for unfinished features
        messagebox.showinfo("Coming Soon", "This feature is coming soon!")
    
    #Shop GUI
    def shop(self):
        self.shopwindow = tk.Toplevel(self.root)
        self.shopwindow.title("Fatal Encounter - Shop")
        self.shopwindow.geometry("300x250")
        tk.Label(self.shopwindow, text="Shop", font=("Arial", 14)).pack(pady=10)

        # Dropdown settings
        shop_var = tk.StringVar(value="Item Shop")
        shop_options = ["Item Shop", "Upgrades Shop"]
        tk.OptionMenu(self.shopwindow, shop_var, *shop_options).pack(pady=5)

        # coins label
        coins_value = self.player.coins if hasattr(self, 'player') else int(self.config.get('coins', 'coins', fallback='0'))
        self.shop_coins_label = tk.Label(self.shopwindow, text=f"Coins: {coins_value}", font=("Arial", 12))
        self.shop_coins_label.pack(pady=5)

        # choose menu
        def open_selected_shop():
            if shop_var.get() == "Item Shop":
                self.open_item_shop()
            else:
                self.upgrades_shop()

        tk.Button(self.shopwindow, text="Open Selected Shop", command=open_selected_shop).pack(pady=12)

        # coins auto-update
        self.update_shop_coins_label()
    
    #coins label update
    def update_shop_coins_label(self):
        # update in shop window if exsist
        if hasattr(self, 'shopwindow') and self.shopwindow.winfo_exists():
            coins_value = self.player.coins if hasattr(self, 'player') else int(self.config.get('coins', 'coins', fallback='0'))
            if hasattr(self, 'shop_coins_label'):
                self.shop_coins_label.config(text=f"Coins: {coins_value}")
            #scheduled update
            self.shopwindow.after(500, self.update_shop_coins_label)

    #item shop window logic
    def open_item_shop(self):
        self.item_shop_window = tk.Toplevel(self.root)
        self.item_shop_window.title("Item Shop")
        self.item_shop_window.geometry("300x450")

        tk.Label(self.item_shop_window, text="Item Shop", font=("Arial", 14)).pack(pady=10)

        # Always show coins value
        if hasattr(self, 'player'):
            coins_value = self.player.coins
        else:
            self.config.read(self.pref_path)
            try:
                coins_value = int(self.config.get('coins', 'coins', fallback='0'))
            except Exception:
                coins_value = 0
        tk.Label(self.item_shop_window, text=f"Coins: {coins_value}", font=("Arial", 12)).pack(pady=5)

        #item display with price
        for item, price in Shop.item_shop.items():
            tk.Label(self.item_shop_window, text=f"{item}: {price} coins").pack(pady=5)
            buy_button = tk.Button(self.item_shop_window, text="Buy", command=lambda item=item: self._buy_item(item)) #add buy to every item(add more items without needing to add more code for buttons)
            buy_button.pack(pady=2)

    def _buy_item(self, item):
        price = Shop.item_shop.get(item, None)
        #no price check
        if price is None:
            messagebox.showerror("Item Shop", "Item not found.")
            return
        # try to get coins value (class or save file)
        if hasattr(self, 'player'):
            coins = self.player.coins
        else:
            self.config.read(self.pref_path)
            try:
                coins = int(self.config.get('coins', 'coins', fallback='0'))
            except Exception:
                coins = 0
        #value check
        if coins < price:
            messagebox.showerror("Item Shop", f"Insufficient coins to buy {item}!")
            return
        coins -= price
        # Auto.save coins value to pref.save
        if hasattr(self, 'player'):
            self.player.coins = coins
            self.save_coins()
            self.update_health_labels()
        else:
            self.config['coins']['coins'] = str(coins)
            with open(self.pref_path, 'w') as configfile:
                self.config.write(configfile)
        #messagebox.showerror("Item Shop", f"Bought {item} for {price} coins!\n(Shop Service Offline: Item not delivered.)") #temporary service offline message

    #upgrades shop logic
    def upgrades_shop(self):
        self.upgrades_window = tk.Toplevel(self.root)
        self.upgrades_window.title("Upgrades Shop")
        self.upgrades_window.geometry("350x350")
        tk.Label(self.upgrades_window, text="Upgrades Shop", font=("Arial", 14)).pack(pady=10)

        # Load current upgrade levels from save file
        self.config.read(self.pref_path)
        upgrades = self.config['upgrades'] if 'upgrades' in self.config else {}
        sharpness_level = int(upgrades.get('Sharpness Upgrade', 0))
        shield_level = int(upgrades.get('Shield Upgrade', 0))

        # pull coins value from class or save file
        if hasattr(self, 'player'):
            coins_value = self.player.coins
        else:
            try:
                coins_value = int(self.config.get('coins', 'coins', fallback='0'))
            except Exception:
                coins_value = 0
        tk.Label(self.upgrades_window, text=f"Coins: {coins_value}", font=("Arial", 12)).pack(pady=5)

        # Sharpness upgrade logic
        tk.Label(self.upgrades_window, text=f"Sharpness Upgrade (Level {sharpness_level}/6)", font=("Arial", 12)).pack(pady=5)
        if sharpness_level < 6: #Max upgrade level
            price = Shop.upgrade_shop["Sharpness Upgrade"][sharpness_level]
            multiplier = Shop.upgrade_multipliers["Sharpness Upgrade"][sharpness_level]
            tk.Label(self.upgrades_window, text=f"Price: {price} | Multiplier: x{multiplier}").pack()
            tk.Button(self.upgrades_window, text="Buy", command=lambda: self.buy_upgrade("Sharpness Upgrade")).pack(pady=2)
        else:
            tk.Label(self.upgrades_window, text="Max Level Reached").pack()

        # Shield upgrade logic
        tk.Label(self.upgrades_window, text=f"Shield Upgrade (Level {shield_level}/5)", font=("Arial", 12)).pack(pady=5)
        if shield_level < 5: #Max upgrade level
            price = Shop.upgrade_shop["Shield Upgrade"][shield_level]
            multiplier = Shop.upgrade_multipliers["Shield Upgrade"][shield_level]
            tk.Label(self.upgrades_window, text=f"Price: {price} | Multiplier: x{multiplier}").pack()
            tk.Button(self.upgrades_window, text="Buy", command=lambda: self.buy_upgrade("Shield Upgrade")).pack(pady=2)
        else:
            tk.Label(self.upgrades_window, text="Max Level Reached").pack() #max limit reached text

    #Upgrade logic
    def buy_upgrade(self, upgrade_name):
        self.config.read(self.pref_path)
        upgrades = self.config['upgrades']
        level = int(upgrades.get(upgrade_name, 0))
        if level >= 6: #Max Upgrade Level
            messagebox.showinfo("Upgrade", "Max level reached!")
            return
        price = Shop.upgrade_shop[upgrade_name][level]
        # Get coins
        if hasattr(self, 'player'):
            coins = self.player.coins
        else:
            try:
                coins = int(self.config.get('coins', 'coins', fallback='0'))
            except Exception:
                coins = 0
        if coins < price:
            messagebox.showerror("Upgrade Shop", "Insufficient coins for upgrade!")
            return
        coins -= price
        level += 1
        upgrades[upgrade_name] = str(level)
        self.config['upgrades'] = upgrades
        self.config['coins']['coins'] = str(coins)
        with open(self.pref_path, 'w') as configfile:
            self.config.write(configfile)
        if hasattr(self, 'player'):
            self.player.coins = coins
            self.update_health_labels()
        messagebox.showinfo("Upgrade Shop", f"{upgrade_name} upgraded to level {level}!\nMultiplier: x{Shop.upgrade_multipliers[upgrade_name][level-1]}")
        self.upgrades_window.destroy()
        self.upgrades_shop()

    # Credits Window
    def credits_credits(self):
        self.welcome_window2 = tk.Toplevel(self.root)
        self.welcome_window2.title("Credits")
        self.welcome_window2.geometry("300x160")

        tk.Label(self.welcome_window2, text="Fatal Encounter", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.welcome_window2, text="Created by:").pack(padx=15)
        tk.Label(self.welcome_window2, text="Zmalajev And Zorko4288").pack(padx=16)
        tk.Label(self.welcome_window2, text=version).pack(padx=19)
        tk.Label(self.welcome_window2, text="BattleGame.com").pack(padx=16)

    #Release note Window
    def note_release(self):
        self.changenotes = tk.Toplevel(self.root)
        self.changenotes.title("Change Notes")
        self.changenotes.geometry("410x250")

        tk.Label(self.changenotes, text="Fatal Encounter", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.changenotes, text=f"For version: {version}").pack(padx=14)
        tk.Label(self.changenotes, text="Change Notes:").pack(padx=15)
        tk.Label(self.changenotes, text="- Added Story Mode").pack(padx=16)
        tk.Label(self.changenotes, text="- New item in Item Shop").pack(padx=16)
        tk.Label(self.changenotes, text="- Added map for Story Mode").pack(padx=16)
        tk.Label(self.changenotes, text="- Fixes to file saving").pack(padx=16)
        tk.Label(self.changenotes, text="- Removed change window size").pack(padx=16)
        tk.Label(self.changenotes, text="- Major Bug Fixes").pack(padx=16)
        tk.Label(self.changenotes, text="BattleGame.com").pack(padx=16)

    # Starting Window
    def create_welcome_window2(self):
        self.welcome_window2 = tk.Toplevel(self.root)
        self.welcome_window2.title("Fatal Encounter")
        self.welcome_window2.geometry("300x350")
        self.welcome_window.destroy()

        tk.Label(self.welcome_window2, text="Welcome to Fatal Encounter!", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.welcome_window2, text="Enter your character's name:").pack()

        self.player_name = tk.Entry(self.welcome_window2)
        self.player_name.pack(pady=5)

        tk.Label(self.welcome_window2, text="Enter your Enemy's name:").pack()

        self.enemy_name = tk.Entry(self.welcome_window2)
        self.enemy_name.pack(pady=5)

        tk.Button(self.welcome_window2, text="Start Game", command=self.start_game).pack(pady=10)
        tk.Button(self.welcome_window2, text="Back", command=self.back).pack(pady=15)

    #back button logic (for main game window)
    def back(self):
        self.welcome_window2.destroy()
        self.create_welcome_window()

    # Check for no name in value
    def start_game(self):
        self.player_name = self.player_name.get()
        self.enemy_name = self.enemy_name.get()
        if not self.player_name:    #return if player name = null
            messagebox.showerror("Error", "Please enter a valid name.")
            return

        if not self.enemy_name: #return if enemy name = null
            messagebox.showerror("Error", "Please enter a valid name.")
            return
        
        self.main_game_window(self.player_name, self.enemy_name, self.selected_resolution) #pass values to main game window
        self.welcome_window2.destroy()

    # Main Game Window
    def main_game_window(self, player_name, enemy_name, selected_resolution):
        self.root.deiconify()  # Ensure the root window is shown
        self.root.title("Fatal Encounter    (Main Game By Zmalajev, GUIed By Zorko4288)")

        # Load coins from save file
        self.config.read(self.pref_path)
        coins = 0
        try:
            coins = int(self.config.get('coins', 'coins', fallback='0'))
        except Exception:
            coins = 0

        # Load upgrades for ingame
        self.config.read(self.pref_path)
        upgrades = self.config['upgrades'] if 'upgrades' in self.config else {}
        sharpness_level = int(upgrades.get('Sharpness Upgrade', 0))
        shield_level = int(upgrades.get('Shield Upgrade', 0))
        sharpness_multiplier = Shop.upgrade_multipliers["Sharpness Upgrade"][sharpness_level-1] if sharpness_level > 0 else 1.0
        shield_multiplier = Shop.upgrade_multipliers["Shield Upgrade"][shield_level-1] if shield_level > 0 else 1.0

        self.player = Player(player_name, health=100, attack=int(25 * sharpness_multiplier), defense=int(10 * shield_multiplier), heal=0, coins=coins)
        self.enemy = Enemy(enemy_name, health=400, attack=30, defense=20, enemy_heal=0)
        # GUI
        self.info_label = tk.Label(self.root, text="BattleGame.com")
        self.info_label.pack()
        self.player_health_label = tk.Label(self.root, text=f"{self.player.name} 's HP: {self.player.health}")#display player health
        self.player_health_label.pack()
        # load coins value
        self.coins_label = tk.Label(self.root, text=f"Coins: {self.player.coins}")  # Show coins
        self.coins_label.pack()

        self.enemy_health_label = tk.Label(self.root, text=f"{self.enemy.name} 's HP: {self.enemy.health}")#display enemy health
        self.enemy_health_label.pack()

        self.action_frame = tk.Frame(self.root)#create frame for buttons
        self.action_frame.pack()

        self.attack_button = tk.Button(self.action_frame, text="Attack", command=self.attack)  # start attack function
        self.attack_button.pack(side="left", padx=10)

        self.heal_button = tk.Button(self.action_frame, text="Heal", command=self.heal)  # start heal function
        self.heal_button.pack(side="left", padx=10)

        self.defend_button = tk.Button(self.action_frame, text="Defend", command=self.defend)  # start defend function
        self.defend_button.pack(side="left", padx=10)

    #Update scripts
    #health label Updates
    def update_health_labels(self):
        # Only update labels if they still exist (window not destroyed)
        if hasattr(self, 'player_health_label') and self.player_health_label.winfo_exists():
            self.player_health_label.config(text=f"{self.player.name}'s HP: {self.player.health}")
        if hasattr(self, 'enemy_health_label') and self.enemy_health_label.winfo_exists():
            self.enemy_health_label.config(text=f"{self.enemy.name}'s HP: {self.enemy.health}")
        if hasattr(self, 'coins_label') and self.coins_label.winfo_exists():
            self.coins_label.config(text=f"Coins: {self.player.coins}")

    def inventory_update(self):
        pass  # Placeholder for future inventory updates

#Games Logic, Developed in corporation with Zorko4288 and Zmalajev inc.
    # Attack function
    def attack(self):
        if not self.player.is_alive() or not self.enemy.is_alive():#player/enemy alive check
            return
            
        # Attack Taktika
        damage = random.randint(self.player.attack - 2, self.player.attack + 2) - self.enemy.defense#bulj random damage(self.player.attack defined in start of main game window.)
        self.enemy.take_damage(damage)
        if damage < 0:
            damage = 0  #negative damage prevention
        
        messagebox.showinfo("Attack", f"{self.player.name} attacks {self.enemy.name} for {damage} damage!")
        BattleGame.hits += 1 #oneshot counter
        self.update_health_labels()#sent update request

        damagechance = random.randint(1, 5) #random critical hit
        if damagechance == 2:
            criticaldamage = random.randint(5, 15)#random critical damage value
            total_damage = criticaldamage + damage
            self.enemy.take_damage(criticaldamage)#send damage value
            messagebox.showinfo("Critical Hit", f"{self.player.name} attacks {self.enemy.name} with extra {criticaldamage} damage! Total damage: {total_damage}")

        if not self.enemy.is_alive():
            self.end_game(winner=self.player.name)
            return
        
        self.enemy_turn()

    #Heal Logic
    def heal(self):
        if not self.player.is_alive() or not self.enemy.is_alive():
            return
        
        superheal = random.randint(1, 3)

        if superheal == 3:
            superhealing_amount = random.randint(20, 30)
            self.player.health += superhealing_amount
            if self.player.health > 100:
                self.player.health = 100
            self.update_health_labels()
            messagebox.showinfo("Super Heal", f"{self.player.name} super heals for {superhealing_amount} health!")

        # Heal Taktika
        healing_amount = self.player.heal_player()#heal random value in player class
        self.update_health_labels()
        messagebox.showinfo("Heal", f"{self.player.name} heals for {healing_amount} health!")
        self.enemy_turn()    
    
    #Defend Logic
    def defend(self):
        if not self.player.is_alive() or not self.enemy.is_alive():
            return
        
        if self.immunity_rounds > 0:
            messagebox.showinfo("Defend", f"{self.player.name} already immune for {self.immunity_rounds} more rounds!")

        immunity_chance = random.randint(1, 20)
        if immunity_chance == 20:
            self.immunity_rounds = 3
            messagebox.showinfo("Immunity", f"{self.player.name} is immune for 3 rounds!")
        else:
            self.player.defense += 5
            messagebox.showinfo("Defend", f"{self.player.name} is defending this turn!")

        self.enemy_turn()
        # Defend Taktika
        if self.immunity_rounds == 0:
            self.player.defense -= 5

        self.update_health_labels()
 
    #Enemy AI
    def enemy_turn(self):
        if not self.player.is_alive() or not self.enemy.is_alive():#alive check
            return
        
        if self.immunity_rounds > 0:#check for immunity of player
            self.immunity_rounds -= 1
            messagebox.showinfo("Enemy Attack", f"{self.enemy.name} attacks, but {self.player_name} is immune!")
            return
        
        choise = random.randint(1, 3) #random enemy action choice
        print(choise) #debug print
        if choise == 1:
            damage = max(0, random.randint(self.enemy.attack - 2, self.enemy.attack + 2) - self.player.defense)
            self.player.take_damage(damage)
            messagebox.showinfo("Enemy Attack", f"{self.enemy.name} attacks {self.player.name} for {damage} damage!")
            self.update_health_labels()
        elif choise == 2:
            heal_amount = self.enemy.heal_enemy()
            messagebox.showinfo("Enemy Heal", f"{self.enemy.name} heals for {heal_amount} health!")
            self.update_health_labels()
        elif choise == 3:
            self.enemy.defense += 5
            messagebox.showinfo("Enemy Defend", f"{self.enemy.name} is defending this turn!")
            self.update_health_labels()


        if not self.player.is_alive():
            self.end_game(winner=self.enemy.name)
            self.update_health_labels()

    # End game function
    def end_game(self, winner):
        bonusreward = 0 #default value
        # Display the winner message
        if winner == self.player.name:
            reward = random.randint(200, 400) #random for coin reward
            messagebox.showinfo("Battle Over", f"{self.player.name} wins the battle!\nYou earned {reward} coins!")
            if BattleGame.hits == 1: #if player oneshuts enemy
                bonusreward = random.randint(500, 1000)
                messagebox.showinfo("Bonus", f"\nYou Receive {bonusreward} coins for oneshot!")
            else:
                pass
            self.player.coins += reward #add coins to player
            self.player.coins += bonusreward #add bonus coins for oneshot
            self.save_coins()#initiate autosave
            
        else:
            messagebox.showinfo("Battle Over", f"{self.player.name} has been defeated. {self.enemy.name} wins.")

        # autosave
        self.save_coins()

        # Destroy the main game window
        self.root.destroy()

        # Start Main Window
        self.root = tk.Tk()
        self.root.withdraw()
        self.create_welcome_window()

#Game loop
if __name__ == "__main__":
    root = tk.Tk()
    game = BattleGame(root)
    story = Story(game, root)
    root.mainloop()

#Used code
    #print("""# Create player and enemy objects
    #print("Welcome to the battle game!")
    #player_name = input("Enter your character's name: ")
    
    # Create player and enemy objects
    #player = Player(player_name, health=100, attack=25, defense=10, heal=0)
    #enemy = Enemy(name="Noatov tič", health=75, attack=20, defense=10)

    # Start the battle
    #battle(player, enemy)
    
          # Function to handle the battle
#def battle(player, enemy):
    #print(f"\n{player.name} encounters {enemy.name}!")
    #while player.is_alive() and enemy.is_alive():
        #print(f"\n{player.name}'s HP: {player.health} | {enemy.name}'s HP: {enemy.health}")
        #print("Choose an action:")
        #print("1. Attack")
        #print("2. Defend")
        #print("3. Heal")
        #choice = input("Enter 1, 2 or 3: ")

        #if choice == '1':  # Player attacks enemy
            #player.attack_enemy(enemy)
        #elif choice == '2':  # Player defends (no damage for this round)
            #print(f"{player.name} is defending this turn!")
        #elif choice == '3':  # Player heals
            #player.heal_player()
        #else:
            #print("Invalid choice. Please choose 1, 2, or 3.")
            #continue

        # Enemy attacks player after player's action
        #if enemy.is_alive():
            #time.sleep(1)  # Simulate time between actions
            #enemy.attack_player(player)

        #time.sleep(1)  # Pause between turns

    # Determine winner
    #if player.is_alive():
        #print(f"\n{player.name} wins the battle!")
    #else:
        #print(f"\n{player.name} has been defeated. {enemy.name} wins.")""")