import pygame


class Button:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from middle of box
        size (tuple): takes (width, height) of rectangle
        text (str): places text on button
        action: performs function when clicked
    """

    def __init__(self, pos: tuple, size: tuple, text: str, action=None):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos[0] - (self.size[0] / 2), self.pos[1] - (self.size[1] / 2), self.size[0],
                                self.size[1])
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
        text_rect = text_surface.get_rect(center=(self.size[0] / 2, self.size[1] / 2))
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


class Checkbox:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from the middle of box
        dim (int): takes value used for width and height of box
        states (list): takes stored volume levels
    """
    def __init__(self, pos: tuple, dim: int, states: list):
        self.pos = pos
        self.size = (dim, dim)
        self.rect = pygame.Rect(self.pos[0] - (self.size[0]/2), self.pos[1] - (self.size[1]/2), self.size[0], self.size[1])
        self.checked = states[2]  # True/False

        # Load images from folder
        self.unchecked_image = pygame.image.load("assets/menuAssets/unchecked_box.png")
        self.checked_image = pygame.image.load("assets/menuAssets/checked_box.png")

        self.unchecked_image = pygame.transform.scale(self.unchecked_image, self.size)
        self.checked_image = pygame.transform.scale(self.checked_image, self.size)

    def draw(self, screen):
        if self.checked:
            screen.blit(self.checked_image, (self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2))
        else:
            screen.blit(self.unchecked_image, (self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2))

    def handle_event(self, event, states):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.checked = not self.checked
            states[2] = self.checked

            with open('audioLevels.txt', 'r') as audioFile:
                lines = audioFile.readlines()
            lines[2] = str(states[2])
            with open('audioLevels.txt', 'w') as audioFile:
                audioFile.writelines(lines)

            if self.checked:
                pygame.mixer.music.pause()
                print("MUTED")
            else:
                pygame.mixer.music.unpause()
                print("UNMUTED")

class Slider:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from middle of line
        size (int): takes width of slider
        audio (str): determines what audio to adjust
        states (list): takes stored volume levels
    """
    def __init__(self, pos: tuple, size: int, audio: str, states: list):
        if audio not in ["music", "sfx"]:
            raise ValueError("Audio must be 'music' or 'sfx' for Slider() class initialization")

        self.audio = audio
        self.pos = pos
        self.size = size

        self.min = 0
        self.max = 75
        self.dragging = False

        self.slider_left = self.pos[0] - (size//2)
        self.slider_right = self.pos[0] + (size//2)
        self.initial_val = self.slider_right   # set base volume at 100%

        self.circle_radius = 10
        if audio == "music":
            self.button_pos = (int(self.slider_left+((self.slider_right - self.slider_left)*states[0])), int(self.pos[1]))
        elif audio == "sfx":
            self.button_pos = (int(self.slider_left+((self.slider_right - self.slider_left)*states[1])), int(self.pos[1]))

    def draw(self, screen):
        pygame.draw.line(screen, (190, 190, 190), (self.slider_left, self.pos[1]), (self.slider_right, self.pos[1]), 5)
        pygame.draw.circle(screen, (34, 90, 48), self.button_pos, self.circle_radius)

    def move_slider(self, mouse_pos, states):
        x_val = min(max(mouse_pos[0], self.slider_left), self.slider_right)
        self.button_pos = (int(x_val), int(self.pos[1]))
        if self.audio == 'music':
            states[0] = 1-((self.slider_right-x_val)/300)
            with open('audioLevels.txt', 'r') as audioFile:
                lines = audioFile.readlines()
            lines[0] = str(states[0]) + "\n"
            with open('audioLevels.txt', 'w') as audioFile:
                audioFile.writelines(lines)

        elif self.audio == 'sfx':
            states[1] = 1-((self.slider_right-x_val)/300)

            with open('audioLevels.txt', 'r') as audioFile:
                lines = audioFile.readlines()
            lines[1] = str(states[1]) + "\n"
            with open('audioLevels.txt', 'w') as audioFile:
                audioFile.writelines(lines)

    def handle_event(self, mouse_pos, mouse, states):
        distance = (mouse_pos[0] - self.button_pos[0])**2 + (mouse_pos[1] - self.button_pos[1])**2
        if distance <= self.circle_radius**2 and mouse[0] and not self.dragging:
            self.dragging = True

        if mouse[0] and self.dragging:
            self.move_slider(mouse_pos, states)
            if self.audio == 'music':
                pygame.mixer.music.set_volume(self.get_value()/100)

        if not mouse[0]:
            self.dragging = False

    def get_value(self):
        val_range = self.slider_right - self.slider_left - 1
        button_val = self.button_pos[0] - self.slider_left
        value = (button_val/val_range) * (self.max-self.min) + self.min
        if value > 98.5:
            return 100.0
        elif value < 1.5:
            return 0.0
        else:
            return value

class ColorfulButton:
    """
    Args:
        pos (tuple): take (x, y) position on screen, centered from middle of box
        size (tuple): takes (width, height) of rectangle
        text (str): places text on button
        action: performs function when clicked
    """

    def __init__(self, pos: tuple, size: tuple, text: str, action=None):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos[0] - (self.size[0] / 2), self.pos[1] - (self.size[1] / 2), self.size[0],
                                self.size[1])
        self.text = text
        self.action = action
        self.default_color = (190, 190, 190)
        self.color = (190, 190, 190)
        self.hover_color = (210, 210, 210)
        self.hovered = False

    def draw(self, screen):
        self.handle_hover()

        button_surface = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, self.color, (0, 0, self.size[0], self.size[1]), border_radius=7)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (34, 90, 48))
        text_rect = text_surface.get_rect(center=(self.size[0] / 2, self.size[1] / 2))
        button_surface.blit(text_surface, text_rect)
        button_rect = button_surface.get_rect(center=(self.pos[0], self.pos[1]))

        screen.blit(button_surface, button_rect)

    def handle_hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hovered = True
            self.color = self.hover_color
        else:
            self.hovered = False
            self.color = self.default_color

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.action:
                self.action()