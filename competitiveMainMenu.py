import pygame
import sys
from MenuWidgets import *


# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def show_competitive_main_menu(screen):
    # Load in background image
    background_img = pygame.image.load("assets/Background/TitleNoShear.png").convert_alpha()

    # Run game loop for this page
    while True:
        # Resize images
        screen_size = screen.get_size()
        button_size = (screen_size[0]/4.286, screen_size[1]/16)
        center = screen_size[0] / 2

        # Draw background
        screen.blit(pygame.transform.scale(background_img, screen_size), (0, 0))

        # Create and draw widgets
        widgets = [
            Button((center, 240), button_size, "BEGIN YOUR QUEST", None),
            Button((center, 307), button_size, "LOAD LEVEL", None),
            Button((center, 374), button_size, "CHALLENGE MODE", None),
            Button((center, 441), button_size, "LEADERBOARD", None),
            Button((center, 508), button_size, "SETTINGS", None),
            Button((center, 575), button_size, "QUIT", None)
        ]

        for widget in widgets:
            widget.draw(screen)

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Check button presses
            if event.type == pygame.MOUSEBUTTONDOWN:
                if widgets[0].hovered:
                    return "START"
                elif widgets[1].hovered:
                    return "LOAD"
                elif widgets[2].hovered:
                    return "CHALLENGE MODE"
                elif widgets[3].hovered:
                    return "LEADERBOARD"
                elif widgets[4].hovered:
                    return "SETTINGS"
                elif widgets[5].hovered:
                    sys.exit()

        # Update display
        pygame.display.update()


# Used to test function by running file
if __name__ == '__main__':
    pygame.init()
    screen_size = (1200, 800)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    print(show_competitive_main_menu(screen))