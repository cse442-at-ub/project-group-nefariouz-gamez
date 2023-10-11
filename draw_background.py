import pygame


# Call to draw the background for your page
def draw_background(screen, background_img, screen_size):
    background_img = pygame.transform.scale(background_img, screen_size)
    screen.blit(background_img, (0, 0))
