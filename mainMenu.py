import pygame
import sys
from Button import *

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
    start_btn = Button(screen_width/2, (screen_height/2)-105, "BEGIN YOUR QUEST", start_game)
    load_btn = Button(screen_width/2, (screen_height/2)-35, "LOAD LEVEL", load_level)
    settings_btn = Button(screen_width/2, (screen_height/2)+35, "SETTINGS", settings)
    quit_btn = Button(screen_width/2, (screen_height/2)+105, "QUIT", quit_game)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # checks for buttons clicked
            start_btn.handle_event(event)
            load_btn.handle_event(event)
            settings_btn.handle_event(event)
            quit_btn.handle_event(event)
        
        # add background image and buttons to window
        screen.blit(background_img, (0, 0))
        start_btn.draw(screen)
        load_btn.draw(screen)
        settings_btn.draw(screen)
        quit_btn.draw(screen)

        pygame.display.flip()

    pygame.quit()

# runs main menu
if __name__ == "__main__":
    screen = pygame.display.set_mode((1248, 702), pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    display_main_menu(screen)