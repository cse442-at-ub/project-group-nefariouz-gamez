import pygame, os
from MenuWidgets import *

pygame.init()

WIDTH, HEIGHT = 1200, 800
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

font = pygame.font.Font(None, 32)
f = open("CurrentCharacter.txt", "r")
text = font.render("You are currently playing as " + f.read() + "!", False, "Black")
current_character = f.read()


# onClick events for each character and the OK button
def click_Celia():
    global current_character
    global text
    current_character = "Celia"
    text = font.render("You have selected Celia", False, "Black")
    Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Celia1.png'))
    PlatformCelia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformCelia.png'))

    Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMaia.png'))
    Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveOscar.png'))
    Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMalcolm.png'))

    PlatformMalcolm.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDMalcolm.png'))
    PlatformMaia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDMaia.png'))
    PlatformOscar.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDOscar.png'))


def click_Malcolm():
    global current_character
    global text
    current_character = "Malcolm"
    text = font.render("You have selected Malcolm", False, "Black")
    Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Malcolm1.png'))
    PlatformMalcolm.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformMalcolm.png'))

    Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveCelia.png'))
    Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMaia.png'))
    Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveOscar.png'))

    PlatformCelia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDCelia.png'))
    PlatformMaia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDMaia.png'))
    PlatformOscar.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDOscar.png'))


def click_Maia():
    global current_character
    global text
    current_character = "Maia"
    text = font.render("You have selected Maia", False, "Black")
    Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Maia1.png'))
    PlatformMaia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformMaia.png'))
    
    Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveCelia.png'))
    Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveOscar.png'))
    Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMalcolm.png'))

    PlatformCelia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDCelia.png'))
    PlatformMalcolm.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDMalcolm.png'))
    PlatformOscar.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDOscar.png'))


def click_Oscar():
    global current_character
    global text
    current_character = "Oscar" 
    text = font.render("You have selected Oscar", False, "Black")
    Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Oscar1.png'))
    PlatformOscar.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformOscar.png'))

    Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveCelia.png'))
    Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMaia.png'))
    Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMalcolm.png'))

    PlatformCelia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDCelia.png'))
    PlatformMalcolm.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDMalcolm.png'))
    PlatformMaia.image = pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformDMaia.png'))


# confirms player's selected choice, writes character's name to "CurrentCharacter.txt"
def click_OK():
    global current_character
    global text
    f = open("CurrentCharacter.txt", "w")
    f.write(current_character)
    f.close()
    f = open("CurrentCharacter.txt", "r")
    print("Final selection =", f.read())
    pygame.quit()
    # would then move user from this page back to the settings page


# class that allows sprites to be clicked on
class ClickableSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, callback):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.callback = callback
 
    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos):
                    self.callback()

# initializing characters, their platforms, and OK button as clickable objects
Celia = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Celia1.png')), 50, 330, click_Celia)
Malcolm = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Malcolm1.png')), 250, 350, click_Malcolm)
Maia = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Maia1.png')), 450, 350, click_Maia)
Oscar = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Oscar1.png')), 650, 330, click_Oscar)

PlatformCelia = ClickableSprite(pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformCelia.png')), Celia.rect.x, Celia.rect.y + 60, click_Celia)
PlatformMalcolm = ClickableSprite(pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformMalcolm.png')), Malcolm.rect.x, Malcolm.rect.y + 60, click_Malcolm)
PlatformMaia = ClickableSprite(pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformMaia.png')), Maia.rect.x, Maia.rect.y + 60, click_Maia)
PlatformOscar = ClickableSprite(pygame.image.load(os.path.join('assets', 'Platforms', 'PlatformOscar.png')), Oscar.rect.x, Oscar.rect.y + 60, click_Oscar)

# OK_button = ClickableSprite(pygame.Surface((100,100)), 450, 700, click_OK)
# OK_button.image.fill("Grey")
# group sprites and their platforms

# check the pre-exisiting selection (default = Celia)
f = open("CurrentCharacter.txt", "r")
current_character = f.read()
if current_character == "":
    print(".txt Empty")
    f.close()
    f = open("CurrentCharacter.txt", "w")
    f.write("Celia")
    f.close()
    f = open("CurrentCharacter.txt", "r")
    click_Celia()
elif current_character == "Celia":
    click_Celia()
elif current_character == "Malcolm":
    click_Malcolm()
elif current_character == "Maia":
    click_Maia()
elif current_character == "Oscar":
    click_Oscar()
f = open("CurrentCharacter.txt", "r")
text = font.render("You are currently playing as " + f.read() + "!", False, "Black")

def main(window):
    background = pygame.image.load("assets/Background/plain_background.png")
    size = pygame.display.get_window_size()
    background = pygame.transform.scale(background, size)
    widgets = [Button((size[0]/2, (size[1]/2) + 350), (300, 54), "OK", click_OK)]

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            for widget in widgets:
                if type(widget) == Button:
                    widget.handle_event(event)
            

        background = pygame.image.load("assets/Background/plain_background.png")
        size = pygame.display.get_window_size()
        background = pygame.transform.scale(background, size)
        widgets = [Button((size[0]/2, (size[1]/2) + 350), (300, 54), "OK", click_OK)]

        x, y = size[0]/6, size[1]/2
        Celia.rect.x, Celia.rect.y = x, y - 60
        Malcolm.rect.x, Malcolm.rect.y = x * 2, y - 45
        Maia.rect.x, Maia.rect.y = x * 3, y - 45
        Oscar.rect.x, Oscar.rect.y = x * 4, y - 60

        PlatformCelia.rect.x, PlatformCelia.rect.y = x, y
        PlatformMalcolm.rect.x, PlatformMalcolm.rect.y = x * 2, y + 15
        PlatformMaia.rect.x, PlatformMaia.rect.y = x * 3, y + 15
        PlatformOscar.rect.x, PlatformOscar.rect.y = x * 4, y

           
        window.blit(background, (0, 0))

        spriteGroup = pygame.sprite.Group(Celia, Malcolm, Maia, Oscar)
        platformGroup = pygame.sprite.Group(PlatformCelia, PlatformMalcolm, PlatformMaia, PlatformOscar)

        platformGroup.update(events)
        platformGroup.draw(window)

        spriteGroup.update(events)
        spriteGroup.draw(window)

        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, 50)
        window.blit(text, textRect)
        
        for widget in widgets:
            widget.draw(window)

        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main(window) 