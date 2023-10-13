import pygame
import math


# Call to draw button
def draw_button(screen, size, location, text):
    button_surface = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
    pygame.draw.rect(button_surface, (190, 190, 190), (0, 0, size[0], size[1]), border_radius=7)

    font = pygame.font.Font(None, math.floor(36*(screen.get_size()[0]/1200)))
    text_surface = font.render(text, True, (34, 90, 48))
    text_rect = text_surface.get_rect(center=(size[0] / 2, size[1] / 2))
    button_surface.blit(text_surface, text_rect)
    button_rect = button_surface.get_rect(center=location)

    screen.blit(button_surface, button_rect)
    return button_rect
