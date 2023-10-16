import pygame

<<<<<<< HEAD
=======

>>>>>>> Sprint2-Pause-Screen
class Button:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from middle of box
        size (tuple): takes (width, height) of rectangle
        text (str): places text on button
        action: performs function when clicked
    """
<<<<<<< HEAD
    def __init__(self, pos: tuple, size: tuple, text: str, action=None):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos[0] - (self.size[0]/2), self.pos[1] - (self.size[1]/2), self.size[0], self.size[1])
=======

    def __init__(self, pos: tuple, size: tuple, text: str, action=None):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos[0] - (self.size[0] / 2), self.pos[1] - (self.size[1] / 2), self.size[0],
                                self.size[1])
>>>>>>> Sprint2-Pause-Screen
        self.text = text
        self.action = action
        self.color = (190, 190, 190)
        self.hovered = False

    def draw(self, screen):
        self.handle_hover()

        button_surface = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, self.color, (0, 0, self.size[0], self.size[1]), border_radius=7)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (34, 90, 48))
<<<<<<< HEAD
        text_rect = text_surface.get_rect(center=(self.size[0]/2, self.size[1]/2))
=======
        text_rect = text_surface.get_rect(center=(self.size[0] / 2, self.size[1] / 2))
>>>>>>> Sprint2-Pause-Screen
        button_surface.blit(text_surface, text_rect)
        button_rect = button_surface.get_rect(center=(self.pos[0], self.pos[1]))

        screen.blit(button_surface, button_rect)

    def handle_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovered = True
            self.color = (210, 210, 210)
        else:
            self.hovered = False
            self.color = (190, 190, 190)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.action:
                self.action()

<<<<<<< HEAD
=======

>>>>>>> Sprint2-Pause-Screen
class Checkbox:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from the middle of box
        dim (int): takes value used for width and height of box
    """
<<<<<<< HEAD
    def __init__(self, pos: tuple, dim: int):
        self.pos = pos
        self.size = (dim, dim)
        self.rect = pygame.Rect(self.pos[0] - (self.size[0]/2), self.pos[1] - (self.size[1]/2), self.size[0], self.size[1])
=======

    def __init__(self, pos: tuple, dim: int):
        self.pos = pos
        self.size = (dim, dim)
        self.rect = pygame.Rect(self.pos[0] - (self.size[0] / 2), self.pos[1] - (self.size[1] / 2), self.size[0],
                                self.size[1])
>>>>>>> Sprint2-Pause-Screen
        self.checked = False

        # Load images from folder
        self.unchecked_image = pygame.image.load("images/unchecked_box.png")
        self.checked_image = pygame.image.load("images/checked_box.png")

        self.unchecked_image = pygame.transform.scale(self.unchecked_image, self.size)
        self.checked_image = pygame.transform.scale(self.checked_image, self.size)

    def draw(self, screen):
        if self.checked:
<<<<<<< HEAD
            screen.blit(self.checked_image, (self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2))
        else:
            screen.blit(self.unchecked_image, (self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2))
=======
            screen.blit(self.checked_image, (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2))
        else:
            screen.blit(self.unchecked_image, (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2))
>>>>>>> Sprint2-Pause-Screen

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.checked = not self.checked
            if self.checked:
                print("MUTED")
            else:
                print("UNMUTED")

<<<<<<< HEAD
=======

>>>>>>> Sprint2-Pause-Screen
class Slider:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from middle of box
        size (tuple): takes (width, height) of slider
        text (str): places text on button
        action: performs function when clicked
    """
<<<<<<< HEAD
=======

>>>>>>> Sprint2-Pause-Screen
    def __init__(self, pos: tuple, size: tuple):
        self.pos = pos
        self.size = size

<<<<<<< HEAD
        self.slider_left = self.pos[0] - (size[0]//2)
        self.slider_right = self.pos[0] + (size[0]//2)
        self.slider_top = self.pos[1] - (size[1]//2)

        self.min = 0
        self.max = 100
        self.initial_val = (self.slider_right - self.slider_left) * 0.95    # set base volume at 95%
=======
        self.slider_left = self.pos[0] - (size[0] // 2)
        self.slider_right = self.pos[0] + (size[0] // 2)
        self.slider_top = self.pos[1] - (size[1] // 2)

        self.min = 0
        self.max = 100
        self.initial_val = (self.slider_right - self.slider_left) * 0.95  # set base volume at 95%
>>>>>>> Sprint2-Pause-Screen

        self.container_rect = pygame.Rect(self.slider_left, self.slider_top, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left + self.initial_val - 5, self.slider_top, 10, self.size[1])

    def draw(self, screen):
        pygame.draw.rect(screen, (190, 190, 190), self.container_rect)
        pygame.draw.rect(screen, (34, 90, 48), self.button_rect)

    def move_slider(self, mouse_pos):
        self.button_rect.centerx = mouse_pos[0]

    def handle_event(self, mouse_pos, mouse):
        if self.container_rect.collidepoint(mouse_pos) and mouse[0]:
            self.move_slider(mouse_pos)
        # print(self.get_value())

    def get_value(self):
        val_range = self.slider_right - self.slider_left - 1
        button_val = self.button_rect.centerx - self.slider_left
<<<<<<< HEAD
        value = (button_val/val_range) * (self.max-self.min) + self.min
=======
        value = (button_val / val_range) * (self.max - self.min) + self.min
>>>>>>> Sprint2-Pause-Screen
        if value > 98.5:
            return 100.0
        elif value < 1.5:
            return 0.0
        else:
            return value

<<<<<<< HEAD
=======

>>>>>>> Sprint2-Pause-Screen
class Checkbox:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from the middle of box
        dim (int): takes value used for width and height of box
    """
<<<<<<< HEAD
    def __init__(self, pos: tuple, dim: int):
        self.pos = pos
        self.size = (dim, dim)
        self.rect = pygame.Rect(self.pos[0] - (self.size[0]/2), self.pos[1] - (self.size[1]/2), self.size[0], self.size[1])
=======

    def __init__(self, pos: tuple, dim: int):
        self.pos = pos
        self.size = (dim, dim)
        self.rect = pygame.Rect(self.pos[0] - (self.size[0] / 2), self.pos[1] - (self.size[1] / 2), self.size[0],
                                self.size[1])
>>>>>>> Sprint2-Pause-Screen
        self.checked = False

        # Load images from folder
        self.unchecked_image = pygame.image.load("assets/menuAssets/unchecked_box.png")
        self.checked_image = pygame.image.load("assets/menuAssets/checked_box.png")

        self.unchecked_image = pygame.transform.scale(self.unchecked_image, self.size)
        self.checked_image = pygame.transform.scale(self.checked_image, self.size)

    def draw(self, screen):
        if self.checked:
<<<<<<< HEAD
            screen.blit(self.checked_image, (self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2))
        else:
            screen.blit(self.unchecked_image, (self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2))
=======
            screen.blit(self.checked_image, (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2))
        else:
            screen.blit(self.unchecked_image, (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2))
>>>>>>> Sprint2-Pause-Screen

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.checked = not self.checked
            if self.checked:
                print("MUTED")
            else:
                print("UNMUTED")

<<<<<<< HEAD
=======

>>>>>>> Sprint2-Pause-Screen
class Slider:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from middle of box
        size (tuple): takes (width, height) of slider
        text (str): places text on button
        action: performs function when clicked
    """
<<<<<<< HEAD
=======

>>>>>>> Sprint2-Pause-Screen
    def __init__(self, pos: tuple, size: tuple):
        self.pos = pos
        self.size = size

<<<<<<< HEAD
        self.slider_left = self.pos[0] - (size[0]//2)
        self.slider_right = self.pos[0] + (size[0]//2)
        self.slider_top = self.pos[1] - (size[1]//2)

        self.min = 0
        self.max = 100
        self.initial_val = (self.slider_right - self.slider_left) * 0.95    # set base volume at 95%
=======
        self.slider_left = self.pos[0] - (size[0] // 2)
        self.slider_right = self.pos[0] + (size[0] // 2)
        self.slider_top = self.pos[1] - (size[1] // 2)

        self.min = 0
        self.max = 100
        self.initial_val = (self.slider_right - self.slider_left) * 0.95  # set base volume at 95%
>>>>>>> Sprint2-Pause-Screen

        self.container_rect = pygame.Rect(self.slider_left, self.slider_top, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left + self.initial_val - 5, self.slider_top, 10, self.size[1])

    def draw(self, screen):
        pygame.draw.rect(screen, (190, 190, 190), self.container_rect)
        pygame.draw.rect(screen, (34, 90, 48), self.button_rect)

    def move_slider(self, mouse_pos):
        self.button_rect.centerx = mouse_pos[0]

    def handle_event(self, mouse_pos, mouse):
        if self.container_rect.collidepoint(mouse_pos) and mouse[0]:
            self.move_slider(mouse_pos)
        # print(self.get_value())

    def get_value(self):
        val_range = self.slider_right - self.slider_left - 1
        button_val = self.button_rect.centerx - self.slider_left
<<<<<<< HEAD
        value = (button_val/val_range) * (self.max-self.min) + self.min
=======
        value = (button_val / val_range) * (self.max - self.min) + self.min
>>>>>>> Sprint2-Pause-Screen
        if value > 98.5:
            return 100.0
        elif value < 1.5:
            return 0.0
        else:
            return value