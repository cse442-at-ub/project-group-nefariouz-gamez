import pygame
import sys


# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def show_tutorial(screen):
    # Load in images
    background_img = pygame.image.load("assets/tutorial_background.png").convert_alpha()
    return_button_img = pygame.image.load("assets/return_button.png").convert_alpha()

    # Run game loop for this page
    while True:
        # Draw background
        screen_size = screen.get_size()
        c_background_img = pygame.transform.scale(background_img, screen_size)
        screen.blit(c_background_img, (0, 0))

        # Draw return button
        c_return_button_img = pygame.transform.scale(return_button_img,(screen_size[0]/4.2, screen_size[1]/14.5))
        return_button_rect = c_return_button_img.get_rect()
        return_button_rect.topleft = (screen_size[0]/30, screen_size[1]/36.4)
        screen.blit(c_return_button_img, return_button_rect.topleft)

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if pygame.mouse.get_pressed()[0] == 1:
                pos = pygame.mouse.get_pos()
                if return_button_rect.collidepoint(pos):
                    return

        # Update display
        pygame.display.update()


# Used to test function by running file
if __name__ == '__main__':
    pygame.init()
    screen_size = (1200, 800)
    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    show_tutorial(screen)
