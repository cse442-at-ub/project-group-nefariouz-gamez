import pygame
import sys
from MenuWidgets import Button


# Temp function
def go_back():
    print("RETURN")


# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def show_tutorial(screen):
    # Load in images
    background_img = pygame.image.load("assets/Background/tutorial_background.png").convert_alpha()

    # Run game loop for this page
    while True:
        # Resize images
        screen_size = screen.get_size()
        button_size = (screen_size[0] / 4.286, screen_size[1] / 16)

        # Draw background
        screen.blit(pygame.transform.scale(background_img, screen_size), (0, 0))

        # Make and draw return button
        return_button = Button((screen_size[0] / 6.557, screen_size[1] / 17.000), button_size, "RETURN", go_back)
        return_button.draw(screen)

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Handle button press
            return_button.handle_event(event)

        # Update display
        pygame.display.update()


# Used to test function by running file
if __name__ == '__main__':
    pygame.init()
    screen_size = (1200, 800)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    show_tutorial(screen)