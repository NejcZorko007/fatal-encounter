import pygame
import sys
import time

pygame.init()

window_text = "Fatal Encounter - Alpha Test Files"

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(window_text)

BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
DARK_GREEN = (34, 139, 34)
GRAY = (60, 60, 60)

font_large = pygame.font.SysFont("Arial", 48)
font_small = pygame.font.SysFont("Arial", 28)

BAR_WIDTH = 600
BAR_HEIGHT = 40
bar_x = WIDTH // 2 - BAR_WIDTH // 2
bar_y = HEIGHT // 2

def draw_loading_screen(progress):
    """draw loadscreen"""
    screen.fill(BLACK)
    
    #text above bar
    title_text = font_large.render("Fatal Encounter", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 180))
    #bar bcg
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT), border_radius=8)
    #bar fill
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, BAR_WIDTH * (progress / 100), BAR_HEIGHT), border_radius=8)
    #bar border
    pygame.draw.rect(screen, DARK_GREEN, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT), 3, border_radius=8)
    #precent
    percent_text = font_small.render(f"Loading... {int(progress)}%", True, WHITE)
    screen.blit(percent_text, (WIDTH//2 - percent_text.get_width()//2, bar_y + 60))
    
    pygame.display.flip()

def loading_screen():
    """loading sequence"""
    clock = pygame.time.Clock()
    progress = 0
    
    while progress <= 100:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        draw_loading_screen(progress)
        progress += 0.5 #speed of loading 
        time.sleep(0.02)
        clock.tick(60)
    
    time.sleep(2)
    main_menu()

def main_menu():
    """sample screen"""
    running = True
    while running:
        screen.fill((30, 30, 30))
        text = font_large.render("Rendering Menu...", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    loading_screen()
