import pygame
from Button import *

pygame.init()

def display_settings_page(screen):

    # find screen dimensions
    screen_width = screen.get_size()[0]
    screen_height = screen.get_size()[1]

    background_img = pygame.image.load("images/plain_background.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

    # initializes buttons, button dimensions: 300x54, buttons have a 70 unit gap between them
    tutorial_btn = Button(screen_width/2, (screen_height/2)+50, "TUTORIAL")
    character_btn = Button(screen_width/2, (screen_height/2)+120, "CHOOSE CHARACTER")
    return_btn = Button(screen_width/2, (screen_height/2)+190, "RETURN TO MAIN")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background_img, (0, 0))
        tutorial_btn.draw(screen)
        character_btn.draw(screen)
        return_btn.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    screen = pygame.display.set_mode((1248, 702), pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    display_settings_page(screen)