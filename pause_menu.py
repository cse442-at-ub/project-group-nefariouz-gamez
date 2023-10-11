import pygame
import sys
from draw_background import draw_background
from draw_button import draw_button


# Call show_tutorial with screen (pygame.display.set_mode(screen_size))
def show_pause_menu(screen):
    # Load in images
    background_img = pygame.image.load("assets/pause_screen_background.png").convert_alpha()
    resume_button_img = pygame.image.load("assets/resume_button.png").convert_alpha()
    settings_button_img = pygame.image.load("assets/settings_button.png").convert_alpha()
    return_button_img = pygame.image.load("assets/return_to_main_button.png").convert_alpha()
    exit_button_img = pygame.image.load("assets/exit_button.png").convert_alpha()

    # Run game loop for this page
    while True:
        screen_size = screen.get_size()
        button_size = (screen_size[0]/4.286, screen_size[1]/16)

        # Draw background
        draw_background(screen, background_img, screen_size)

        # Draw buttons
        resume_button_rect = draw_button(screen, resume_button_img, button_size, (screen_size[0]/2.632, screen_size[1]/3.279))
        settings_button_rect = draw_button(screen, settings_button_img, button_size, (screen_size[0]/2.632, screen_size[1]/2.432))
        return_button_rect = draw_button(screen, return_button_img, button_size, (screen_size[0] / 2.632, screen_size[1] / 1.900))
        exit_button_rect = draw_button(screen, exit_button_img, button_size, (screen_size[0] / 2.632, screen_size[1] / 1.600))

        # Check inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if pygame.mouse.get_pressed()[0] == 1:
                pos = pygame.mouse.get_pos()
                if resume_button_rect.collidepoint(pos):
                    return
                if settings_button_rect.collidepoint(pos):
                    print("SETTINGS")
                if return_button_rect.collidepoint(pos):
                    print("RETURN TO MAIN")
                if exit_button_rect.collidepoint(pos):
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
