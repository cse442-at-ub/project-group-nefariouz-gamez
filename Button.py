import pygame

class Button:
    def __init__(self, x, y, text, action=None):
        self.x = x
        self.y = y
        self.width = 300
        self.height = 55
        self.rect = pygame.Rect(x - (self.width / 2), y - (self.height / 2), self.width, self.height)
        self.text = text
        self.action = action
        self.color = (190, 190, 190)
        self.hovered = False

    def draw(self, screen):
        self.handle_hover()

        button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, self.color, (0, 0, self.width, self.height), border_radius=7)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (34, 90, 48))
        text_rect = text_surface.get_rect(center=(self.width / 2, self.height / 2))
        button_surface.blit(text_surface, text_rect)
        button_rect = button_surface.get_rect(center=(self.x, self.y))
        
        screen.blit(button_surface, button_rect)

    def handle_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovered = True
            self.color = (210,210,210)
        else:
            self.hovered = False
            self.color = (190,190,190)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.action:
                self.action()