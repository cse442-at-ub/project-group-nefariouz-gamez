import pygame
import sys
from MenuWidgets import *

pygame.init()

def scale_window(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("images/main_background.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))   # scale background to resolution

    # creates widgets based on screen size
    widgets = [
        Button(screen_width/2, (screen_height/2)-120, "BEGIN YOUR QUEST", start_game),
        Button(screen_width/2, (screen_height/2)-40, "LOAD LEVEL", load_level),
        Button(screen_width/2, (screen_height/2)+40, "SETTINGS", settings),
        Button(screen_width/2, (screen_height/2)+120, "QUIT", quit_game)
    ]

    return widgets, background_img

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
    widgets, background_img = scale_window(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                widgets, background_img = scale_window(screen)   # rescales visuals for new resolution

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