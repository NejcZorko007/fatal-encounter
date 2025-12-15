import sys
import pygame
import random
import json
import os
import time
from typing import Literal
from tkinter import messagebox
from pygame import mixer
# ----------------- GAME IMPORTS (with Fallback) -------------------
try:
    from functions.shop import Shop
    from functions.player import Player
    from functions.enemy import Enemy
    import functions.config as config
    print("External game functions imported successfully.")
except Exception:#if import fails, user fallback for player/enemy config
    class Placeholder:
        def __init__(self, name, health, attack, defense, heal_amount=10, coins=0):
            self.name = name
            self.health = health
            self.max_health = health
            self.attack = attack
            self.defense = defense
            self._heal_amount = heal_amount
            self.coins = coins

        def is_alive(self):
            return self.health > 0

        def take_damage(self, damage):
            self.health = max(0, self.health - damage)

        def heal_player(self):
            heal_amount = self._heal_amount
            self.health = min(self.max_health, self.health + heal_amount)
            return heal_amount

        def attack_enemy(self, target):
            # simple attack calculation
            base = random.randint(max(0, self.attack - 2), self.attack + 2)
            damage = max(0, base - getattr(target, "defense", 0))
            target.take_damage(damage)
            return damage

    Player = Placeholder
    Enemy = Placeholder

    class ConfigPlaceholder:
        player = None
        enemy = None

    config = ConfigPlaceholder()
    print("WARNING: Using placeholder Player/Enemy/Config classes (functions.* not found).")

# ----------------- START OF CONFIG -------------------
version = "b1.1.7 (Pygame Demo Fixed)"
hits = 0
enemy_turn_pending = False

pygame.init()
# Safe mixer init
try:
    pygame.mixer.init()
except pygame.error:
    print("Warning: Mixer failed to initialize. Audio will be disabled.")

# Global entities and data storage
player = None #player entity
enemy = None #enemy entity
health_player = None #health label surfaces
health_enemy = None 
log_text = "Welcome to Fatal Encounter!"#log text shown in battle
immunity_rounds = 0 #immunity for chance of immunity

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fatal Encounter - Fixed Demo")

# Loading bar setup
BAR_WIDTH = 600
BAR_HEIGHT = 40
bar_x = WIDTH // 2 - BAR_WIDTH // 2
bar_y = HEIGHT // 2

# Colors
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GREEN = (50, 205, 50)
DARK_GREEN = (34, 139, 34)
GRAY = (60, 60, 60)
BUTTON_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 160, 210)
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

# Credits config
CREDITS_FPS = 90
SCROLL_SPEED = 0.4
LINE_SPACING = 30
CREDITS_CONTENT = [
    "A Game By",
    "-------------------",
    "Zmalajev Inc. and BattleGame Studios",
    "",
    "Project Lead",
    "Žiga Plevel",
    "",
    "Lead Developers",
    "NejcZorko007",
    "",
    "Year of Creation",
    "2024",
    "",
    "--- MUSIC & SOUND ---",
    "Menu Music: Mergatroid | 8-Bit Sound",
    "Credits Music: Dinner Set | Jazz",
    "Game Music: Winners-Rock",
    "",
    "All music was recorded from a Roland D-110 Sound Module.",
    "Used with permission from zorko4288.",
    "",
    "--- END OF PRODUCTION ---",
    "Thank You For Playing Beta!",
    "-------------------",
    "", "", "", "", "", ""
]

# Fonts
title_font = pygame.font.SysFont("Consolas", 64)
version_font = pygame.font.SysFont("Consolas", 18)
button_font = pygame.font.SysFont("Consolas", 28)
font_large = pygame.font.SysFont("Consolas", 43)
font_small = pygame.font.SysFont("Consolas", 24)
notes_font = pygame.font.SysFont("Consolas", 15)

#main menu buttons
buttons = {
    "Start": pygame.Rect(WIDTH // 2 - 100, 250, 200, 60),# positions: x, y, width, height
    "Settings": pygame.Rect(WIDTH // 2 - 100, 350, 200, 60),
    "Quit": pygame.Rect(WIDTH // 2 - 100, 450, 200, 60)
}

#main game screen buttons
game_screen = {
    "Attack": pygame.Rect(WIDTH // 2 - 320, 400, 180, 50),  # moved up 50 px, smaller size
    "Heal": pygame.Rect(WIDTH // 2 - 100, 400, 180, 50),
    "Defend": pygame.Rect(WIDTH // 2 + 120, 400, 180, 50)
}

#player name input boxes init
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = font_small.render(text, True, WHITE)
        self.active = False

    def handle_event(self, event):#events for input box
        # check for mouse click in or out of box
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                if self.text in ("Player Name", "Enemy Name"):
                    self.text = ""
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            self.txt_surface = font_small.render(self.text, True, WHITE)

        # Keyboard input when active
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = COLOR_INACTIVE
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20:
                    self.text += event.unicode
            self.txt_surface = font_small.render(self.text, True, WHITE)

    def update_text(self):#input box text update
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw_text(self, surf):#inputbox draw
        self.update_text()
        surf.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 6))
        pygame.draw.rect(surf, self.color, self.rect, 2)

# initialize boxes
input_box_player = InputBox(WIDTH // 2 - 100, 200, 200, 36, text='Player Name')#input box positions and small text
input_box_enemy = InputBox(WIDTH // 2 - 100, 280, 200, 36, text='Enemy Name')
name_input_confirm_button = pygame.Rect(WIDTH // 2 - 100, 340, 200, 48)#buttons config
name_input_back_button = pygame.Rect(WIDTH // 2 - 100, 520, 200, 60)

# ----------------- Audio / Paths -----------------
ASSET_DIR = "Audio/Menu-music"
MENU_MUSIC = os.path.join(ASSET_DIR, "8-Bit-Sound.wav")
GAME_MUSIC = os.path.join(ASSET_DIR, "Winners-Rock.wav")
CREDITS_MUSIC = os.path.join(ASSET_DIR, "Jazz.wav")
SFX_HIT = None# placeholder; can load if available

def safe_music_load(path):#music exsists check
    try:
        mixer.music.load(path)
        return True
    except Exception:
        print(f"Warning: failed to load music: {path}")
        return False
# ----------------- Utility: Save/Load last player names ----------------- (Made to remember the last used names)
SAVE_FILE = "fe_last.json"

def save_last_players(pname, ename):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"player": pname, "enemy": ename}, f)#write to json
    except Exception:
        pass

def load_last_players():#load from json
    if not os.path.exists(SAVE_FILE):
        return None, None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            return d.get("player"), d.get("enemy")
    except Exception:
        return None, None

# ----------------- Drawing Helpers ----------------- (loading screen, Primary)
def draw_loading_screen(text, progress):
    screen.fill(BLACK)
    title_text = font_large.render(text, True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 160))#centered text
    # bar background
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT), border_radius=8)# draw bar bg
    # progress
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, BAR_WIDTH * (progress / 100), BAR_HEIGHT), border_radius=8)# draw progress
    pygame.draw.rect(screen, DARK_GREEN, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT), 3, border_radius=8)# border
    percent_text = font_small.render(f"Loading... {int(progress)}%", True, WHITE)# percent text
    screen.blit(percent_text, (WIDTH // 2 - percent_text.get_width() // 2, bar_y + BAR_HEIGHT + 10))#centered percent
    pygame.display.flip()#update screen

def loading_screen(text, duration=1.5):
    clock = pygame.time.Clock()
    progress = 0
    while progress <= 100:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        draw_loading_screen(text, progress)
        progress += 1.5 #progress for %
        clock.tick(144)
    # small pause
    t0 = time.time()
    while time.time() - t0 < duration:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

# ----------------- Screen Drawers -----------------
def draw_menu():#main menu draw
    screen.fill(BLACK)
    title_text = title_font.render("Fatal Encounter", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
    version_text = version_font.render(f"Version: {version}", True, WHITE)
    screen.blit(version_text, (10, 10))
    mouse_pos = pygame.mouse.get_pos()
    for text, rect in buttons.items():
        color = HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)# draw button
        bt = button_font.render(text, True, WHITE)
        screen.blit(bt, (rect.x + rect.width // 2 - bt.get_width() // 2, rect.y + rect.height // 2 - bt.get_height() // 2))

def draw_settings():#settings screen draw
    screen.fill(BLACK)
    title_text = title_font.render("Settings", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))

    mouse_pos = pygame.mouse.get_pos()

    back_button = pygame.Rect(WIDTH // 2 - 100, 450, 200, 60)#button config
    credits_button = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)
    change_note_button = pygame.Rect(WIDTH // 2 - 100, 250, 200, 60)

    for rect, label in [# buttons
        (back_button, "Back"),
        (credits_button, "Credits"),
        (change_note_button, "Change Notes")
    ]:
        color = HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)
        txt = button_font.render(label, True, WHITE)
        screen.blit(txt, (rect.x + rect.width // 2 - txt.get_width() // 2,
                          rect.y + rect.height // 2 - txt.get_height() // 2))

    return back_button, credits_button, change_note_button #return buttons for event handling

def draw_change_notes():#change notes
    screen.fill(BLACK)
    title_text = title_font.render("Change Notes", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))

    notes = [#da notes
        "- Pygame in full effect (fixed demo)",
        "- converted parts of code from previous versions to work with pygame",
        "- Improved state logic",
        "- Added basic save for last names",
        "- Fixed a huge load of bugs, that came with pygame (inc. battle load and screen fix)",
        "- added timeout while enemy turn, to prevent spam attack",
        "- improved ui",
        "",
        "Press Back to return."
    ]

    for i, line in enumerate(notes):
        txt = notes_font.render(line, True, LIGHT_GRAY)#font and color.. p.s, size change with font number5
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 180 + i * 40))

    #back button
    back_button = pygame.Rect(WIDTH // 2 - 100, 500, 200, 60)
    mouse_pos = pygame.mouse.get_pos()
    color = HOVER_COLOR if back_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, back_button, border_radius=10)
    bt = button_font.render("Back", True, WHITE)
    screen.blit(bt, (back_button.x + back_button.width // 2 - bt.get_width() // 2,
                     back_button.y + back_button.height // 2 - bt.get_height() // 2))

    return back_button

def draw_name_input_screen():
    screen.fill(BLACK)
    title_text = title_font.render("Enter Names", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 40))

    lbl_player = button_font.render("Your Name:", True, WHITE)
    screen.blit(lbl_player, (input_box_player.rect.x, input_box_player.rect.y - 30))
    lbl_enemy = button_font.render("Enemy Name:", True, WHITE)
    screen.blit(lbl_enemy, (input_box_enemy.rect.x, input_box_enemy.rect.y - 30))

    input_box_player.draw_text(screen)
    input_box_enemy.draw_text(screen)

    mouse_pos = pygame.mouse.get_pos()

    # Confirm button
    color = HOVER_COLOR if name_input_confirm_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, name_input_confirm_button, border_radius=10)
    bt = button_font.render("Confirm", True, WHITE)
    screen.blit(bt, (name_input_confirm_button.x + name_input_confirm_button.width // 2 - bt.get_width() // 2,
                     name_input_confirm_button.y + name_input_confirm_button.height // 2 - bt.get_height() // 2))

    # REAL back button
    back_button = pygame.Rect(WIDTH // 2 - 100, 450, 200, 60)
    bcol = HOVER_COLOR if back_button.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, bcol, back_button, border_radius=10)
    bt2 = button_font.render("Back", True, WHITE)
    screen.blit(bt2, (back_button.x + back_button.width // 2 - bt2.get_width() // 2,
                      back_button.y + back_button.height // 2 - bt2.get_height() // 2))

    return back_button

def draw_game_screen():
    global health_player, health_enemy, log_text, player, enemy
    screen.fill(BLACK)

    if not player or not enemy:
        update_health_labels()
    else:
        update_health_labels()

    # Health Bars
    if player and enemy:
        # Player Health Bar
        p_bar_width = 300
        p_hp_width = int(p_bar_width * player.health / player.max_health)
        pygame.draw.rect(screen, DARK_GRAY, (50, 160, p_bar_width, 30), border_radius=5)
        pygame.draw.rect(screen, GREEN, (50, 160, p_hp_width, 30), border_radius=5)

        # Enemy Health Bar (right-aligned)
        e_bar_width = 300
        e_hp_width = int(e_bar_width * enemy.health / enemy.max_health)
        e_bar_x = WIDTH - 50 - e_bar_width
        pygame.draw.rect(screen, DARK_GRAY, (e_bar_x, 160, e_bar_width, 30), border_radius=5)
        pygame.draw.rect(screen, GREEN, (e_bar_x + (e_bar_width - e_hp_width), 160, e_hp_width, 30), border_radius=5)

    # Health Text (this contains the names)
    # Correct health labels
        if health_player:
            screen.blit(health_player, (50, 120))
        if health_enemy:
            screen.blit(health_enemy, (WIDTH - health_enemy.get_width() - 50, 120))

    # Log Text
    log_surface = button_font.render(log_text, True, LIGHT_GRAY)
    log_bg_rect = log_surface.get_rect(centerx=WIDTH//2, top=HEIGHT - 120)
    log_bg_rect.inflate_ip(20, 10)
    pygame.draw.rect(screen, DARK_GRAY, log_bg_rect, border_radius=5)
    screen.blit(log_surface, (log_bg_rect.x + 10, log_bg_rect.y + 5))

    # Action Buttons
    mouse_pos = pygame.mouse.get_pos()
    for text, rect in game_screen.items():
        color = HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        if not player.is_alive() or not enemy.is_alive():
            color = DARK_GRAY
        pygame.draw.rect(screen, color, rect, border_radius=10)
        bt = button_font.render(text, True, WHITE)
        screen.blit(bt, (rect.x + rect.width // 2 - bt.get_width() // 2,
                         rect.y + rect.height // 2 - bt.get_height() // 2))

    # Quit Battle Button
    quit_battle_rect = pygame.Rect(WIDTH // 2 - 100, 520, 200, 60)
    quit_color = HOVER_COLOR if quit_battle_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, quit_color, quit_battle_rect, border_radius=10)
    quit_text = button_font.render("Quit Battle (ESC)", True, WHITE)
    screen.blit(quit_text, (quit_battle_rect.x + quit_battle_rect.width // 2 - quit_text.get_width() // 2,
                            quit_battle_rect.y + quit_battle_rect.height // 2 - quit_text.get_height() // 2))

    return quit_battle_rect

# ----------------- Game functions -----------------
def update_health_labels():
    global health_player, health_enemy
    if player and enemy:
        player_color = GREEN if player.is_alive() else DARK_GRAY
        enemy_color = GREEN if enemy.is_alive() else DARK_GRAY
        health_player = button_font.render(f"{player.name} HP: {player.health}/{player.max_health}", True, player_color)
        health_enemy = button_font.render(f"{enemy.name} HP: {enemy.health}/{enemy.max_health}", True, enemy_color)

def end_game(winner: str):
    global log_text, immunity_rounds, hits, player, enemy
    log_text = f"GAME OVER! {winner} wins!"
    
    # Check if the player is actually defeated before showing the message box
    if player and player.is_alive():
        # Player won, reset is done later by the loop when state changes
        pass
    elif enemy and enemy.is_alive():
        # Enemy won or draw, display message.
        try:
            messagebox.showinfo("Game Over", log_text + f" (Hits: {hits})")
        except Exception:
            print("Game Over:", log_text)

    # Note: State change logic is handled in the main loop to return to name_input/menu.
    # We just stop the music here to prevent looping battle music over the Game Over screen.
    try:
        mixer.music.stop()
    except Exception:
        pass
        
    immunity_rounds = 0
    hits = 0

def heal():
    global log_text, player, enemy, enemy_turn_pending

    if enemy_turn_pending:
        return
    if not player or not enemy or not player.is_alive() or not enemy.is_alive():
        return
    
    # Check if a cooldown is needed, or if an action is already scheduled.
    # The original code allows spamming, which is fine for a demo.

    superheal = random.randint(1, 3)
    if superheal == 3:
        amount = random.randint(20, 30)
        player.health = min(player.max_health, player.health + amount)
        log_text = f"{player.name} **super heals** for {amount}!"
    else:
        # Assuming player.heal_player() is defined in Player class
        amount = player.heal_player()
        log_text = f"{player.name} heals for {amount}!"
        
    update_health_labels()
    enemy_turn_pending = True
    pygame.time.set_timer(pygame.USEREVENT + 1, 400, loops=1) # schedule enemy turn once

def attack():
    global log_text, hits, player, enemy, enemy_turn_pending
    if enemy_turn_pending:
        return
    if not player or not enemy or not player.is_alive() or not enemy.is_alive():
        return
    
    # Player's turn to attack
    damage = random.randint(max(0, player.attack - 2), player.attack + 2) - enemy.defense
    enemy.take_damage(damage)
    hits += 1
    log_text = f"{player.name} attacks {enemy.name} for {damage} damage!"
    
    # Critical chance
    chance = random.randint(1,5)
    if chance == 5:
        crit = random.randint(5, 15)
        total_damage = damage + crit
        enemy.take_damage(total_damage)
        log_text += f" CRITICAL! +{crit}"
    
    # Check if enemy died after player's attack
    if not enemy.is_alive():
        end_game(winner=player.name)
        return

    update_health_labels()
    enemy_turn_pending = True
    pygame.time.set_timer(pygame.USEREVENT + 1, 450, loops=1)# enemy turn

def defend():
    global log_text, immunity_rounds, enemy_turn_pending
    if enemy_turn_pending:
        return
    if not player or not enemy or not player.is_alive() or not enemy.is_alive():
        return
        
    immunity_rounds = 1
    log_text = f"{player.name} raises guard and will be immune for 1 enemy attack!"
    enemy_turn_pending = False
    pygame.time.set_timer(pygame.USEREVENT + 1, 350, loops=1)# schedule enemy turn

def enemy_turn():
    global log_text, immunity_rounds, player, enemy, enemy_turn_pending
    enemy_turn_pending = False
    
    if not player or not enemy or not player.is_alive() or not enemy.is_alive():
        return

    # 1. Handle immunity
    if immunity_rounds > 0:
        immunity_rounds -= 1
        log_text = f"{enemy.name} attacks but {player.name} is immune (Defense up)!"
        return
    else:
        # Enemy attacks (with defense applied to player damage taken)
        dmg = max(0, random.randint(max(0, enemy.attack - 2), enemy.attack + 2) - player.defense)
        player.take_damage(dmg)
        log_text = f"{enemy.name} attacks {player.name} for {dmg} damage!"
        
    update_health_labels()
    
    # 3. Check for game over (enemy wins)
    if not player.is_alive():
        end_game(winner=enemy.name)
    
def handle_back_button(state, back_rect, music_path=None):
    mouse_pos = pygame.mouse.get_pos()
    pressed = pygame.mouse.get_pressed()[0]  # left mouse button

    # Mouse click on back button
    if pressed and back_rect.collidepoint(mouse_pos):
        # Stop any game music if given
        if music_path:
            try:
                mixer.music.stop()
                mixer.music.unload()
                safe_music_load(music_path)
                mixer.music.play(-1)
            except Exception:
                pass
        return "menu"

    return state


# ----------------- Credits -----------------
def run_credits(credits_music_path=None, menu_music_path=None):
    try:
        mixer.music.stop()
        mixer.music.unload()
    except Exception:
        pass
    if credits_music_path and safe_music_load(credits_music_path):
        mixer.music.play(loops=0)
    clock = pygame.time.Clock()
    try:
        f = pygame.font.SysFont("Consolas", 22)
    except Exception:
        f = pygame.font.SysFont(None, 22)
    total_lines = len(CREDITS_CONTENT)
    total_height = total_lines * LINE_SPACING
    scroll_y = HEIGHT
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
        scroll_y -= SCROLL_SPEED
        if scroll_y < -total_height:
            running = False
        screen.fill(BLACK)
        for i, line in enumerate(CREDITS_CONTENT):
            y = scroll_y + i * LINE_SPACING
            if -LINE_SPACING < y < HEIGHT:
                txt = f.render(line, True, WHITE)
                rect = txt.get_rect(centerx=WIDTH // 2)
                rect.y = int(y)
                screen.blit(txt, rect)
        pygame.display.flip()
        clock.tick(CREDITS_FPS)
    try:
        mixer.music.fadeout(800)
    except Exception:
        pass
    time.sleep(0.6)
    if menu_music_path and safe_music_load(menu_music_path):
        mixer.music.play(-1)

# ----------------- Main Menu Loop (rewritten & fixed) -----------------
def menu_loop():
    global player, enemy, immunity_rounds, log_text, hits
    clock = pygame.time.Clock()
    running = True
    state: Literal["menu", "settings", "name_input", "game", "change_notes"] = "menu"
    previous_state = "menu"  # not used for back anymore except for start/game exit
    back_button = None

    # --- Hard-coded back routing ---
    BACK_TARGET = {
        "settings": "menu",
        "change_notes": "settings",
        "name_input": "menu"
    }

    # Paths
    menu_music_path = MENU_MUSIC
    game_music_path = GAME_MUSIC
    credits_music_path = CREDITS_MUSIC

    # One-time initialization flags
    state_initialized = {
        "menu": False,
        "settings": False,
        "name_input": False,
        "game": False,
        "change_notes": False
    }

    hits = 0

    # Start menu music
    if safe_music_load(menu_music_path):
        try:
            mixer.music.play(-1)
        except Exception:
            pass

    # Prefill name input boxes
    last_p, last_e = load_last_players()
    if last_p:
        input_box_player.text = last_p
        input_box_player.txt_surface = font_small.render(last_p, True, WHITE)
    if last_e:
        input_box_enemy.text = last_e
        input_box_enemy.txt_surface = font_small.render(last_e, True, WHITE)

    # ---------------- MAIN LOOP ----------------
    while running:

        # Draw according to state
        if state == "menu":
            if not state_initialized["menu"]:
                state_initialized = {k: False for k in state_initialized}
                state_initialized["menu"] = True

                if not mixer.music.get_busy() and safe_music_load(menu_music_path):
                    try:
                        mixer.music.play(-1)
                    except Exception:
                        pass

            draw_menu()

        elif state == "settings":
            if not state_initialized["settings"]:
                state_initialized = {k: False for k in state_initialized}
                state_initialized["settings"] = True

            back_button, credits_button, change_note_button = draw_settings()

        elif state == "change_notes":
            if not state_initialized["change_notes"]:
                state_initialized = {k: False for k in state_initialized}
                state_initialized["change_notes"] = True

            back_button = draw_change_notes()

        elif state == "name_input":
            if not state_initialized["name_input"]:
                state_initialized = {k: False for k in state_initialized}
                state_initialized["name_input"] = True

            back_button = draw_name_input_screen()

        elif state == "game":
            if not state_initialized["game"]:
                state_initialized = {k: False for k in state_initialized}
                state_initialized["game"] = True

                try:
                    mixer.music.stop()
                    mixer.music.unload()
                except Exception:
                    pass

                loading_screen("Entering Battle...", duration=0.8)

                if safe_music_load(game_music_path):
                    try:
                        mixer.music.play(-1)
                    except Exception:
                        pass

            quit_battle_rect = draw_game_screen()

        pygame.display.flip()

        # --------- EVENT PROCESSING ---------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.USEREVENT + 1:
                enemy_turn()
                continue

            if state == "name_input":
                input_box_player.handle_event(event)
                input_box_enemy.handle_event(event)

            # MOUSE CLICK
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                # -------- MENU --------
                if state == "menu":
                    if buttons["Start"].collidepoint(pos):
                        previous_state = state
                        loading_screen("Loading Game Assets...", duration=0.7)

                        try:
                            mixer.music.stop()
                            mixer.music.unload()
                        except Exception:
                            pass

                        state = "name_input"

                    elif buttons["Settings"].collidepoint(pos):
                        previous_state = state
                        state = "settings"

                    elif buttons["Quit"].collidepoint(pos):
                        try:
                            mixer.music.stop()
                            mixer.quit()
                        except Exception:
                            pass

                        try:
                            messagebox.showinfo("Quit", "Thank you for trying the demo! See you on B1.1.7!")
                        except Exception:
                            print("Quit: Thank you for trying the demo!")

                        running = False
                        break

                # -------- SETTINGS --------
                elif state == "settings":
                    if credits_button is not None and credits_button.collidepoint(pos):
                        previous_state = state
                        try:
                            messagebox.showinfo("Credits", "Showing credits... (press ESC to skip)")
                        except Exception:
                            print("Credits: Showing credits... (press ESC to skip)")
                        run_credits(credits_music_path, menu_music_path)
                        state = "menu"

                    elif back_button is not None and back_button.collidepoint(pos):
                        state = BACK_TARGET["settings"]

                    elif change_note_button is not None and change_note_button.collidepoint(pos):
                        previous_state = state
                        state = "change_notes"

                # -------- CHANGE NOTES --------
                elif state == "change_notes":
                    if back_button is not None and back_button.collidepoint(pos):
                        state = BACK_TARGET["change_notes"]

                # -------- NAME INPUT --------
                elif state == "name_input":

                    if name_input_confirm_button.collidepoint(pos):
                        ptext = input_box_player.text.strip() or "Hero"
                        etext = input_box_enemy.text.strip() or "Fighter"

                        save_last_players(ptext, etext)

                        player = Player(ptext, health=100, attack=15, defense=5, heal=0)
                        player.max_health = 100
                        enemy = Enemy(etext, health=100, attack=12, defense=3)
                        enemy.max_health = 100

                        hits = 0
                        update_health_labels()

                        log_text = f"{player.name} vs {enemy.name}! Battle Start!"

                        previous_state = state
                        state = "game"

                    elif back_button is not None and back_button.collidepoint(pos):
                        state = BACK_TARGET["name_input"]  # -> menu

                # -------- GAME --------
                elif state == "game":
                    if not (player and player.is_alive() and enemy and enemy.is_alive()):
                        if quit_battle_rect.collidepoint(pos):
                            previous_state = state
                            state = "menu"
                        continue

                    if game_screen["Attack"].collidepoint(pos):
                        attack()
                    elif game_screen["Heal"].collidepoint(pos):
                        heal()
                    elif game_screen["Defend"].collidepoint(pos):
                        defend()
                    elif quit_battle_rect.collidepoint(pos):
                        previous_state = state
                        state = "name_input"

                        try:
                            mixer.music.stop()
                            mixer.music.unload()
                        except Exception:
                            pass

                        if safe_music_load(menu_music_path):
                            try:
                                mixer.music.play(-1)
                            except Exception:
                                pass

            # -------- KEYBOARD --------
            if event.type == pygame.KEYDOWN:

                # ESC Exit from Battle
                if event.key == pygame.K_ESCAPE:

                    if state == "game":
                        if player and enemy:
                            try:
                                messagebox.showinfo("Exit to Menu", "Returning to name input. Current battle progress is lost.")
                            except Exception:
                                print("Returning to name input. Current battle progress is lost.")

                        player = None
                        enemy = None

                        previous_state = state
                        state = "name_input"

                        try:
                            mixer.music.stop()
                            mixer.music.unload()
                        except Exception:
                            pass

                        if safe_music_load(menu_music_path):
                            try:
                                mixer.music.play(-1)
                            except Exception:
                                pass

                    # ESC from settings/change_notes/name_input
                    elif state in ["settings", "change_notes", "name_input"]:
                        state = BACK_TARGET[state]

        clock.tick(60)

    # Cleanup
    try:
        mixer.music.stop()
    except Exception:
        pass

    pygame.quit()
    sys.exit()

# ----------------- Entrypoint -----------------
if __name__ == "__main__":
    # small startup load
    loading_screen("Fatal Encounter (Fixed Demo)", duration=0.9)
    menu_loop()