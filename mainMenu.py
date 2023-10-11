import pygame
import sys
from MenuWidgets import *

pygame.init()

def start_game():
    print("BEGIN YOUR QUEST")

def load_level():
    print("LOAD LEVEL")

def settings():
    print("SETTINGS")

def quit_game():
    pygame.quit()
    sys.exit()

def display_main_menu(screen):
    
    # find screen dimensions
    screen_width = screen.get_size()[0]
    screen_height = screen.get_size()[1]

    background_img = pygame.image.load("images/main_background.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

    # initializes buttons, button dimensions: 300x54, buttons have a 70 unit gap between them
    widgets = [
        Button(screen_width/2, (screen_height/2)-120, "BEGIN YOUR QUEST", start_game),
        Button(screen_width/2, (screen_height/2)-40, "LOAD LEVEL", load_level),
        Button(screen_width/2, (screen_height/2)+40, "SETTINGS", settings),
        Button(screen_width/2, (screen_height/2)+120, "QUIT", quit_game)
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # checks for buttons clicked
            for widget in widgets:
                widget.handle_event(event)
        
        # add background image and buttons to window
        screen.blit(background_img, (0, 0))

        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()

    pygame.quit()

# runs main menu
if __name__ == "__main__":
    screen = pygame.display.set_mode((1248, 702), pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    display_main_menu(screen)