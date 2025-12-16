import pygame
import sys
import time

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 90 #fps
SCROLL_SPEED = 0.4  #speed
LINE_SPACING = 30 #pixels inbetween lines

CREDITS_CONTENT = [
    "A Game By",
    "-------------------",
    "BattleGame Studios",
    "",
    "Project Lead",
    "zmalajev",
    "",
    "",
    "Lead Developers",
    "Zorko",
    "zmalajev",
    "",
    "",
    "Year of Creation",
    "2024",
    "",
    "",
    "Special Thanks To",
    "Zorko Studios",
    "",
    "",
    "",
    "--- MUSIC & SOUND ---",
    "Menu Music: Mergatroid | 8-Bit Sound",
    "Credits Music: Dinner Set | Jazz",
    "Game Music: Folk | 8-Guitar-Bits",
    "",
    "",
    "All music was recorded from a Roland D-110 Sound Module.",
    "",
    "",
    "BattleGame Studios",
    "",
    "",
    "--- END OF PRODUCTION ---",
    "Thank You For Playing Beta!",
    "-------------------",
    #for spacing
    "", "", "", "", "", "", "", "", "", "",
]

def run_credits():
    """Initializes Pygame, handles other stuff"""

    pygame.init()
    pygame.mixer.init()
    #mixer.music.load('Audio/Menu-music/Jazz.wav')  # Load background music


    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rolling Credits")
    clock = pygame.time.Clock()

    try:
        font = pygame.font.SysFont("Consolas", 24)
    except pygame.error:
        print("Warning: Default font not found. Using a fallback.")
        font = pygame.font.SysFont("Consolas", 36)

    total_lines = len(CREDITS_CONTENT)
    total_credit_height = total_lines * LINE_SPACING
    scroll_y = SCREEN_HEIGHT

    #Main Loop
    running = True
    #mixer.music.play(1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        #scroll speed update
        scroll_y -= SCROLL_SPEED

        #check for end credits
        if scroll_y < -total_credit_height:
            print("Credits finished scrolling!")
            #mixer.music.fadeout(2000)
            time.sleep(1) 
            running = False


        #rendering
        screen.fill(BLACK)

        for i, line in enumerate(CREDITS_CONTENT):
            line_y = scroll_y + (i * LINE_SPACING)

            if -LINE_SPACING < line_y < SCREEN_HEIGHT:
                text_surface = font.render(line, True, WHITE)
                text_rect = text_surface.get_rect()

                text_rect.centerx = SCREEN_WIDTH // 2
                text_rect.y = line_y

                screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    run_credits()
