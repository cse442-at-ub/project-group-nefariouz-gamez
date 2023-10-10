import pygame
from Button import *

pygame.init()

def start_game_btn():
    print("BEGIN YOUR QUEST")

def display_main_menu(screen):
    
    # find screen dimensions
    screen_width = screen.get_size()[0]
    screen_height = screen.get_size()[1]

    background_img = pygame.image.load("images/main_background.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

    # initializes buttons
    start_btn = Button(screen_width/2, screen_height/2, "BEGIN YOUR QUEST", start_game_btn)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # checks for buttons clicked
            start_btn.handle_event(event)
        
        # add background image and buttons to window
        screen.blit(background_img, (0, 0))
        start_btn.draw(screen)

        pygame.display.flip()

    pygame.quit()

# runs main menu
if __name__ == "__main__":
    screen = pygame.display.set_mode((1248, 702), pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    display_main_menu(screen)