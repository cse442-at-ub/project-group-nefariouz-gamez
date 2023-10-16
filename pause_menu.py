import pygame
import sys
from MenuWidgets import Button


def resume():
    print("RESUME")


def settings():
    print("SETTINGS")


def main_menu():
    print("MAIN MENU")


def exit():
    print("EXIT")

# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def show_pause_menu(screen):
    # Load in background image
    background_img = pygame.image.load("assets/Background/pause_screen_background.png").convert_alpha()

    # Run game loop for this page
    while True:
        screen_size = screen.get_size()
        button_size = (screen_size[0]/4.286, screen_size[1]/16)
        center = screen_size[0] / 2

        widgets = [
            Button((center, screen_size[1] / 3.300), button_size, "Resume", resume),
            Button((center, screen_size[1] / 2.425), button_size, "Settings", settings),
            Button((center, screen_size[1] / 1.900), button_size, "Main Menu", main_menu),
            Button((center, screen_size[1] / 1.575), button_size, "Exit", exit)
        ]

        # Draw background
        screen.blit(pygame.transform.scale(background_img, screen_size), (0, 0))

        for widget in widgets:
            widget.draw(screen)

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    resume()

            for widget in widgets:
                widget.handle_event(event)

        # Update display
        pygame.display.update()


# Used to test function by running file
if __name__ == '__main__':
    pygame.init()
    screen_size = (1200, 800)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    show_pause_menu(screen)
