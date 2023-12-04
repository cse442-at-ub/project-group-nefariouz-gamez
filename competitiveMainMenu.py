import pygame
import sys
from MenuWidgets import *


# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def show_competitive_main_menu(screen, hertz_ee):
    # Load in background image
    background_imgs = (pygame.image.load("assets/Background/TitleNoShear.png").convert_alpha(), pygame.image.load("assets/Background/hertz_passion.png").convert_alpha())
    secret_code = [pygame.K_h, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_z]
    buffer = []

    # Run game loop for this page
    while True:
        # Resize images
        screen_size = screen.get_size()
        button_size = (screen_size[0]/4.286, screen_size[1]/16)
        center = screen_size[0] / 2

        # Draw background
        if hertz_ee:
            screen.blit(pygame.transform.scale(background_imgs[1], screen_size), (0, 0))
        else:
            screen.blit(pygame.transform.scale(background_imgs[0], screen_size), (0, 0))

        # Create and draw widgets
        widgets = [
            ColorfulButton((center, 240), button_size, "BEGIN YOUR QUEST", None),
            ColorfulButton((center, 307), button_size, "LOAD LEVEL", None),
            ColorfulButton((center, 374), button_size, "CHALLENGE MODE", None),
            ColorfulButton((center, 441), button_size, "LEADERBOARD", None),
            ColorfulButton((center, 508), button_size, "SETTINGS", None),
            ColorfulButton((center, 575), button_size, "QUIT", None)
        ]

        for widget in widgets:
            if hertz_ee:
                widget.default_color = (137, 148, 153)
                widget.hover_color = (169, 169, 169)
            widget.draw(screen)

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if widgets[0].hovered:
                    return "START", hertz_ee
                elif widgets[1].hovered:
                    return "LOAD", hertz_ee
                elif widgets[2].hovered:
                    return "CHALLENGE MODE", hertz_ee
                elif widgets[3].hovered:
                    return "LEADERBOARD", hertz_ee
                elif widgets[4].hovered:
                    return "SETTINGS", hertz_ee
                elif widgets[5].hovered:
                    sys.exit()
            elif event.type == pygame.KEYDOWN:
                if len(buffer) == 0 or buffer[-1] != event.key:
                    buffer.append(event.key)

                    if len(buffer) > 5:
                        buffer.pop(0)

                    if buffer == secret_code:
                        hertz_ee = not hertz_ee

        # Update display
        pygame.display.update()


# Used to test function by running file
if __name__ == '__main__':
    pygame.init()
    screen_size = (1200, 800)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    print(show_competitive_main_menu(screen))