import pygame
from MenuWidgets import *

pygame.init()

def scale_window(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("images/plain_background.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))   # scale background to resolution

    # create widgets based on screen size
    widgets = [
        Slider(((screen_width/2)+150, (screen_height/2)-190), (300, 54)),
        Slider(((screen_width/2)+150, (screen_height/2)-110), (300, 54)),
        Checkbox(((screen_width/2+27), (screen_height/2)-30), 54),
        Button((screen_width/2, (screen_height/2)+50), (300, 54), "TUTORIAL", tutorial),
        Button((screen_width/2, (screen_height/2)+130), (300, 54), "CHOOSE CHARACTER", choose_character),
        Button((screen_width/2, (screen_height/2)+210), (300, 54), "RETURN TO MAIN", return_main)
    ]

    return widgets, screen_width, screen_height, background_img

def draw_text(text, font, color, pos):
    img = font.render(text, True, color)
    centered_x = pos[0] - img.get_width() // 2
    centered_y = pos[1] - img.get_height() // 2
    centered_pos = (centered_x, centered_y)
    screen.blit(img, centered_pos)

def tutorial():
    print("TUTORIAL")

def choose_character():
    print("CHOOSE CHARACTER")

def return_main():
    print("RETURN TO MAIN")

def display_settings_page(screen):
    widgets, screen_width, screen_height, background_img = scale_window(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                widgets, screen_width, screen_height, background_img = scale_window(screen)   # rescales visuals for new resolution

            for widget in widgets:
                if type(widget) == Button or type(widget) == Checkbox:
                    widget.handle_event(event)
                elif type(widget) == Slider:
                    widget.handle_event(pygame.mouse.get_pos(), pygame.mouse.get_pressed()) 

        # render background and widgets
        screen.blit(background_img, (0, 0))
        draw_text("MUSIC VOLUME", pygame.font.Font(None, 36), (34, 90, 48), ((screen_width/2)-150, (screen_height/2)-190))
        draw_text("SFX VOLUME", pygame.font.Font(None, 36), (34, 90, 48), ((screen_width/2)-150, (screen_height/2)-110))
        draw_text("MUTE", pygame.font.Font(None, 36), (34, 90, 48), ((screen_width/2)-150, (screen_height/2)-30))
        
        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Shrubbery Quest")
    display_settings_page(screen)