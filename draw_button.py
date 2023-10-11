import pygame
import pygame.gfxdraw


# Call to draw button
def draw_button(screen, button_img, size, location):
    button_img = pygame.transform.scale(button_img, size)

    shadow_surface = pygame.Surface((button_img.get_width()+2, button_img.get_height()+2), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(0, 0, button_img.get_width()+2, button_img.get_height()+2)
    shadow_color = (0, 0, 0, 128)
    pygame.gfxdraw.box(shadow_surface, shadow_rect, shadow_color)
    pygame.gfxdraw.filled_ellipse(shadow_surface, shadow_rect.centerx, shadow_rect.centery + 10, shadow_rect.width // 2, shadow_rect.height // 4, shadow_color)
    screen.blit(shadow_surface, (location[0]-2, location[1]+2))

    button_rect = button_img.get_rect()
    button_rect.topleft = location
    screen.blit(button_img, button_rect.topleft)
    return button_rect
