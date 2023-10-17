import pygame
import sys
from MenuWidgets import *
from tutorial_page import show_tutorial


def draw_text(screen, text, font, color, pos):
    img = font.render(text, True, color)
    centered_x = pos[0] - img.get_width() // 2
    centered_y = pos[1] - img.get_height() // 2
    centered_pos = (centered_x, centered_y)
    screen.blit(img, centered_pos)


# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def pause_menu_settings(screen):
    # Load in background image
    background_img = pygame.image.load("assets/Background/BetLvlBackground.png").convert_alpha()

    # Get screen size
    screen_size = screen.get_size()
    button_size = (300, 54)

    # Create widgets
    widgets = [
        Slider(((screen_size[0]/2)+150, (screen_size[1]/2)-190), 300, 'music'),
        Slider(((screen_size[0]/2)+150, (screen_size[1]/2)-110), 300, 'sfx'),
        Checkbox(((screen_size[0]/2+27), (screen_size[1]/2)-30), 54),
        Button((screen_size[0]/2, (screen_size[1]/2)+50), button_size, "TUTORIAL", None),
        Button((screen_size[0] / 6.557, screen_size[1] / 17.000), button_size, "RETURN", None)
    ]

    # Run game loop for this page
    while True:
        screen_size = screen.get_size()

        # Draw background
        screen.blit(pygame.transform.scale(background_img, screen_size), (0, 0))
        draw_text(screen, "MUSIC VOLUME", pygame.font.Font(None, 36), (34, 90, 48), ((screen_size[0]/2)-150, (screen_size[1]/2)-190))
        draw_text(screen, "SFX VOLUME", pygame.font.Font(None, 36), (34, 90, 48), ((screen_size[0]/2)-150, (screen_size[1]/2)-110))
        draw_text(screen, "MUTE", pygame.font.Font(None, 36), (34, 90, 48), ((screen_size[0]/2)-150, (screen_size[1]/2)-30))

        # Draw widgets
        for widget in widgets:
            widget.draw(screen)

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Return if escape is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

            # Check button presses
            if event.type == pygame.MOUSEBUTTONDOWN:
                widgets[2].handle_event(event)

                if widgets[3].hovered:
                    show_tutorial(screen)
                elif widgets[4].hovered:
                    return False

            for widget in widgets[0:2]:
                widget.handle_event(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

        # Update display
        pygame.display.update()


# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def show_pause_menu(screen):
    # Load in background image
    background_img = pygame.image.load("assets/Background/pause_screen_background.png").convert_alpha()

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
            Button((center, screen_size[1] / 3.300), button_size, "Resume", None),
            Button((center, screen_size[1] / 2.425), button_size, "Settings", None),
            Button((center, screen_size[1] / 1.900), button_size, "Main Menu", None),
            Button((center, screen_size[1] / 1.575), button_size, "Exit", None)
        ]

        for widget in widgets:
            widget.draw(screen)

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Return if escape is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

            # Check button presses
            if event.type == pygame.MOUSEBUTTONDOWN:
                if widgets[0].hovered:
                    return False
                elif widgets[1].hovered:
                    if pause_menu_settings(screen):
                        return True
                elif widgets[2].hovered:
                    return True
                elif widgets[3].hovered:
                    sys.exit()

        # Update display
        pygame.display.update()


# Used to test function by running file
if __name__ == '__main__':
    pygame.init()
    screen_size = (1200, 800)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    show_pause_menu(screen)
