# environment setup taken from freeCodeCamp.org on Youtube: https://www.youtube.com/watch?v=6gLeplbqtqg
# basis for player movement/collision, background setup from same source
import os
import random
import math
import pygame
import sys

from gameObjects import Object, Platform, Block, smallShrub, TallShrub, Spike, Water, FallPlat, Ladder, endSign, BlackSpike,BlackLSpike,BlackRSpike,BlueSpike, SideSpike, ReverseSmallShrub, Void, MovePlat, MovePlatVert, MovePlatDiag, TallPinkShrub,TallPurpleShrub,TallRedShrub,SmallPinkShrub,SmallPurpleShrub,SmallRedShrub,RedSpike,BlueSpike,GoldSpike,GreenSpike,GoldDSpike,GoldLSpike,GoldRSpike,GreenDSpike,GreenLSpike,GreenRSpike, AnglePlat, AngleSpike
from MenuWidgets import *
from tutorial_page import show_tutorial
from pause_menu import show_pause_menu
from level_timer import *

from os import listdir
from os.path import isfile, join
#from pygame.sprite import _Group

pygame.init()

VOLUME_STATES = [1, 1, False]   # music slider pos (start at 100%), sfx slider pos (start at 100%), checkbox status (starts unchecked)
pygame.mixer.music.load("assets/audio/background_music.mp3")   # https://www.youtube.com/watch?v=cTDSFCC9rQ4
pygame.mixer.music.play(loops=-1)   # play and loop music indefinitely
pygame.mixer.music.set_volume(.75)   # initialize max volume of music

pygame.display.set_caption("Shrubbery Quest")
GRAVITY=1#Rate at which objects and players fall
WIDTH, HEIGHT = 1200, 800 #Exact size of figma levels, 1-1 for design purposes
FPS = 60
PLAYER_VEL=5 #Player Movement speed
WHITE=(255,255,255)
PURPLE=(128,0,128)
BEIGE=(200,200,161)
ORANGE=(255, 102, 0)
ENDLEVEL = False

window = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)
timer = Timer()
global last_pause_time

##############################################################
##############################################################
###################### PLAYER OBJECT #########################
##############################################################
##############################################################
current_object = None

def flip_image(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(directory1, directory2, width, height, direction=False):
    path = join("assets", directory1, directory2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        pygame.display.get_surface()
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            # scales all sprite sheets up double size (including player)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip_image(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

class Player(pygame.sprite.Sprite):
    ANIMATION_DELAY = 4
    GRAVITY = 1

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.xO=x#For respawning purposes
        self.yO=y
        self.wO=width
        self.hO=height
        self.x_velocity, self.y_velocity = 0, 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.in_air=False
        self.on_ladder=False
        self.e_timer=0
        self.chop = False
        self.chop_count = 0

        self.reachBox=Platform(x-15,y-15,width*2.5,height*1.2,WHITE)#Invisible bounding box for interacting with objects
        self.reachBox.surface=pygame.Surface((width*3,height*1.5))
        self.reachBox.mask = pygame.mask.from_surface(self.reachBox.surface)

        self.powerup_timer = 0
        self.powerup_active = False
        self.cooldown_timer = 0
        self.cooldown_active = False

    def reset(self,level):
        self.rect=pygame.Rect(level.init_x, level.init_y,self.wO,self.hO)
        self.reachBox.x=self.rect.x-15
        self.reachBox.y=self.rect.y-15
        self.x_velocity=0
        self.y_velocity=0
        self.update()
        level.reset()


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.reachBox.rect.x=self.rect.x-15
        self.reachBox.rect.y=self.rect.y-15

    def move_left(self, velocity):
        self.x_velocity = -velocity
        if self.direction != "left":
            #if self.in_air: Old bug fix for mid air flip image collisions
                #self.rect.x+=6
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velocity):
        self.x_velocity = velocity
        if self.direction != "right":
            #if self.in_air:
                #self.rect.x-=6
            self.direction = "right"
            self.animation_count = 0
    def move_up(self, velocity):
        self.y_velocity=-velocity
    def move_down(self, velocity):
        self.y_velocity=velocity
    # does not allow double jump
    def jump(self):
        global current_character
        if self.y_velocity > .5:# Can only jump if not going down
            placeholder=0
        else:# if not falling
            self.rect.y-=1#avoid falling through the floor glitch
            self.in_air=True#anti=double jump
            self.y_velocity = -self.GRAVITY * 4.5
            self.animation_count = 0
            self.jump_count += 1
            if self.jump_count == 1:
                self.fall_count = 0
            if self.jump_count == 2:
                self.y_velocity = -self.GRAVITY * 7

    def landed(self):
        self.in_air=False
        self.fall_count = 0
        self.y_velocity = 0
        self.jump_count = 0

    def hit_head(self):
        # fall_count?
        self.count = 0
        self.rect.y+=1
        self.y_velocity *= -1

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def do_chop(self):
        self.animation_count = 0
        self.chop = True

    def update_sprite(self):
        f = open("CurrentCharacter.txt", "r")
        current_character = f.read()

        if current_character == "":
            current_character = "Celia"
            f.close()
            f = open("CurrentCharacter.txt", "w")
            f.write("Celia")

        #print("Spritesheet to be opened:", current_character)

        character_sprites = load_sprite_sheets("Characters", current_character, 32, 32, True)

        keys = pygame.key.get_pressed()
        if self.powerup_active == False:
            sprite_sheet = "idle"
            # if self.hit:
            #     sprite_sheet = "hit"
            if self.chop:
                sprite_sheet = "chop"
                self.chop_count += 1
                if self.chop_count == 1:
                    current_object.destroy() 
            elif self.y_velocity < 0:
                if self.jump_count == 1:
                    if not self.chop:
                        sprite_sheet = "jump"
                    else:
                        sprite_sheet = "chop"
                elif self.jump_count == 2:
                    if not self.chop:
                        sprite_sheet = "double_jump" # TODO replace Malcolm and Oscar's animation in files (create 2 new animations)
                    else:
                        sprite_sheet = "chop"

            elif self.y_velocity > self.GRAVITY*2:
                sprite_sheet = "fall"
            elif self.x_velocity != 0:
                sprite_sheet = "run"
            if self.on_ladder:
                if keys[pygame.K_w] or keys[pygame.K_s]:
                    sprite_sheet = "climb"
                else:
                    sprite_sheet = "climb_idle"


        elif self.powerup_active == True:
            sprite_sheet = "cooldown_idle"
            # if self.hit:
            #     sprite_sheet = "cooldown_hit"
            if self.chop:
                sprite_sheet = "cooldown_chop"
                self.chop_count += 1
                if self.chop_count == 1:
                    current_object.destroy()
            elif self.y_velocity < 0:
                if self.jump_count == 1:
                    if not self.chop:
                        sprite_sheet = "cooldown_jump"
                    else:
                        sprite_sheet = "cooldown_chop"
                elif self.jump_count == 2:
                    if not self.chop:
                        sprite_sheet = "cooldown_double_jump"
                    else:
                        sprite_sheet = "cooldown_chop"

            elif self.y_velocity > self.GRAVITY*2:
                sprite_sheet = "cooldown_fall"
            elif self.x_velocity != 0:
                sprite_sheet = "cooldown_run"
            if self.on_ladder:
                if keys[pygame.K_w] or keys[pygame.K_s]:
                    sprite_sheet = "cooldown_climb"
                else:
                    sprite_sheet = "cooldown_climb_idle"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = character_sprites[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def loop(self, fps):
        global current_object

        # gravity
        if self.e_timer!=0:
            self.e_timer-=1

        if not self.on_ladder:#only apply gravity when not on ladder
            self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        # POWER UP AND COOLDOWN TIMERS
        if self.powerup_timer != 0:
            self.powerup_active = True
            self.powerup_timer -= 1

            if self.powerup_timer == 0:
                print("powerup timer ran out")
                self.powerup_active = False
                self.cooldown_active = True
        
        if self.cooldown_active:
            self.cooldown_timer -= 1
            if self.cooldown_timer == 0:
                self.cooldown_active = False
                print("cooldown over")


        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        # FIXED NO LOOP YAY!!!!! :D
        
        if self.chop_count > fps/30:
            self.chop_count = 0
            self.chop = False
            current_object = None

        self.fall_count += 1
        self.update_sprite()

    def draw(self, window, offset_x):
        #self.reachBox.draw(window,0)------------VISUALISE reachBox
        window.blit(self.sprite, (self.rect.x + offset_x, self.rect.y))# - to +

##############################################################
##############################################################
######################## MAIN MENU ###########################
##############################################################
##############################################################

def scale_window_main(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("assets/Background/TitleNoShear.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))   # scale background to resolution

    # creates widgets based on screen size
    widgets = [
        Button((screen_width/2, (screen_height/2)-120), (300, 54), "BEGIN YOUR QUEST", start_game),
        Button((screen_width/2, (screen_height/2)-40), (300, 54), "LOAD LEVEL", load_level),
        Button((screen_width/2, (screen_height/2)+40), (300, 54), "SETTINGS", settings),
        Button((screen_width/2, (screen_height/2)+120), (300, 54), "QUIT", quit_game)
    ]

    return widgets, background_img

def start_game():
    # Always Loads Level 1
    lvlf = open("currentLevel.txt", "w")
    lvlf.write("1")
    lvlf.close()

    display_tut(window)

def load_level():
    # Loads level based on what current level you're on in
    lvlfile = open("currentLevel.txt", "r")
    currlvl = lvlfile.read()

    match currlvl:
        case "2":
            loadLevel(window, levelTwo)
        case "3":
            loadLevel(window, levelThree)
        case "4":
            loadLevel(window, levelFour)
        case "5":
            loadLevel(window, levelFive)
        case "6":
            loadLevel(window, levelSix)
        case "7":
            loadLevel(window, levelSeven)
        case "8":
            loadLevel(window, levelEight)
        case "9":
            loadLevel(window, levelNine)
        case "10":
            loadLevel(window, levelTen)
        case "11":
            loadLevel(window, levelEleven)
        case "12":
            loadLevel(window, levelTwelve)
        case "13":
            loadLevel(window, levelThirteen)
        case "14":
            loadLevel(window, levelFourteen)
        case "15":
            loadLevel(window, levelFifteen)
        case "16":
            loadLevel(window, levelSixteen)
        case "17":
            loadLevel(window, levelSeventeen)
        case "18":
            loadLevel(window, levelEighteen)
        case "19":
            loadLevel(window, levelNineteen)
        case "20":
            loadLevel(window, levelTwenty)

    print("LOAD LEVEL " + currlvl)

def settings():
    display_settings_page(window)
    print("SETTINGS")

def quit_game():
    pygame.quit()
    sys.exit()

def display_main_menu(screen):
    widgets, background_img = scale_window_main(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                widgets, background_img = scale_window_main(screen)   # rescales visuals for new resolution

            # checks for buttons clicked
            for widget in widgets:
                widget.handle_event(event)

        # add background image and buttons to window
        screen.blit(background_img, (0, 0))

        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()

    pygame.quit()


##############################################################
##############################################################
######################## TUTORIAL ############################
##############################################################
##############################################################

def scale_window_tut(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("assets/Background/newgameexplan.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))   # scale background to resolution

    # creates widgets based on screen size
    widgets = [
        Button((screen_width/2, (screen_height-200)), (300, 54), "CONTINUE TO GAME", cont_game),
    ]

    return widgets, background_img

def cont_game():
    # Always Loads Level 1
    loadLevel(window, levelOne)

def display_tut(screen):
    widgets, background_img = scale_window_tut(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                widgets, background_img = scale_window_tut(screen)   # rescales visuals for new resolution

            # checks for buttons clicked
            for widget in widgets:
                widget.handle_event(event)

        # add background image and buttons to window
        screen.blit(background_img, (0, 0))

        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()

    pygame.quit()

##############################################################
##############################################################
######################## SETTINGS ############################
##############################################################
##############################################################

def scale_window_settings(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("assets/Background/BetLvlBackground.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))   # scale background to resolution

    # create widgets based on screen size
    widgets = [
        Slider(((screen_width/2)+150, (screen_height/2)-190), 300, 'music', VOLUME_STATES),
        Slider(((screen_width/2)+150, (screen_height/2)-110), 300, 'sfx',VOLUME_STATES),
        Checkbox(((screen_width/2+27), (screen_height/2)-30), 54, VOLUME_STATES),
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
    window.blit(img, centered_pos)

def tutorial():
    show_tutorial(window)

def choose_character():
    display_choose_character(window)
    print("CHOOSE CHARACTER")

def return_main():
    display_main_menu(window)
    print("RETURN TO MAIN")

def display_settings_page(screen):
    widgets, screen_width, screen_height, background_img = scale_window_settings(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                widgets, screen_width, screen_height, background_img = scale_window_settings(screen)   # rescales visuals for new resolution

            for widget in widgets:
                if type(widget) == Button:
                    widget.handle_event(event)
                elif type(widget) == Checkbox:
                    widget.handle_event(event, VOLUME_STATES)
                elif type(widget) == Slider:
                    widget.handle_event(pygame.mouse.get_pos(), pygame.mouse.get_pressed(), VOLUME_STATES)

        # render background and widgets
        screen.blit(background_img, (0, 0))
        draw_text("MUSIC VOLUME", pygame.font.Font(None, 36), (34, 90, 48), ((screen_width/2)-150, (screen_height/2)-190))
        draw_text("SFX VOLUME", pygame.font.Font(None, 36), (34, 90, 48), ((screen_width/2)-150, (screen_height/2)-110))
        draw_text("MUTE", pygame.font.Font(None, 36), (34, 90, 48), ((screen_width/2)-150, (screen_height/2)-30))

        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()

    pygame.quit()


##############################################################
##############################################################
################# CHOOSE CHARACTER SCREEN ####################
##############################################################
##############################################################

character_select_font = pygame.font.Font(None, 32)

f = open("CurrentCharacter.txt", "r")
current_character = f.read()
powerup_read, cooldown_read = "", ""

maxlevelread = open("MaxUnlocked.txt", "r")
max_level_unlocked = maxlevelread.read()
if current_character == "" or max_level_unlocked == "" or int(max_level_unlocked) < 5:
    current_character = "Celia"
    f.close()
    f = open("CurrentCharacter.txt", "w")
    f.write("Celia")
    f.close()
    f = open("CurrentCharacter.txt", "r")
    powerup_read = "N/A"
elif (current_character == "Malcolm" and int(max_level_unlocked) < 5) or (current_character == "Maia" and int(max_level_unlocked) < 10) or (current_character == "Oscar" and int(max_level_unlocked) < 15):
    current_character = "Celia"
    f.close()
    f = open("CurrentCharacter.txt", "w")
    f.write("Celia")
    f.close()
    f = open("CurrentCharacter.txt", "r")
    powerup_read = "N/A"

char_text_color = "black"

if current_character == "Celia" or current_character == "":
    char_text_color = "darkgreen"
elif current_character == "Malcolm":
    char_text_color = "darkorange4"
elif current_character == "Maia":
    char_text_color = "maroon3"
elif current_character == "Oscar":
    char_text_color = "indigo"

selected_text = character_select_font.render("You are currently playing as", False, "Black")
char_text_color = "black"
character_text = character_select_font.render(current_character, False, char_text_color)
powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")
cooldown_text = character_select_font.render(cooldown_read, False, "Black")
print(current_character)
clevel = open("currentLevel.txt", "r")
current_level = clevel.read()
max_level = str(int(current_level) - 1)
clevel.close()
maxlevelread.close()
if max_level_unlocked == "" or int(max_level_unlocked) < int(max_level):
    max_level_unlocked = max_level
    w_max = open("MaxUnlocked.txt", "w")
    w_max.write(str(max_level_unlocked))
    w_max.close()

def click_Celia():
    global current_character
    global character_text
    global selected_text
    global powerup_read
    global powerup_text
    global cooldown_read
    global cooldown_text
    current_character = "Celia"
    selected_text = character_select_font.render("You have selected", False, "Black")
    character_text = character_select_font.render("Celia", False, "darkgreen")
    
    powerup_read = "N/A"
    cooldown_read = ""
    powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")
    cooldown_text = character_select_font.render(cooldown_read, False, "Black")


    Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Celia.png'))
    Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMalcolm.png'))
    Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMaia.png'))
    Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveOscar.png'))

    check_unlocked_level()


def click_Malcolm():
    global current_character
    global character_text
    global selected_text
    global powerup_read
    global powerup_text
    global cooldown_read
    global cooldown_text

    maxlevelread = open("MaxUnlocked.txt", "r")
    max_level_unlocked = maxlevelread.read()
    
    if max_level_unlocked != "" and int(max_level_unlocked) >= 5:
        current_character = "Malcolm"
        powerup_read = "Double jump in air"
        cooldown_read = ""
        powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")
        cooldown_text = character_select_font.render(cooldown_read, False, "Black")
        selected_text = character_select_font.render("You have selected", False, "Black")
        character_text = character_select_font.render("Malcolm", False, "darkorange4")
        Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Malcolm.png'))
        Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveCelia.png'))
    Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMaia.png'))
    Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveOscar.png'))

    check_unlocked_level()


def click_Maia():
    global current_character
    global character_text
    global selected_text
    global powerup_read
    global powerup_text
    global cooldown_read
    global cooldown_text

    maxlevelread = open("MaxUnlocked.txt", "r")
    max_level_unlocked = maxlevelread.read() 
    
    if max_level_unlocked != "" and int(max_level_unlocked) >= 10:
        current_character = "Maia"
        powerup_read = "Walk through shrubs for 5 seconds (15 sec cooldown)"
        cooldown_read = ""
        powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")
        cooldown_text = character_select_font.render(cooldown_read, False, "Black")
        selected_text = character_select_font.render("You have selected", False, "Black")
        character_text = character_select_font.render("Maia", False, "maroon3")
        Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Maia.png'))
        Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveCelia.png'))
        Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMalcolm.png'))
    Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveOscar.png'))
    
    check_unlocked_level()


def click_Oscar():
    global current_character
    global character_text
    global selected_text
    global powerup_read
    global powerup_text
    global cooldown_read
    global cooldown_text
    

    maxlevelread = open("MaxUnlocked.txt", "r")
    max_level_unlocked = maxlevelread.read()
    
    if max_level_unlocked != "" and int(max_level_unlocked) >= 15:
        current_character = "Oscar"
        powerup_read = "Walk through shrubs and spikes for 5 seconds (30 sec cooldown)"
        cooldown_read = "Can also double jump in air"
        selected_text = character_select_font.render("You have selected", False, "Black")
        character_text = character_select_font.render("Oscar", False, "indigo")
        powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")
        cooldown_text = character_select_font.render(cooldown_read, False, "Black")
        Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Oscar.png'))
        Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveCelia.png'))
        Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMalcolm.png'))
        Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'DeactiveMaia.png'))

    check_unlocked_level()


# confirms player's selected choice, writes character's name to "CurrentCharacter.txt"
def click_OK():
    global current_character
    f = open("CurrentCharacter.txt", "w")
    f.write(current_character)
    f.close()
    f = open("CurrentCharacter.txt", "r")
    print("Final selection =", f.read())
    display_settings_page(window)


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
Celia = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Celia.png')), 50, 330, click_Celia)
Malcolm = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Malcolm.png')), 250, 350, click_Malcolm)
Maia = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Maia.png')), 450, 350, click_Maia)
Oscar = ClickableSprite(pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Oscar.png')), 650, 330, click_Oscar)


def check_update():
    global current_character
    global character_text
    global selected_text
    global powerup_text
    global cooldown_text
    global char_text_color

    check_unlocked_level()

    f = open("CurrentCharacter.txt", "r")
    current_character = f.read()
    print(current_character)
    maxlevelread = open("MaxUnlocked.txt", "r")
    max_level_unlocked = maxlevelread.read()
    
    if current_character == "" or max_level_unlocked == "" or int(max_level_unlocked) < 5:
        f.close()
        f = open("CurrentCharacter.txt", "w")
        f.write("Celia")
        f.close()
        f = open("CurrentCharacter.txt", "r")
        click_Celia()
    elif (current_character == "Malcolm" and int(max_level_unlocked) < 5) or (current_character == "Maia" and int(max_level_unlocked) < 10) or (current_character == "Oscar" and int(max_level_unlocked) < 15):
        f.close()
        f = open("CurrentCharacter.txt", "w")
        f.write("Celia")
        f.close()
        f = open("CurrentCharacter.txt", "r")
        click_Celia()
    elif current_character == "Celia":
        char_text_color = "darkgreen"
        click_Celia()
    elif current_character == "Malcolm":
        char_text_color = "darkorange4"
        click_Malcolm()
    elif current_character == "Maia":
        char_text_color = "maroon3"
        click_Maia()
    elif current_character == "Oscar":
        char_text_color = "indigo"
        click_Oscar()
    f = open("CurrentCharacter.txt", "r")
    selected_text = character_select_font.render("You are currently playing as", False, "Black")
    character_text = character_select_font.render(current_character, False, char_text_color)
    powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")    
    cooldown_text = character_select_font.render(cooldown_read, False, "Black")
    print(current_character)
    

def check_unlocked_level():
    global current_character

    maxlevelread = open("MaxUnlocked.txt", "r")
    max_level_unlocked = maxlevelread.read()

    if max_level_unlocked == "" or int(max_level_unlocked) < 5:
        current_character = "Celia"
        f = open("CurrentCharacter.txt", "w")
        f.write("Celia")
        f.close()
        Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Celia.png'))
        Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'LockedMalcolm.png'))
        Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'LockedMaia.png'))
        Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'LockedOscar.png'))
    elif int(max_level_unlocked) < 10:
        Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'LockedMaia.png'))
        Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'LockedOscar.png'))
    elif int(max_level_unlocked) < 15:
        Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'LockedOscar.png'))


def display_choose_character(window):
    background = pygame.image.load("assets/Background/BetLvlBackground.png")
    size = pygame.display.get_window_size()
    screen_width, screen_height = size[0], size[1]
    background = pygame.transform.scale(background, size)
    widgets = [Button((screen_width/2, (screen_height/2) + 160), (300, 54), "OK", click_OK)]
    
    check_update()
    check_unlocked_level()


    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            for widget in widgets:
                if type(widget) == Button:
                    widget.handle_event(event)

        background = pygame.image.load("assets/Background/BetLvlBackground.png")
        size = pygame.display.get_window_size()
        background = pygame.transform.scale(background, size)
        widgets = [Button((screen_width/2, (screen_height/2) + 160), (300, 54), "OK", click_OK)]

        x, y = size[0]/6, size[1]/2

        const_size_1 = 220
        Celia.rect.x, Celia.rect.y = x, y - const_size_1
        Malcolm.rect.x, Malcolm.rect.y = x * 2, y - const_size_1
        Maia.rect.x, Maia.rect.y = x * 3, y - const_size_1
        Oscar.rect.x, Oscar.rect.y = x * 4, y - const_size_1

        window.blit(background, (0, 0))

        spriteGroup = pygame.sprite.Group(Celia, Malcolm, Maia, Oscar)

        spriteGroup.update(events)
        spriteGroup.draw(window)

        selectedTextRect = selected_text.get_rect()
        selectedTextRect.center = (screen_width // 2, 45)
        window.blit(selected_text, selectedTextRect)

        characterTextRect = character_text.get_rect()
        characterTextRect.center = (screen_width // 2, 75)
        window.blit(character_text, characterTextRect)

        powerupTextRect = powerup_text.get_rect()
        powerupTextRect.center = (screen_width // 2, 120)
        window.blit(powerup_text, powerupTextRect)

        cooldownTextRect = cooldown_text.get_rect()
        cooldownTextRect.center = (screen_width // 2, 150)
        window.blit(cooldown_text, cooldownTextRect)

        for widget in widgets:
            widget.draw(window)

        pygame.display.update()

    pygame.quit()


##############################################################
##############################################################
################### BETWEEN LEVEL SCREEN #####################
##############################################################
##############################################################

def scale_window_between(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("assets\Background\BetlvlBackground.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))   # scale background to resolution

    # create widgets based on screen size
    widgets = [
        Button((screen_width/2, (screen_height/2)+20), (300, 54), "CONTINUE", continuelvl),
        Button((screen_width/2, (screen_height/2)+100), (300, 54), "RETURN TO MAIN", return_main)
    ]

    return widgets, screen_width, screen_height, background_img


def continuelvl():
    lvlf = open("currentLevel.txt", "r")
    currlvl = lvlf.read()

    match currlvl:
        case "2":
            loadLevel(window, levelTwo)
        case "3":
            loadLevel(window, levelThree)
        case "4":
            loadLevel(window, levelFour)
        case "5":
            loadLevel(window, levelFive)
        case "6":
            loadLevel(window, levelSix)
        case "7":
            loadLevel(window, levelSeven)
        case "8":
            loadLevel(window, levelEight)
        case "9":
            loadLevel(window, levelNine)
        case "10":
            loadLevel(window, levelTen)
        case "11":
            loadLevel(window, levelEleven)
        case "12":
            loadLevel(window, levelTwelve)
        case "13":
            loadLevel(window, levelThirteen)
        case "14":
            loadLevel(window, levelFourteen)
        case "15":
            loadLevel(window, levelFifteen)
        case "16":
            loadLevel(window, levelSixteen)
        case "17":
            loadLevel(window, levelSeventeen)
        case "18":
            loadLevel(window, levelEighteen)
        case "19":
            loadLevel(window, levelNineteen)
        case "20":
            loadLevel(window, levelTwenty)

    print("CONTINUE")


def display_between_level_page(screen):
    widgets, screen_width, screen_height, background_img = scale_window_between(screen)

    #get level num
    lvlf = open("currentLevel.txt", "r")
    currlvl = lvlf.read()
    printlvl = str(int(currlvl) - 1)
    lvlf.close()

    maxlevelread = open("MaxUnlocked.txt", "r")
    max_level_unlocked = maxlevelread.read()
    maxlevelread.close()

    if max_level_unlocked == "" or int(max_level_unlocked) < int(printlvl):
        max_level_unlocked = printlvl
        w_max = open("MaxUnlocked.txt", "w")
        w_max.write(str(max_level_unlocked))
        w_max.close()

    currtime = str(round(timer.return_time(), 2))

    betweenlvl = True
    while betweenlvl:
        for event in pygame.event.get():
            #event handler
            if event.type == pygame.QUIT:
                betweenlvl=False

            for widget in widgets:
                if type(widget) == Button or type(widget) == Checkbox:
                    widget.handle_event(event)
                elif type(widget) == Slider:
                    widget.handle_event(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

        screen.blit(background_img, (0,0))
        draw_text("Congratulations!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-190))
        draw_text("You Beat Level " + printlvl + "!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-130))
        draw_text("Your Time Was: " + currtime + "s", pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-70))

        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()
    pygame.quit()
    

##############################################################
##############################################################
################### POST LEVEL 20 SCREEN #####################
##############################################################
##############################################################

def scale_window_endgame(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("assets\Background\BetlvlBackground.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))   # scale background to resolution

    # create widgets based on screen size
    widgets = [
        Button((screen_width/2, (screen_height/2)+50), (300, 54), "RETURN TO MAIN", return_main)
    ]

    return widgets, screen_width, screen_height, background_img


def display_endgame_level_page(screen):
    widgets, screen_width, screen_height, background_img = scale_window_endgame(screen)

    #get level num
    lvlf = open("currentLevel.txt", "r")
    currlvl = lvlf.read()
    printlvl = str(int(currlvl) - 1)
    lvlf.close()

    currtime = str(round(timer.return_time(), 2))

    betweenlvl = True
    while betweenlvl:
        for event in pygame.event.get():
            #event handler
            if event.type == pygame.QUIT:
                betweenlvl=False

            for widget in widgets:
                if type(widget) == Button or type(widget) == Checkbox:
                    widget.handle_event(event)
                elif type(widget) == Slider:
                    widget.handle_event(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

        screen.blit(background_img, (0,0))
        draw_text("Congratulations!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-190))
        draw_text("You Have Beaten Shrubbery Quest!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-130))
        draw_text("Your Time For Level 20 Was: " + currtime + "s", pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-80))
        draw_text("You Can Now Access Challenge Mode!", pygame.font.Font(None, 56),(34, 90, 48), ((screen_width/2), (screen_height/2)-30))
        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()
    pygame.quit()

##############################################################
##############################################################
######################## GAME RUNNER #########################
##############################################################
##############################################################

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

class Level():
    def __init__(self,objects,starting_x,starting_y,bgpath):
        self.background,self.bg_image=get_background(bgpath)
        self.object_list=objects.copy()
        self.init_x=starting_x
        self.init_y=starting_y
        self.copied=objects.copy()
    def reset(self):
        for object in self.object_list:
            object.reset()
    def resize(self,factor):#resize everything in object_list, init_y,init_x by factor
        x=0
    def loop(self,player):
        for object in self.object_list:
            #if object.name=="fall"or object.name=="move" or object.name=="plat":
            if object.name=="fall":
                object.check_time(player)
            if object.name=="move":
                object.loop(player)



def draw(window, background, bg_image,player,level,offset):
    for tile in background:
        offtile=(tile.__getitem__(0)+offset,tile.__getitem__(1))
        window.blit(bg_image, offtile)

    for object in level.object_list:
        object.draw(window,offset)

    player.draw(window,offset)

    pygame.display.update()


def handle_vertical_collision(player, level, dy):
    collided_objects = []
    for object in level.object_list:
        if pygame.sprite.collide_mask(player, object):
            #if(object.name=="fall"):
                #object.timer+=1
            if (object.name == "tall shrub" and player.powerup_active == True) or (object.name == "small shrub" and player.powerup_active == True):
                if current_character == "Oscar":
                    print("vertical Oscar is ignoring shrubs")
                elif current_character == "Maia":
                    print("Maia is ignoring shrubs")

            elif object.name == "spike" and current_character == "Oscar" and player.powerup_active == True:
                print("Oscar is ignoring spikes")

            elif(object.name == "spike"):
                print("hit a spike in vert")
                player.x_velocity=0
                player.y_velocity=0#Helps 0 out if gravity is huge
                player.reset(level)
                continue
            
                #keep from reseting Y
            elif dy > 0 and object.name!="ladder" and not player.on_ladder:
                if not (player.rect.bottom-2*player.y_velocity)>object.rect.top or object.name=="angle":#if the players bottom is not within 12 pixels of the object's top
                    player.rect.bottom = object.rect.top#put the player on top of the object
                    player.landed()
                else:
                    if player.rect.right>object.rect.right:#Falling off right side
                        player.rect.x=object.rect.right#(player.rect.right-object.rect.right)
                        player.rect.x+=1
                    elif player.rect.left<object.rect.left:#Falling of left side
                        player.rect.x+=(object.rect.left-player.rect.right)
                        player.rect.x-=1

            elif dy < 0 and object.name!="ladder" and not player.on_ladder:
                if object.name=="tall shrub" or object.name=="small shrub":
                    #if object.name=="small shrub":
                        #player.y_velocity=PLAYER_VEL*2
                        #player.hit_head()
                    if player.rect.right>object.rect.right:#Falling onto
                        player.rect.x=object.rect.right#(player.rect.right-object.rect.right)
                        player.rect.x+=1
                    elif player.rect.left<object.rect.left:#Falling onto left side
                        player.rect.x+=(object.rect.left-player.rect.right)
                        player.rect.x-=1
                else:
                    player.rect.top = object.rect.bottom
                    #player.rect.y+=2
                    player.y_velocity=-PLAYER_VEL*2
                    #player.rect.y=player.rect.y+5
                    player.hit_head()

            collided_objects.append(object)
    return collided_objects

def collide(player, level, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for object in level.object_list:
        if pygame.sprite.collide_mask(player, object) and object.name!="ladder" and object.name!="spike":
            collided_object = object
            if (object.name == "tall shrub" and player.powerup_active == True) or (object.name == "small shrub" and player.powerup_active == True):
                if current_character == "Oscar":
                    collided_object = None
                    print("collide() Oscar is ignoring shrubs")
                elif current_character == "Maia":
                    print("Maia is ignoring shrubs")
                    collided_object = None
            elif object.name == "spike" and current_character == "Oscar" and player.powerup_active == True:
                print("Oscar is ignoring spikes")
            elif(object.name=="spike"):
                # collided_object = object
                player.x_velocity=0
                player.y_velocity=0
                print("hit a spike in collide")
                player.reset(level)
            elif(object.name == "end sign"):
                # collided_object = object
                #PLAYER HAS REACHED END OF LEVEL
                # ADD ONE TO COMPLETED LEVELS
                #ENDLEVEL = True
                timer.stop_timer()
                lvlf = open("currentLevel.txt", "r")
                levelnum = int(lvlf.read())
                levelnum += 1
                lvlf = open("currentLevel.txt", "w")
                lvlf.write(str(levelnum))
                lvlf.close()
                # THEN OPEN BETWEEN LEVEL MENU
                if levelnum > 20:
                    open("competitive.txt", "x").close()
                    display_endgame_level_page(window)
                else:
                    display_between_level_page(window)
            break

    player.move(-dx, 0)

    player.x_velocity=0
    player.update()
    return collided_object

def checkOverlap(player,level):
    validLadder=False
    for object in level.object_list:
        if pygame.sprite.collide_mask(player.reachBox,object):
            if(object.name=="ladder"):
                validLadder=True
    return validLadder

def getOverlap(player, reachBox, level):
    global current_object
    for object in level.object_list:
        if pygame.sprite.collide_mask(reachBox,object):
            if object.name=="small shrub":
                #Handle small shrub behavior
                current_object = object
                player.do_chop()
                # object.destroy()
                return
            elif object.name=="tall shrub":
                #Handle tall shrub behavior
                current_object = object
                player.do_chop()
                # object.destroy()
                return

def destroy_it(object):
    global current_object
    object.destroy()
    current_object = None

def getInput(player, level):
    keys=pygame.key.get_pressed()
    collide_left = collide(player, level, -PLAYER_VEL*2)
    collide_right = collide(player, level, PLAYER_VEL*2)
    if player.on_ladder:
        player.y_velocity=0
        if keys[pygame.K_w]:
            g=0
            #Move up on ladder
            #check if still on ladder
            player.move_up(PLAYER_VEL)
            for object in level.object_list:
                if pygame.sprite.collide_mask(player,object):
                    if object.name=="ladder":
                        player.on_ladder=True
                        player.in_air=False
                        player.rect.x=object.rect.x-15#set x value to Ladder x Valued
                        #player.rect.y=player.rect.y+1
                        g=1
            if g==0:
                player.on_ladder=False
                player.rect.y-=8
        if keys[pygame.K_SPACE] and player.jump_count < 1:
            player.on_ladder=False
            player.jump()
        if keys[pygame.K_s]:
            #Move down on ladder
            #check if still on ladder
            g=0
            player.move_down(PLAYER_VEL)
            for object in level.object_list:
                if pygame.sprite.collide_mask(player,object):#if the player is colliding with it
                    if object.name=="ladder":#if the player is colliding with a ladder
                        if player.rect.bottom<object.rect.bottom+7:#if the players feet are above the bottom of the object
                            if g==0:#if the player has not yet been st
                                g=1
                                player.rect.x=object.rect.x-15#set x value to Ladder x Valued
                                player.on_ladder=True
                                player.in_air=False
                            #player.rect.y=player.rect.y+1
                            #player.move_down(PLAYER_VEL)
            if g==0:
                player.on_ladder=False
                #player.move_up(PLAYER_VEL)
                #player.move_down(PLAYER_VEL)#push into ground a tiny bit to reset
            else:
                player.on_ladder=True
                player.in_air=False
        if keys[pygame.K_a] and not collide_left and not player.chop:
            player.on_ladder=False
            player.move_left(PLAYER_VEL)

        if keys[pygame.K_d] and not collide_right and not player.chop:
            player.on_ladder=False
            player.move_right(PLAYER_VEL)

        if keys[pygame.K_e]:
            if player.e_timer==0:
                player.e_timer=15
                #getOverlap(player,player.reachBox,level)
                #No breaking things while on ladder, no sprites for that
        if keys[pygame.K_q]:
            x=0#placeholder

    if not player.on_ladder:
        player.x_velocity=0 #Reset

        if keys[pygame.K_w]:
            #player.rect.y-=1#move up 1 pixel, avoid getting on ladder with W at top of ladder
            for object in level.object_list:
                if pygame.sprite.collide_mask(player,object):
                    if (object.name == "tall shrub" and player.powerup_active == True) or (object.name == "small shrub" and player.powerup_active == True):
                        if current_character == "Oscar":
                            print("dy > 0 Oscar is ignoring shrubs")
                        elif current_character == "Maia":
                            print("Maia is ignoring shrubs")
                    elif object.name=="ladder":
                        if player.rect.bottom-1>object.rect.top:#prevent getting on ladder with W at top of ladder
                            player.on_ladder=True
                            player.in_air=False
                            player.rect.x=object.rect.x-15
                            player.move_up(PLAYER_VEL)

        if keys[pygame.K_SPACE] and player.jump_count < 1:
            if player.in_air==False:
                player.jump()
        if keys[pygame.K_a] and not collide_left and not player.on_ladder and not player.chop:
            player.move_left(PLAYER_VEL)
        if keys[pygame.K_s]:
            player.rect.y+=3#BOOKMARK
            for object in level.object_list:
                if pygame.sprite.collide_mask(player,object):
                    if object.name=="ladder":
                        if player.rect.bottom<object.rect.bottom:
                            player.on_ladder=True
                            player.in_air=False
                            player.rect.x=object.rect.x-15

            player.rect.y-=3
        if keys[pygame.K_d] and not collide_right and not player.on_ladder and not player.chop:
            player.move_right(PLAYER_VEL)
        if keys[pygame.K_e]:
            if player.e_timer==0:
                player.e_timer=15
                getOverlap(player,player.reachBox,level)
        if keys[pygame.K_ESCAPE]:
            timer.stop_timer()

            global last_pause_time
            time_since_last = timer.return_time() - last_pause_time
            if time_since_last > 0.40:
                if show_pause_menu(window, VOLUME_STATES):
                    display_main_menu(window)
                last_pause_time = timer.return_time()

            timer.start_timer()
            
        if current_character == "Malcolm":
            if keys[pygame.K_q] and player.jump_count == 1 and player.in_air:
                player.jump
                
        elif current_character == "Maia":
            if keys[pygame.K_q] and player.cooldown_active == False: 
                if player.powerup_timer == 0 and player.powerup_active == False  and player.cooldown_active == False:
                    player.powerup_timer = FPS*4 # about 5 seconds
                    player.cooldown_timer = FPS*12 # about 15 seconds, not exactly?

        elif current_character == "Oscar":
            if keys[pygame.K_q] and player.jump_count == 1 and player.in_air:
                player.jump()
            elif keys[pygame.K_q] and player.cooldown_active == False and not player.in_air:
                if player.powerup_timer == 0 and player.powerup_active == False  and player.cooldown_active == False:
                    player.powerup_timer = FPS*4 # about 5 seconds
                    player.cooldown_timer = FPS*22 # about 30 seconds, not exactly?

    vertical_collide = handle_vertical_collision(player, level, player.y_velocity)
    if player.on_ladder:
        if not checkOverlap(player,level):
           player.on_ladder=False


BLACK=(0,0,0)
fullScreenLeft=Platform(-2000,0,2000,2000,BLACK,None,"spike")
fullScreenRight=Platform(1201,0,2000,2000,BLACK,None,"spike")
fullScreenBottom=Platform(-2000,801,5200,2000,BLACK,None,"spike")

lOne=[]
lBorderLeft=Platform(-1,0,1,800,WHITE)
lBorderRight=Platform(1201,0,1,800,WHITE)
#Player starting position (1100, 644)
#background,bg_image = get_background("Level 1 to 3 bkgrnd.png")
start=Platform(890,670,152,75,WHITE)
base=Platform(0,720,1200,80,WHITE)
plat2=Platform(502,650,264,75,WHITE)
plat3=Platform(0,624,361,96,WHITE)
sShrub1=smallShrub(610,598)
tShrub1=TallShrub(216,441)
spike1=Spike(853,687)
spike2=Spike(813,687)
spike3=Spike(773,687)
spike4=Spike(453,687)
spike5=Spike(413,687)
spike6=Spike(373,687)
endlvl1 = endSign(10, 584)
lOne.append(start)
lOne.append(base)
lOne.append(plat2)
lOne.append(plat3)
lOne.append(sShrub1)
lOne.append(tShrub1)
lOne.append(spike1)
lOne.append(spike2)
lOne.append(spike3)
lOne.append(spike4)
lOne.append(spike5)
lOne.append(spike6)
lOne.append(endlvl1)

lOne.append(lBorderLeft)
lOne.append(lBorderRight)

lOne.append(fullScreenLeft)
lOne.append(fullScreenBottom)
lOne.append(fullScreenRight)

levelOne=Level(lOne,1135,639,"updated tutorial.png")

BROWN=(100,65,23)
BLUE=(0,0,255)
lTwo=[]
#Player starting position (1135,655)
#background,bg_image = get_background("Level 1 to 3 bkgrnd.png")
lTwo.append(Platform(1031,344,57,436,BROWN))#May just do this in the future
post2=Platform(739,364,57,436,BROWN)
post3=Platform(550,590,57,176,BROWN)
post4=Platform(159,590,57,176,BROWN)
post5=Platform(35,590,57,176,BROWN)
start2=Platform(976,624,224,176,WHITE)
water1=Water(0,720,1200,80,BLUE)
bplat1=Platform(976,324,224,20,WHITE)
bplat2=Platform(579,344,269,20,WHITE)
bplat3=Platform(436,540,286,50,WHITE)
bplat4=Platform(0,549,297,50,WHITE)
bshrub1=smallShrub(800,292)
bshrub2=smallShrub(249,497)
endlvl2 = endSign(25,509)
#lTwo.append(post1)
lTwo.append(post2)
lTwo.append(post3)
lTwo.append(post4)
lTwo.append(post5)
lTwo.append(start2)
lTwo.append(water1)
lTwo.append(bplat1)
lTwo.append(bplat2)
lTwo.append(bplat3)
lTwo.append(bplat4)
lTwo.append(bshrub1)
lTwo.append(bshrub2)
lTwo.append(Ladder(1101,524))
lTwo.append(Ladder(1101,424))
lTwo.append(Ladder(1101,324))
lTwo.append(Ladder(689,440))
lTwo.append(Ladder(689,344))


lTwo.append(lBorderLeft)
lTwo.append(lBorderRight)


lTwo.append(endlvl2)
levelTwo=Level(lTwo,1135,538,"Level 1 to 3 bkgrnd.png")

GRAY=(192,192,192)
lThree=[]
#Player Starting position (1100,559)
lThree.append(Platform(1096,599,57,176,BROWN))#POST 1
lThree.append(Platform(975,599,57,176,BROWN))#POST 2
lThree.append(Platform(643,573,57,176,BROWN))#POST 3
lThree.append(Platform(330,523,57,237,BROWN))#POST 4
lThree.append(Platform(0,0,131,800,GRAY))#MOUNTAINSIDE
lThree.append(SideSpike(131,388))
lThree.append(SideSpike(131,348))
lThree.append(SideSpike(131,308))
lThree.append(SideSpike(131,268))
lThree.append(SideSpike(131,228))
lThree.append(Water(0,720,1200,80,BLUE))#WATER
lThree.append(Platform(922,549,278,50,WHITE))#START
lThree.append(Platform(564,523,215,50,WHITE))#PLAT 1
lThree.append(Platform(258,483,200,50,WHITE))#PLAT 2
lThree.append(Platform(131,425,65,15,WHITE))#PLAT 3
lThree.append(Platform(131,103,200,23,WHITE))#PLAT 4
lThree.append(TallShrub(587,340))#TALLSHRUB 1
lThree.append(Ladder(255,229))#LADDER 1
lThree.append(Ladder(255,103))#LADDER 2
lThree.append(Ladder(255,201))#LADDER 3
lThree.append(Ladder(145,0))#LADDER 4
lThree.append(lBorderLeft)
lThree.append(lBorderRight)
lThree.append(endSign(180,63)) # END SIGN
levelThree=Level(lThree,1100,470,"Level 1 to 3 bkgrnd.png")

lFour=[]
#Player starting position (1100, 644)
#background,bg_image = get_background("CaveBackground1.png")
lFour.append(Void(960,795,244,5))
lFour.append(BlackSpike(0,767))
lFour.append(BlackSpike(40,767))
lFour.append(BlackSpike(80,767))
lFour.append(BlackSpike(120,767))
lFour.append(BlackSpike(160,767))
lFour.append(BlackSpike(200,767))
lFour.append(BlackSpike(240,767))
lFour.append(BlackSpike(280,767))
lFour.append(BlackSpike(320,767))
lFour.append(BlackSpike(360,767))
lFour.append(BlackSpike(400,767))
lFour.append(BlackSpike(440,767))
lFour.append(BlackSpike(480,767))
lFour.append(BlackSpike(520,767))
lFour.append(BlackSpike(560,767))
lFour.append(BlackSpike(600,767))
lFour.append(BlackSpike(640,767))
lFour.append(BlackSpike(680,767))
lFour.append(BlackSpike(720,767))
lFour.append(BlackSpike(760,767))
lFour.append(BlackSpike(800,767))
lFour.append(BlackSpike(840,767))
lFour.append(BlackSpike(880,767))
lFour.append(BlackSpike(920,767))
lFour.append(Platform(960,720,244,35,WHITE))
#ladder x 1105
lFour.append(Ladder(1105,720))
lFour.append(FallPlat(670,695,165,32))#First Platform
fShrub1=smallShrub(382,500)
fLadder2=Ladder(445,621)
fLadder3=Ladder(445,552)
fallGroup1=[fShrub1,fLadder2,fLadder3]
fallPlat2=FallPlat(221,552,257,48,PURPLE,fallGroup1)#platform with shrub and ladder
lFour.append(fallPlat2)
lFour.append(fLadder2)
lFour.append(fLadder3)
lFour.append(fShrub1)
lFour.append(FallPlat(600,485,257,20))#Third platform
lFour.append(FallPlat(223,420,257,15))#Fourth platform
lFour.append(Platform(0,116,200,80,WHITE))
lFour.append(Ladder(108,286))
lFour.append(Ladder(108,216))
lFour.append(Platform(0,118,200,80,WHITE))
lFour.append(Ladder(108,116))
lFour.append(Ladder(23,0))
lFour.append(lBorderLeft)
lFour.append(lBorderRight)
lFour.append(endSign(23,76)) # END SIGN
levelFour=Level(lFour,1100,635,"CaveBackground1.png")

lFive=[]
lFive.append(Void(0,800,1115,15))
lFive.append(Platform(0,700,200,80,WHITE))#Start
lFive.append(Ladder(21,700))
lFive.append(FallPlat(298,649,200,51))#Fall plat 1
lFive.append(Platform(600, 590, 170, 51,WHITE))#plat 1
lFive.append(Platform(889,573,200,51,WHITE))#plat 2
lFive.append(Platform(889,373,200,51,WHITE))#plat 3
lFive.append(Ladder(1011,373))
lFive.append(Ladder(1011, 473))
lFive.append(Platform(600,432,200,51,WHITE))#plat 4
lFive.append(ReverseSmallShrub(750,483))
lFive.append(TallShrub(752,249))
lFive.append(FallPlat(298,384,200,51))
lFive.append(Platform(56,190,200,51,WHITE))
lFive.append(Ladder(215,190))
lFive.append(Ladder(215,204))
fpShrub1=smallShrub(340,91)
fpShrub2=smallShrub(450,91)
fallGroupFive1=[fpShrub1,fpShrub2]
fiveFPlat1=FallPlat(298,143,200,51,PURPLE,fallGroupFive1)
lFive.append(fpShrub1)
lFive.append(fpShrub2)
lFive.append(fiveFPlat1)

fpShrub3=smallShrub(637,91)
fpShrub4=smallShrub(749,91)
fallGroupFive2=[fpShrub3,fpShrub4]
fiveFPlat2=FallPlat(597,143,200,51,PURPLE,fallGroupFive2)
lFive.append(fpShrub3)
lFive.append(fpShrub4)
lFive.append(fiveFPlat2)

fpShrub5=smallShrub(933,91)
fpShrub6=smallShrub(1041,91)
fallGroupFive3=[fpShrub5,fpShrub6]
fiveFPlat3=FallPlat(889,143,200,51,PURPLE,fallGroupFive3)
lFive.append(fpShrub5)
lFive.append(fpShrub6)
lFive.append(fiveFPlat3)

lFive.append(Platform(1097,114,103,58,WHITE))
lFive.append(lBorderLeft)
lFive.append(lBorderRight)

# End Level 6
lFive.append(endSign(1140,74))
levelFive=Level(lFive,50,625,"CaveBackground1.png")

# LEVEL 6
lSix=[]
lSix.append(Void(0,800,1115,15))
lSix.append(Platform(0,114,103,58,WHITE))##Start
lSix.append(Platform(0,0,1200,13,GRAY))
lSix.append(Platform(0,172,34,628,GRAY))
lSix.append(Platform(34,695,850,105,GRAY))

# Moving platform line 1
mpo6_1 = []
mpo6_1.append(smallShrub(151,202))
mpo6_1.append(smallShrub(308,202))
mpo6_1.append(ReverseSmallShrub(151,305))
mpo6_1.append(ReverseSmallShrub(308,305))
mp6_1  = MovePlat(151, 254, 200, 51, 34, 1166, oList=mpo6_1)

mpo6_2 = []
mpo6_2.append(Ladder(758, 256))
mp6_2  = MovePlat(745, 256, 200, 51, 34, 1166, oList=mpo6_2, aList=[mp6_1])

mp6_1.set_a([mp6_2])
lSix.append(mp6_1)
lSix.extend(mpo6_1)
lSix.append(mp6_2)
lSix.extend(mpo6_2)

lSix.append(MovePlat(281, 405, 200, 51, 34, 860))

# Spikes at bottom
lSix.append(BlackSpike(35,662))
lSix.append(BlackSpike(72,662))
lSix.append(BlackSpike(109,662))
lSix.append(BlackSpike(146,662))
lSix.append(BlackSpike(183,662))
lSix.append(BlackSpike(220,662))
lSix.append(BlackSpike(257,662))
lSix.append(BlackSpike(294,662))
lSix.append(BlackSpike(331,662))
lSix.append(BlackSpike(368,662))
lSix.append(BlackSpike(405,662))
lSix.append(BlackSpike(442,662))
lSix.append(BlackSpike(479,662))
lSix.append(BlackSpike(516,662))
lSix.append(BlackSpike(553,662))
lSix.append(BlackSpike(590,662))
lSix.append(BlackSpike(627,662))
lSix.append(BlackSpike(664,662))
lSix.append(BlackSpike(701,662))
lSix.append(BlackSpike(738,662))
lSix.append(BlackSpike(775,662))
lSix.append(BlackSpike(812,662))

# Spikes in sides
lSix.append(BlackLSpike(1132, 366))
lSix.append(BlackLSpike(1132, 406))
lSix.append(BlackLSpike(1132, 446))
lSix.append(BlackLSpike(1132, 486))
lSix.append(BlackLSpike(1132, 526))

lSix.append(BlackRSpike(884, 488))
lSix.append(BlackRSpike(884, 528))
lSix.append(BlackRSpike(884, 568))
lSix.append(BlackRSpike(884, 608))

lSix.append(BlackLSpike(1132, 596))
lSix.append(BlackLSpike(1132, 636))
lSix.append(BlackLSpike(1132, 676))
lSix.append(BlackLSpike(1132, 716))

lSix.append(Platform(860,405,24,290,GRAY))
lSix.append(Platform(1166,13,34,787,GRAY))
lSix.append(Platform(884,457,85,30,WHITE))
lSix.append(Platform(1081,566,85,30,WHITE))
lSix.append(Platform(884,665,85,30,WHITE))
lSix.append(Platform(1081,770,85,30,WHITE))
lSix.append(lBorderLeft)
lSix.append(lBorderRight)
# End Level 6
lSix.append(endSign(1086,730))
levelSix=Level(lSix,25,50,"CaveBackground1.png")

# LEVEL 7
lSeven=[]
lSeven.append(Void(0,800,1200,15))
lSeven.append(Void(884,-5,242,5))
lSeven.append(Ladder(1070,-1))
lSeven.append(Ladder(1070,97))
lSeven.append(Ladder(1070,194))
lSeven.append(Platform(926,295,200,51,WHITE))##Start
lSeven.append(Platform(0,0,890,105,GRAY))
lSeven.append(Platform(0,0,34,800,GRAY))
lSeven.append(Platform(1126,0,74,624,GRAY))
lSeven.append(Platform(1126,727,74,100,GRAY))

# Moving platform line 1
mp07_1 = []
mp07_1.append(smallShrub(95,363))
mp07_1.append(ReverseSmallShrub(245,466))
mp07_1.append(Ladder(145, 414))
mp7_1 = MovePlat(95, 415, 200, 51, 34, 1126, oList=mp07_1)

mpo7_2 = []
mpo7_2.append(smallShrub(641,363))
mpo7_2.append(ReverseSmallShrub(792,466))
mp7_2 = MovePlat(642, 415, 200, 51, 34, 1126, oList=mpo7_2, aList=[mp7_1])
mp7_1.set_a([mp7_2])

lSeven.append(mp7_1)
lSeven.extend(mp07_1)
lSeven.append(mp7_2)
lSeven.extend(mpo7_2)

# Moving platform line 2
mp07_3 = []
mp07_3.append(smallShrub(330,520))
mp07_3.append(ReverseSmallShrub(330,623))
mp7_3 = MovePlat(178, 573, 200, 51, 34, 1126, oList=mp07_3)

mpo7_4 = []
mpo7_4.append(smallShrub(624,520))
mpo7_4.append(ReverseSmallShrub(624,623))
mpo7_4.append(Ladder(673, 573))
mpo7_4.append(smallShrub(786,520))
mp7_4 = MovePlat(634, 573, 200, 51, 34, 1126, oList=mpo7_4, aList=[mp7_3])
mp7_3.set_a([mp7_4])

lSeven.append(mp7_3)
lSeven.extend(mp07_3)
lSeven.append(mp7_4)
lSeven.extend(mpo7_4)

# Moving platform line 3
mp07_5 = []
mp07_5.append(smallShrub(320,675))
mp07_5.append(smallShrub(472,675))
mp7_5 = MovePlat(320, 727, 200, 51, 34, 1126, oList=mp07_5)

mpo7_6 = []
mpo7_6.append(smallShrub(786,675))
mp7_6 =  MovePlat(792, 727, 200, 51, 34, 1126, oList=mpo7_6, aList=[mp7_5])
mp7_5.set_a([mp7_6])

lSeven.append(mp7_5)
lSeven.extend(mp07_5)
lSeven.append(mp7_6)
lSeven.extend(mpo7_6)

# End Level 7
lSeven.append(lBorderLeft)
lSeven.append(lBorderRight)

lSeven.append(endSign(1160,663+24))
levelSeven=Level(lSeven,1040,225,"CaveBackground1.png")

# LEVEL 8
lEight=[]
lEight.append(Void(0,800,1200,15))
lEight.append(Platform(0,0,74,560,GRAY))
lEight.append(Platform(0,663,74,137,GRAY))
lEight.append(Platform(74,663,187,137,WHITE))##Start
lEight.append(SmallPurpleShrub(143,611))
lEight.append(RedSpike(261, 767))
lEight.append(RedSpike(301, 767))
lEight.append(RedSpike(341, 767))
lEight.append(RedSpike(381, 767))
lEight.append(Platform(418,663,187,137,WHITE))
lEight.append(SmallPurpleShrub(418,611))
lEight.append(RedSpike(605, 767))
lEight.append(RedSpike(647, 767))
lEight.append(RedSpike(689, 767))
lEight.append(RedSpike(733, 767))
lEight.append(Platform(774,663,187,137,WHITE))
lEight.append(TallPurpleShrub(854,480))
lEight.append(RedSpike(962, 767))
lEight.append(RedSpike(1002, 767))
lEight.append(RedSpike(1042, 767))
lEight.append(RedSpike(1082, 767))
lEight.append(RedSpike(1122, 767))
lEight.append(RedSpike(1162, 767))
lEight.append(RedSpike(1202, 767))
lEight.append(Platform(1020,604,180,30,WHITE))
lEight.append(Platform(825,375,155,30,WHITE))
lEight.append(Ladder(947,375))

lEight.append(FallPlat(672,375,75,30))
lEight.append(FallPlat(570,405,50,30))
lEight.append(FallPlat(475,375,50,30))
fpShrub8_1 = SmallPurpleShrub(378,353)
lEight.append(FallPlat(376,405,50,30, oList=[fpShrub8_1]))
lEight.append(fpShrub8_1)
lEight.append(FallPlat(253,375,75,30))

lEight.append(FallPlat(253,186,75,30))
lEight.append(FallPlat(376,211,50,30))
lEight.append(FallPlat(475,197,50,30))
fpShrub8_2 = SmallPurpleShrub(570,164)
lEight.append(FallPlat(570,216,50,30, oList=[fpShrub8_2]))
lEight.append(fpShrub8_2)
lEight.append(FallPlat(672,186,75,30))


lEight.append(Platform(74,175,155,30,WHITE))
lEight.append(Ladder(175,175))
lEight.append(Ladder(175,244))
lEight.append(Platform(74,345,155,30,WHITE))
lEight.append(Ladder(947,-10))
lEight.append(Ladder(947,60))
lEight.append(Platform(825,160,155,30,WHITE))

# End Level 8
lEight.append(lBorderLeft)
lEight.append(lBorderRight)

lEight.append(endSign(890,120))
levelEight=Level(lEight,70,590,"mysticalBackground.png")

# LEVEL 9
lNine=[]
lNine.append(Void(0,800,1200,15))
lNine.append(Platform(858,759,155,30,WHITE))##Start
lNine.append(Ladder(931,759))
lNine.append(Platform(661,759,155,30,WHITE))
lNine.append(SmallPurpleShrub(686, 707))
lNine.append(RedSpike(776, 726))
lNine.append(Platform(414,759,155,30,WHITE))
lNine.append(RedSpike(491, 726))
lNine.append(Platform(212,731,155,30,WHITE))
lNine.append(TallPurpleShrub(319, 548))
lNine.append(Platform(220,436,158,30,WHITE))
lNine.append(Ladder(220,436))
lNine.append(Ladder(220,534))
lNine.append(Ladder(220,631))
lNine.append(Platform(378,375,37,91,WHITE))

lNine.append(Ladder(325,239))
lNine.append(Ladder(325,336))

lNine.append(RedSpike(378, 342))
lNine.append(FallPlat(415,375,129,26))
mpLadder8_1 = Ladder(731,250)
lNine.append(MovePlatDiag(731, 249, 129, 26, 1, 0.98, 600, 950, oList=[mpLadder8_1]))
lNine.append(mpLadder8_1)
mpLadder8_1 = Ladder(593,128)
lNine.append(MovePlat(497, 128, 129, 26, 462, 737, oList=[mpLadder8_1]))
lNine.append(mpLadder8_1)
lNine.append(Platform(295,153,129,12,WHITE))#Moved this platform up from 128 Y
lNine.append(Platform(200,117,24,17,WHITE))
lNine.append(Platform(139,100,24,17,WHITE))
lNine.append(Platform(0,100,105,17,WHITE))
lNine.append(Ladder(22,0))
lNine.append(Ladder(22,0))

# End Level 9
lNine.append(lBorderLeft)
lNine.append(lBorderRight)

lNine.append(endSign(69,60))
levelNine=Level(lNine,872,645,"mysticalBackground.png")

# LEVEL 10
lTen=[]
lTen.append(Void(0,800,1200,15))
lTen.append(Platform(0,700,174,33,WHITE))##Start
lTen.append(Ladder(22,700))

fpShrub10_1 = SmallPurpleShrub(249,632)
lTen.append(FallPlat(249,683,174,33, oList=[fpShrub10_1]))
lTen.append(fpShrub10_1)

lTen.append(Platform(525,709,174,33,WHITE))
lTen.append(RedSpike(606, 676))
lTen.append(Platform(462,563,174,33,WHITE))
lTen.append(Ladder(462,563))
lTen.append(Ladder(606,561))

mpShrub10_2 = SmallPinkShrub(715,624)
lTen.append(MovePlatDiag(715,676,127,33, 1,0.7,715, 1073, oList=[mpShrub10_2]))
lTen.append(mpShrub10_2)

lTen.append(Platform(660,388,11,120,WHITE))##made height shorter as to not interfere with ladder and moved right slightly
lTen.append(Platform(408,343,174,33,WHITE))

fpLadder10_1 = Ladder(864,276)
lTen.append(FallPlat(723,276,174,33, oList=[fpLadder10_1]))
lTen.append(fpLadder10_1)

lTen.append(MovePlatVert(563,138,37,123, 40, 309))##First vertical moving platform, bounds have been changed from figma to help the player

fpSpike10_1 = RedSpike(241,266)
lTen.append(FallPlat(196,299,126,34, oList=[fpSpike10_1]))
lTen.append(fpSpike10_1)

lTen.append(Platform(0,147,174,33,WHITE))
lTen.append(Ladder(141, 147))

# End Level 10
lTen.append(lBorderLeft)
lTen.append(lBorderRight)

lTen.append(endSign(40, 107))
levelTen=Level(lTen,60,630,"mysticalBackground.png")

# LEVEL 11
lEleven = []
lEleven.append(Water(0,800,1200,1,BLUE))
lEleven.append(Platform(1026,147,174,33,WHITE))
lEleven.append(Platform(752,243,174,33,WHITE))
lEleven.append(Platform(482,324,174,33,WHITE))
lEleven.append(Platform(224,243,174,33,WHITE))
lEleven.append(Platform(0,456,292,33,WHITE))
lEleven.append(Platform(0,631,174,33,WHITE))

# falling platform object
lvl11FallSpike = BlueSpike(429,615)
lvl11FallShrub = SmallRedShrub(292,596)
lvl11FallPlat = FallPlat(292,648,174,33,PURPLE,[lvl11FallSpike,lvl11FallShrub])
lEleven.append(lvl11FallSpike)
lEleven.append(lvl11FallShrub)
lEleven.append(lvl11FallPlat)

lEleven.append(BlueSpike(889,210))
lEleven.append(BlueSpike(752,210))
lEleven.append(BlueSpike(619,291))
lEleven.append(BlueSpike(482,291))
lEleven.append(BlueSpike(255,423))
lEleven.append(BlueSpike(218,423))
lEleven.append(BlueSpike(0,423))
lEleven.append(SmallRedShrub(545,272))
lEleven.append(SmallRedShrub(104,404))
lEleven.append(Ladder(365,243))
lEleven.append(Ladder(365,285))

lEleven.append(lBorderLeft)
lEleven.append(lBorderRight)
lEleven.append(endSign(10,591))

levelEleven=Level(lEleven,1125,80,"lvl-11-12-background.png")

# LEVEL 12
lTwelve = []
lTwelve.append(Water(0,800,1200,1,BLUE))
lTwelve.append(Platform(1026,631,174,33,WHITE))
lTwelve.append(Platform(657,604,304,33,WHITE))
lTwelve.append(Platform(309,395,174,33,WHITE))
lTwelve.append(Platform(9,662,230,33, WHITE))
lTwelve.append(Platform(14,465,206,33,WHITE))
lTwelve.append(Platform(195,246,25,219,WHITE))
lTwelve.append(Platform(132,416,63,19,WHITE))
lTwelve.append(Platform(0,173,174,33,WHITE))

# falling platform object
lvl12FallSpike = BlueSpike(572,508)
lvl12FallTallShrub = TallRedShrub(609,358)
lvl12FallPlat = FallPlat(483,541,174,33,PURPLE,[lvl12FallSpike,lvl12FallTallShrub])
lTwelve.append(lvl12FallSpike)
lTwelve.append(lvl12FallTallShrub)
lTwelve.append(lvl12FallPlat)

lTwelve.append(BlueSpike(924,571))
lTwelve.append(BlueSpike(657,571))
lTwelve.append(BlueSpike(139,629))
lTwelve.append(BlueSpike(87,432))
lTwelve.append(SmallRedShrub(132,364))
lTwelve.append(Ladder(450,395))
lTwelve.append(Ladder(309,395))
lTwelve.append(Ladder(309,451))
lTwelve.append(Ladder(14,465))
lTwelve.append(Ladder(14,562))
lTwelve.append(Ladder(141,173))
lTwelve.append(Ladder(86,206))
lTwelve.append(Ladder(86,262))

lTwelve.append(lBorderLeft)
lTwelve.append(lBorderRight)
lTwelve.append(endSign(10,133))

levelTwelve=Level(lTwelve,1125,563,"lvl-11-12-background.png")

# LEVEL 13
lthirteen = []
lthirteen.append(Water(0,800,1200,1,BLUE))
lthirteen.append(Platform(1061,173,139,33,WHITE))
lthirteen.append(Platform(532,559,32,32,WHITE))
lthirteen.append(Platform(394,579,67,32,WHITE))
lthirteen.append(Platform(201,611,145,32,WHITE))
lthirteen.append(Platform(46,765,111,32,WHITE))
lthirteen.append(Platform(52,603,66,33,WHITE))
lthirteen.append(Platform(52,472,85,33,WHITE))
lthirteen.append(Platform(0,241,138,33,WHITE))

# Angled platform
lthirteen.append(AngleSpike(913,351))

lthirteen.append(AnglePlat(849,330))

# Moving platform
l13mpShrub = SmallPurpleShrub(660,402) # Moving platform shrub
lthirteen.append(l13mpShrub)
l13mp = MovePlat(661,454,99,26,610,814,[l13mpShrub], [])
lthirteen.append(l13mp)

lthirteen.append(GreenSpike(309,578))
lthirteen.append(GreenSpike(87,732))
lthirteen.append(GreenSpike(51,439))
lthirteen.append(SmallPurpleShrub(377,527))
lthirteen.append(SmallPurpleShrub(100,189))
lthirteen.append(Ladder(49,603))
lthirteen.append(Ladder(104,472))
lthirteen.append(Ladder(57,324))
lthirteen.append(Ladder(57,241))

lthirteen.append(lBorderLeft)
lthirteen.append(lBorderRight)
lthirteen.append(endSign(2,201))

levelThirteen=Level(lthirteen,1130,93,"lvl-13-16-background.png")

# LEVEL 14
lFourteen = []
lFourteen.append(Water(0,800,1200,1,BLUE))
lFourteen.append(Platform(1061,241,139,33,WHITE))
lFourteen.append(Platform(1025,106,67,33,WHITE))
lFourteen.append(Platform(549,425,145,33,WHITE))
lFourteen.append(Platform(0,426,134,33,WHITE))
lFourteen.append(Platform(0,264,101,33,WHITE))
lFourteen.append(Platform(0,128,138,33,WHITE))

lFourteen.append(MovePlatVert(727,347,22,59,228,458,[],[]))

lFourteen.append(FallPlat(945,161,56,33,BEIGE,[]))
lFourteen.append(FallPlat(862,201,56,33,BEIGE,[]))
lFourteen.append(FallPlat(786,334,56,33,BEIGE,[]))
lFourteen.append(FallPlat(353,493,185,33,BEIGE,[]))
lFourteen.append(FallPlat(149,585,185,33,BEIGE,[]))
lFourteen.append(FallPlat(207,128,56,33,BEIGE,[]))

l14mpSpike = GreenSpike(355,96)
lFourteen.append(l14mpSpike)
l14mpLadder = Ladder(305,129)
lFourteen.append(l14mpLadder)
l14mp1 = MovePlat(305,129,112,22,305,535,[l14mpSpike, l14mpLadder], [])
lFourteen.append(l14mp1)
lFourteen.append(l14mpSpike)
lFourteen.append(l14mpLadder)

l14mp2 = MovePlat(245,263,112,22,127,357,[],[])
lFourteen.append(l14mp2)

lFourteen.append(Ladder(1060,106))
lFourteen.append(Ladder(101,426))
lFourteen.append(Ladder(35,264))

lFourteen.append(GreenSpike(584,393))
lFourteen.append(GreenSpike(549,393))

lFourteen.append(TallPurpleShrub(608,243))
lFourteen.append(SmallPurpleShrub(31,374))
lFourteen.append(SmallPurpleShrub(68,76))

lFourteen.append(lBorderLeft)
lFourteen.append(lBorderRight)
lFourteen.append(endSign(10,88))

levelFourteen=Level(lFourteen,1125,174,"lvl-13-16-background.png")

# LEVEL 15
lFifteen = []
lFifteen.append(Water(0,800,1200,1,BLUE))
lFifteen.append(Platform(1124,128,76,33,WHITE))
lFifteen.append(Platform(662,142,82,19,WHITE))
lFifteen.append(Platform(634,250,142,33,WHITE))
lFifteen.append(Platform(485,360,216,15,WHITE))
lFifteen.append(Platform(452,360,33,216,WHITE))
lFifteen.append(Platform(452,576,232,33,WHITE))
lFifteen.append(Platform(0,767,44,33,WHITE))
lFifteen.append(FallPlat(847,267,302,33,BEIGE,[]))
lFifteen.append(FallPlat(885,516,74,33,BEIGE,[]))
lFifteen.append(FallPlat(993,622,74,33,BEIGE,[]))
lFifteen.append(FallPlat(885,684,74,33,BEIGE,[]))
lFifteen.append(FallPlat(321,142,302,19,BEIGE,[]))

lFifteen.append(MovePlatVert(302,701,22,139,610,840,[],[]))

l15small1 = SmallPurpleShrub(935,373)
lFifteen.append(l15small1)
l15small2 = SmallPurpleShrub(1051,373)
lFifteen.append(l15small2)
l15mp1 = MovePlat(948,425,139,22,857,1087,[l15small1,l15small2],[])
lFifteen.append(l15mp1)

l15small3 = SmallPurpleShrub(753,643)
lFifteen.append(l15small3)
l15mp2 = MovePlat(708,695,139,22,617,847,[l15small3],[])
lFifteen.append(l15mp2)

l15small4 = SmallPurpleShrub(448,701)
lFifteen.append(l15small4)
l15spike1 = GreenSpike(395,720)
lFifteen.append(l15spike1)
l15mp3 = MovePlat(342,753,139,22,342,572,[l15small4,l15spike1],[])
lFifteen.append(l15mp3)

l15small5 = SmallPurpleShrub(130,701)
lFifteen.append(l15small5)
l15spike2 = GreenSpike(195,720)
lFifteen.append(l15spike2)
l15mp4 = MovePlat(145,753,139,22,54,284,[l15small5,l15spike2],[])
lFifteen.append(l15mp4)

lFifteen.append(Ladder(1124,128))
lFifteen.append(Ladder(711,142))
lFifteen.append(Ladder(634,250))
lFifteen.append(Ladder(485,360))
lFifteen.append(Ladder(485,430))
lFifteen.append(Ladder(630,576))
lFifteen.append(Ladder(6,767))
lFifteen.append(TallPurpleShrub(660,-41))
lFifteen.append(TallPurpleShrub(524,393))
lFifteen.append(SmallPurpleShrub(660,198))
lFifteen.append(GreenSpike(576,543))
lFifteen.append(GreenSpike(485,543))

lFifteen.append(lBorderLeft)
lFifteen.append(lBorderRight)
lFifteen.append(endSign(3,727))

levelFifteen=Level(lFifteen,1135,58,"lvl-13-16-background.png")


# LEVEL SIXTEEN
lSixteen = []
lSixteen.append(Water(0,800,1200,1,BLUE))
lSixteen.append(Platform(0,0,44,33,WHITE))
lSixteen.append(FallPlat(0,154,170,33,BEIGE))
lSixteen.append(FallPlat(711,302,44,33,BEIGE))
lSixteen.append(FallPlat(808,302,44,33,BEIGE))
lSixteen.append(FallPlat(906,302,44,33,BEIGE))
lSixteen.append(Platform(974,326,133,33,WHITE))
lSixteen.append(Platform(974,358,14,280,WHITE))
lSixteen.append(Platform(1093,358,14,280,WHITE))
lSixteen.append(FallPlat(1024,743,33,22,BEIGE))
lSixteen.append(FallPlat(765,424,33,33,BEIGE))
lSixteen.append(FallPlat(863,424,33,33,BEIGE))
lSixteen.append(Platform(633,767,33,33,WHITE))
lSixteen.append(Platform(159,560,507,33,WHITE))
lSixteen.append(Platform(557,390,58,33,WHITE))
lSixteen.append(Platform(446,333,116,33,WHITE))
lSixteen.append(FallPlat(354,386,44,33,BEIGE))
lSixteen.append(FallPlat(256,386,44,33,BEIGE))
lSixteen.append(FallPlat(159,386,44,33,BEIGE))
lSixteen.append(Platform(0,741,40,33,WHITE))
lSixteen.append(Platform(80,300,15,270,WHITE))
lSixteen.append(Ladder(529,332))
lSixteen.append(Ladder(582,390))
lSixteen.append(Ladder(582,460))
lSixteen.append(Ladder(633,560))
lSixteen.append(Ladder(633,630))
lSixteen.append(Ladder(1024,326))
lSixteen.append(Ladder(1024,396))
lSixteen.append(Ladder(1024,467))
lSixteen.append(Ladder(1024,537))
lSixteen.append(Ladder(6,0))
lSixteen.append(GreenSpike(633,734))
lSixteen.append(GreenSpike(542,527))
lSixteen.append(GreenSpike(402,527))
lSixteen.append(GreenSpike(368,527))
lSixteen.append(GreenSpike(333,527))
lSixteen.append(GreenSpike(299,527))
lSixteen.append(GreenSpike(262,527))
lSixteen.append(GreenSpike(228,527))
lSixteen.append(GreenSpike(192,527))
lSixteen.append(GreenSpike(159,527))
lSixteen.append(GreenRSpike(988,358))
lSixteen.append(GreenRSpike(988,392))
lSixteen.append(GreenRSpike(988,427))
lSixteen.append(GreenRSpike(988,461))
lSixteen.append(GreenRSpike(988,498))
lSixteen.append(GreenRSpike(988,532))
lSixteen.append(GreenRSpike(988,567))
lSixteen.append(GreenRSpike(988,601))
lSixteen.append(GreenLSpike(1060,358))
lSixteen.append(GreenLSpike(1060,392))
lSixteen.append(GreenLSpike(1060,427))
lSixteen.append(GreenLSpike(1060,461))
lSixteen.append(GreenLSpike(1060,498))
lSixteen.append(GreenLSpike(1060,532))
lSixteen.append(GreenLSpike(1060,567))
lSixteen.append(GreenLSpike(1060,601))
lSixteen.append(TallPinkShrub(446,375))

# mp 1
l16mp1shrub = SmallPinkShrub(350,80)
l16mp1spike = GreenSpike(274,99)
lSixteen.append(l16mp1shrub)
lSixteen.append(l16mp1spike)
l16mp1 = MovePlat(218,132,162,22,218,458,[l16mp1spike,l16mp1shrub],[])
lSixteen.append(l16mp1)

l16mp2shrub1 = SmallPinkShrub(406,188)
l16mp2shrub2 = SmallPinkShrub(584,188)
lSixteen.append(l16mp2shrub1)
lSixteen.append(l16mp2shrub2)
l16mp2 = MovePlat(422,240,195,22,407,695,[l16mp2shrub1,l16mp2shrub2],[])
lSixteen.append(l16mp2)

l16mp3shrub1 = TallPinkShrub(807, 560)
lSixteen.append(l16mp3shrub1)
l16mp3 = MovePlat(733,743,195,22,686,974,[l16mp3shrub1],[])
lSixteen.append(l16mp3)

l16mp4shrub1 = SmallPinkShrub(274,680)
l16mp4spike1 = GreenSpike(113,699)
lSixteen.append(l16mp4shrub1)
lSixteen.append(l16mp4spike1)
l16mp4 = MovePlat(113,730,195,22,66,354,[l16mp4shrub1,l16mp4spike1],[])
lSixteen.append(l16mp4)

lSixteen.append(lBorderRight)
lSixteen.append(lBorderLeft)
lSixteen.append(endSign(0,700))

levelSixteen=Level(lSixteen,0,75,"lvl-13-16-background.png")

# LEVEL 17
lSeventeen = []
lSeventeen.append(Water(0,800,1200,1,BLUE))
lSeventeen.append(Platform(489,112,711,33,WHITE))
lSeventeen.append(Platform(474,112,15,81,WHITE))
lSeventeen.append(Platform(395,181,94,15,WHITE))
lSeventeen.append(Platform(152,193,249,15,WHITE))
lSeventeen.append(Platform(0,182,170,15,WHITE))
lSeventeen.append(Platform(0,327,567,33,WHITE))
lSeventeen.append(Platform(0,350,15,172,WHITE))
lSeventeen.append(Platform(0,489,68,33,WHITE))
lSeventeen.append(Platform(0,617,68,33,WHITE))
lSeventeen.append(Platform(258,427,52,15,WHITE))
lSeventeen.append(Platform(766,382,434,16,WHITE))
lSeventeen.append(Platform(766,484,434,16,WHITE))
lSeventeen.append(Platform(1089,616,68,33,WHITE))
lSeventeen.append(Platform(1114,741,107,33,WHITE))
lSeventeen.append(Platform(0,256,52,16,WHITE))

lSeventeen.append(Ladder(36,489))
lSeventeen.append(Ladder(0,617))
lSeventeen.append(Ladder(1135,382))
lSeventeen.append(Ladder(1119,616))

l17mp1 = MovePlat(882,644,42,22,835,1027)
lSeventeen.append(l17mp1)
l17mp2 = MovePlat(443,730,42,22,363,522)
lSeventeen.append(l17mp2)
l17mp3 = MovePlat(222,490,25,25,93,258)
lSeventeen.append(l17mp3)
l17mp4 = MovePlat(719,492,25,25,617,750)
lSeventeen.append(l17mp4)
l17mp5 = MovePlat(803,333,10,10,767,827)
lSeventeen.append(l17mp5)
l17mp6 = MovePlat(527,261,24,14,453,569)
lSeventeen.append(l17mp6)
l17mp7 = MovePlat(330,275,15,15,316,432)
lSeventeen.append(l17mp7)
l17mp8 = MovePlat(188,269,10,10,174,290)
lSeventeen.append(l17mp8)

lSeventeen.append(FallPlat(747,694,33,25,BEIGE))
lSeventeen.append(FallPlat(653,711,33,25,BEIGE))
lSeventeen.append(FallPlat(559,711,33,25,BEIGE))
lSeventeen.append(FallPlat(311,719,33,25,BEIGE))
lSeventeen.append(FallPlat(137,732,106,25,BEIGE))
lSeventeen.append(FallPlat(0,739,106,25,BEIGE))
lSeventeen.append(FallPlat(356,460,25,25,BEIGE))
lSeventeen.append(FallPlat(411,473,25,25,BEIGE))
lSeventeen.append(FallPlat(473,480,25,25,BEIGE))
lSeventeen.append(FallPlat(531,490,25,25,BEIGE))
lSeventeen.append(FallPlat(1105,340,20,6,BEIGE))
lSeventeen.append(FallPlat(1070,320,20,6,BEIGE))
lSeventeen.append(FallPlat(1025,300,25,16,BEIGE))
lSeventeen.append(FallPlat(840,300,25,16,BEIGE))
lSeventeen.append(FallPlat(118,277,25,10,BEIGE))
lSeventeen.append(FallPlat(72,270,25,10,BEIGE))

lSeventeen.append(MovePlatVert(268,680,22,55,593,747))
lSeventeen.append(MovePlatVert(684,277,55,20,230,382))
lSeventeen.append(MovePlatVert(600,207,55,20,230,312))


lSeventeen.append(MovePlatDiag(900,261,10,10,1,2,870,930))
lSeventeen.append(MovePlatDiag(980,261,10,10,-1,2,940,1000))

lSeventeen.append(GreenSpike(0,294))
lSeventeen.append(GreenSpike(37,294))
lSeventeen.append(GreenSpike(74,294))
lSeventeen.append(GreenSpike(111,294))
lSeventeen.append(GreenSpike(148,294))
lSeventeen.append(GreenSpike(185,294))
lSeventeen.append(GreenSpike(222,294))
lSeventeen.append(GreenSpike(259,294))
lSeventeen.append(GreenSpike(296,294))
lSeventeen.append(GreenSpike(333,294))
lSeventeen.append(GreenSpike(370,294))
lSeventeen.append(GreenSpike(407,294))
lSeventeen.append(GreenSpike(444,294))
lSeventeen.append(GreenSpike(481,294))
lSeventeen.append(GreenSpike(518,294))

lSeventeen.append(GreenSpike(766,349))
lSeventeen.append(GreenSpike(800,349))
lSeventeen.append(GreenSpike(835,349))
lSeventeen.append(GreenSpike(869,349))
lSeventeen.append(GreenSpike(906,349))
lSeventeen.append(GreenSpike(940,349))
lSeventeen.append(GreenSpike(975,349))
lSeventeen.append(GreenSpike(1009,349))
lSeventeen.append(GreenSpike(1045,349))
lSeventeen.append(GreenSpike(1080,349))

lSeventeen.append(SmallPurpleShrub(1056,432))
lSeventeen.append(SmallPurpleShrub(1008,432))
lSeventeen.append(SmallPurpleShrub(960,432))
lSeventeen.append(SmallPurpleShrub(912,432))
lSeventeen.append(SmallPurpleShrub(864,432))
lSeventeen.append(SmallPurpleShrub(816,432))


lSeventeen.append(endSign(5,216))
lSeventeen.append(lBorderRight)
lSeventeen.append(lBorderLeft)

levelSeventeen=Level(lSeventeen,1120,650,"lvl-13-16-background.png")

# LEVEL 18
lEighteen = []
lEighteen.append(Water(0,800,1200,1,BLUE))
lEighteen.append(Platform(1129,259,74,16,WHITE))
lEighteen.append(Platform(904,160,300,15,WHITE))
lEighteen.append(Platform(887,327,313,33,WHITE))
lEighteen.append(Platform(716,522,47,15,WHITE))
lEighteen.append(Platform(531,627,184,15,WHITE))
lEighteen.append(Platform(427,736,48,20,WHITE))
lEighteen.append(Platform(0,766,118,34,WHITE))

lEighteen.append(Ladder(887,327))
lEighteen.append(Ladder(716,522))
lEighteen.append(Ladder(551,626))

lEighteen.append(FallPlat(865,452,76,25,BEIGE))
lEighteen.append(FallPlat(782,507,12,12,BEIGE))
lEighteen.append(FallPlat(368,732,12,12,BEIGE))
lEighteen.append(FallPlat(317,715,12,12,BEIGE))
lEighteen.append(FallPlat(279,746,12,12,BEIGE))
lEighteen.append(FallPlat(228,729,12,12,BEIGE))

lEighteen.append(MovePlat(1068,265,20,14,1060,1123))
lEighteen.append(MovePlat(1025,265,20,14,989,1052))
lEighteen.append(MovePlat(926,265,20,14,918,981))

lEighteen.append(MovePlatVert(843,215,19,5,186,359))
lEighteen.append(MovePlatVert(807,495,19,5,349,522))
lEighteen.append(MovePlatVert(496,714,19,5,670,766))
lEighteen.append(MovePlatVert(401,742,14,63,627,757))
lEighteen.append(MovePlatVert(843,215,19,5,186,359))
lEighteen.append(MovePlatVert(182,707,19,5,591,764))

lEighteen.append(smallShrub(572,575))
lEighteen.append(smallShrub(514,575))
lEighteen.append(smallShrub(427,684))

lEighteen.append(GreenSpike(954,294))
lEighteen.append(GreenSpike(989,294))
lEighteen.append(GreenSpike(1023,294))
lEighteen.append(GreenSpike(1060,294))
lEighteen.append(GreenSpike(1094,294))
lEighteen.append(GreenSpike(1129,294))
lEighteen.append(GreenSpike(1163,294))

lEighteen.append(endSign(20,726))
lEighteen.append(lBorderRight)
lEighteen.append(lBorderLeft)
levelEighteen=Level(lEighteen,1130,185,"lvl-13-16-background.png")

# LEVEL 19
lNineteen = []

lNineteen.append(Platform(0,75,133,40,WHITE))
lNineteen.append(Platform(0,383,717,17,WHITE))
lNineteen.append(Platform(717,246,37,221,WHITE))
lNineteen.append(Platform(91,591,1109,15,WHITE))
lNineteen.append(Platform(1082,757,126,43,WHITE))

lNineteen.append(Ladder(50,75))

lNineteen.append(GreenRSpike(0,104))
lNineteen.append(GreenRSpike(0,139))
lNineteen.append(GreenRSpike(0,173))
lNineteen.append(GreenRSpike(0,210))
lNineteen.append(GreenRSpike(0,244))
lNineteen.append(GreenRSpike(0,279))

lNineteen.append(FallPlat(0,325,85,15,BEIGE))
lNineteen.append(FallPlat(95,299,25,17,BEIGE))
lNineteen.append(FallPlat(121,269,25,17,BEIGE))
lNineteen.append(smallShrub(115,217))

lNineteen.append(FallPlat(156,316,25,17,BEIGE))
lNineteen.append(FallPlat(191,289,25,17,BEIGE))
lNineteen.append(FallPlat(226,262,25,17,BEIGE))
lNineteen.append(FallPlat(262,230,25,17,BEIGE))
lNineteen.append(smallShrub(257,178))

lNineteen.append(FallPlat(295,319,25,17,BEIGE))
lNineteen.append(FallPlat(331,295,25,17,BEIGE))
lNineteen.append(FallPlat(366,262,25,17,BEIGE))
lNineteen.append(FallPlat(402,226,25,17,BEIGE))
lNineteen.append(smallShrub(397,174))

lNineteen.append(FallPlat(437,316,25,17,BEIGE))
lNineteen.append(FallPlat(472,289,25,17,BEIGE))
lNineteen.append(FallPlat(507,260,25,17,BEIGE))
lNineteen.append(smallShrub(502,208))

lNineteen.append(FallPlat(542,324,25,17,BEIGE))
lNineteen.append(FallPlat(577,299,25,17,BEIGE))
lNineteen.append(FallPlat(613,272,25,17,BEIGE))
lNineteen.append(FallPlat(648,245,25,17,BEIGE))
lNineteen.append(FallPlat(683,218,25,17,BEIGE))
lNineteen.append(smallShrub(678,166))

lNineteen.append(GreenSpike(0,350))
lNineteen.append(GreenSpike(37,350))
lNineteen.append(GreenSpike(75,350))
lNineteen.append(GreenSpike(110,350))
lNineteen.append(GreenSpike(145,350))
lNineteen.append(GreenSpike(180,350))
lNineteen.append(GreenSpike(214,350))
lNineteen.append(GreenSpike(251,350))
lNineteen.append(GreenSpike(285,350))
lNineteen.append(GreenSpike(320,350))
lNineteen.append(GreenSpike(354,350))
lNineteen.append(GreenSpike(392,350))
lNineteen.append(GreenSpike(429,350))
lNineteen.append(GreenSpike(466,350))
lNineteen.append(GreenSpike(503,350))
lNineteen.append(GreenSpike(539,350))
lNineteen.append(GreenSpike(576,350))
lNineteen.append(GreenSpike(610,350))
lNineteen.append(GreenSpike(645,350))
lNineteen.append(GreenSpike(681,350))
lNineteen.append(GreenSpike(717,213))

lNineteen.append(FallPlat(641,534,25,17,BEIGE))
lNineteen.append(FallPlat(605,520,25,17,BEIGE))
lNineteen.append(FallPlat(527,503,25,17,BEIGE))
lNineteen.append(FallPlat(397,529,25,17,BEIGE))
lNineteen.append(FallPlat(308,520,25,17,BEIGE))
lNineteen.append(FallPlat(224,503,25,17,BEIGE))
lNineteen.append(FallPlat(134,471,25,17,BEIGE))

lNineteen.append(GreenSpike(91,558))
lNineteen.append(GreenSpike(126,558))
lNineteen.append(GreenSpike(161,558))
lNineteen.append(GreenSpike(195,558))
lNineteen.append(GreenSpike(232,558))
lNineteen.append(GreenSpike(266,558))
lNineteen.append(GreenSpike(301,558))
lNineteen.append(GreenSpike(335,558))
lNineteen.append(GreenSpike(372,558))
lNineteen.append(GreenSpike(407,558))
lNineteen.append(GreenSpike(442,558))
lNineteen.append(GreenSpike(477,558))
lNineteen.append(GreenSpike(511,558))
lNineteen.append(GreenSpike(548,558))
lNineteen.append(GreenSpike(582,558))
lNineteen.append(GreenSpike(617,558))
lNineteen.append(GreenSpike(651,558))

lNineteen.append(GreenRSpike(0,400))
lNineteen.append(GreenRSpike(0,435))
lNineteen.append(GreenRSpike(0,470))
lNineteen.append(GreenRSpike(0,505))
lNineteen.append(GreenRSpike(0,540))
lNineteen.append(GreenRSpike(0,575))
lNineteen.append(GreenRSpike(0,610))
lNineteen.append(GreenRSpike(0,645))

lNineteen.append(FallPlat(21,757,70,9,BEIGE))
lNineteen.append(FallPlat(96,757,70,9,BEIGE))
lNineteen.append(FallPlat(171,757,70,9,BEIGE))
lNineteen.append(FallPlat(246,757,70,9,BEIGE))
lNineteen.append(FallPlat(321,757,70,9,BEIGE))
lNineteen.append(FallPlat(396,757,70,9,BEIGE))
lNineteen.append(FallPlat(471,757,70,9,BEIGE))
lNineteen.append(FallPlat(553,757,70,9,BEIGE))
lNineteen.append(FallPlat(628,757,70,9,BEIGE))
lNineteen.append(FallPlat(703,757,70,9,BEIGE))
lNineteen.append(FallPlat(778,757,70,9,BEIGE))
lNineteen.append(FallPlat(853,757,70,9,BEIGE))
lNineteen.append(FallPlat(928,757,70,9,BEIGE))
lNineteen.append(FallPlat(1003,757,70,9,BEIGE))

lNineteen.append(GreenSpike(19,767))
lNineteen.append(GreenSpike(56,767))
lNineteen.append(GreenSpike(93,767))
lNineteen.append(GreenSpike(129,767))
lNineteen.append(GreenSpike(164,767))
lNineteen.append(GreenSpike(199,767))
lNineteen.append(GreenSpike(234,767))
lNineteen.append(GreenSpike(269,767))
lNineteen.append(GreenSpike(304,767))
lNineteen.append(GreenSpike(339,767))
lNineteen.append(GreenSpike(373,767))
lNineteen.append(GreenSpike(410,767))
lNineteen.append(GreenSpike(444,767))
lNineteen.append(GreenSpike(479,767))
lNineteen.append(GreenSpike(513,767))
lNineteen.append(GreenSpike(551,767))
lNineteen.append(GreenSpike(588,767))
lNineteen.append(GreenSpike(625,767))
lNineteen.append(GreenSpike(661,767))
lNineteen.append(GreenSpike(696,767))
lNineteen.append(GreenSpike(731,767))
lNineteen.append(GreenSpike(766,767))
lNineteen.append(GreenSpike(801,767))
lNineteen.append(GreenSpike(836,767))
lNineteen.append(GreenSpike(871,767))
lNineteen.append(GreenSpike(905,767))
lNineteen.append(GreenSpike(942,767))
lNineteen.append(GreenSpike(976,767))
lNineteen.append(GreenSpike(1011,767))
lNineteen.append(GreenSpike(1045,767))

lNineteen.append(smallShrub(836,539))
lNineteen.append(smallShrub(983,539))
lNineteen.append(smallShrub(1084,539))

mp1plat1 = Platform(764,378,73,23,ORANGE)
lNineteen.append(mp1plat1)
mp1sp1 = GreenSpike(763,346)
lNineteen.append(mp1sp1)
mp1sp2 = GreenSpike(799,346)
lNineteen.append(mp1sp2)
lNineteen.append(MovePlatVert(784,215,30,23,172,281,[mp1sp2,mp1sp1,mp1plat1]))

mp2plat1 = Platform(840,406,73,23,ORANGE)
lNineteen.append(mp2plat1)
mp2sp1 = GreenSpike(857,373)
lNineteen.append(mp2sp1)
mp2sh1 = smallShrub(851,220)
lNineteen.append(mp2sh1)
lNineteen.append(MovePlatVert(860,272,30,23,172,310,[mp2sp1,mp2sh1,mp2plat1]))

mp3plat1 = Platform(925,433,73,23,ORANGE)
lNineteen.append(mp3plat1)
mp3sp1 = GreenSpike(934,400)
lNineteen.append(mp3sp1)
lNineteen.append(MovePlatVert(946,322,30,23,172,333,[mp3sp1,mp3plat1]))

mp4plat1 = Platform(1017,417,73,23,ORANGE)
lNineteen.append(mp4plat1)
mp4sp1 = GreenSpike(1017,384)
lNineteen.append(mp4sp1)
mp4sh1 = smallShrub(1029,237)
lNineteen.append(mp4sh1)
lNineteen.append(MovePlatVert(1038,289,30,23,172,310,[mp4sp1,mp4sh1,mp4plat1]))

mp5plat1 = Platform(1102,444,73,23,ORANGE)
lNineteen.append(mp5plat1)
lNineteen.append(MovePlatVert(1123,330,30,23,172,331,[mp5plat1]))

mp6plat1 = Platform(352,662,11,48,ORANGE)
lNineteen.append(mp6plat1)
mp6plat2 = Platform(503,662,11,48,ORANGE)
lNineteen.append(mp6plat2)
lNineteen.append(MovePlatVert(423,662,11,48,620,740,[mp6plat1, mp6plat2]))


mp7plat1 = Platform(583,662,11,48,ORANGE)
lNineteen.append(mp7plat1)
mp7plat2 = Platform(731,662,11,48,ORANGE)
lNineteen.append(mp7plat2)
lNineteen.append(MovePlatVert(657,662,11,48,620,740,[mp7plat1, mp7plat2]))

mp8plat1 = Platform(884,662,11,48,ORANGE)
lNineteen.append(mp8plat1)
mp8plat2 = Platform(1035,662,11,48,ORANGE)
lNineteen.append(mp8plat2)
lNineteen.append(MovePlatVert(955,662,11,48,620,740,[mp8plat1, mp8plat2]))

lNineteen.append(endSign(1150,716))
lNineteen.append(lBorderRight)
lNineteen.append(lBorderLeft)
levelNineteen=Level(lNineteen,0,10,"lvl-13-16-background.png")




lTwenty = []

lTwenty.append(Platform(0,757,1200,43,WHITE))
lTwenty.append(Platform(598,645,311,22,WHITE))
lTwenty.append(Platform(598,432,311,22,WHITE))
lTwenty.append(Platform(973,637,218,22,WHITE))
lTwenty.append(Platform(973,499,218,22,WHITE))
lTwenty.append(Platform(184,421,365,22,WHITE))
lTwenty.append(Platform(184,303,311,22,WHITE))
lTwenty.append(Platform(480,171,15,132,WHITE))
lTwenty.append(Platform(1082,188,127,37,WHITE))

lTwenty.append(FallPlat(132,705,20,20,BEIGE))
lTwenty.append(FallPlat(184,667,20,20,BEIGE))
lTwenty.append(FallPlat(275,647,20,20,BEIGE))
lTwenty.append(FallPlat(357,627,20,20,BEIGE))
lTwenty.append(FallPlat(450,627,20,20,BEIGE))
lTwenty.append(FallPlat(117,305,20,20,BEIGE))
lTwenty.append(FallPlat(40,283,20,20,BEIGE))
lTwenty.append(FallPlat(15,237,20,20,BEIGE))
lTwenty.append(FallPlat(97,189,20,20,BEIGE))
lTwenty.append(FallPlat(164,147,20,20,BEIGE))

lTwenty.append(FallPlat(536,183,10,10,BEIGE))
lTwenty.append(FallPlat(586,161,10,10,BEIGE))
lTwenty.append(FallPlat(661,157,10,10,BEIGE))
lTwenty.append(FallPlat(715,179,10,10,BEIGE))
lTwenty.append(FallPlat(777,198,10,10,BEIGE))
lTwenty.append(FallPlat(823,183,10,10,BEIGE))
lTwenty.append(FallPlat(864,167,10,10,BEIGE))
lTwenty.append(FallPlat(930,196,10,10,BEIGE))
lTwenty.append(FallPlat(970,238,10,10,BEIGE))
lTwenty.append(FallPlat(1019,238,10,10,BEIGE))

lTwenty.append(Ladder(1063,498))
lTwenty.append(Ladder(191,303))

lTwenty.append(smallShrub(261,595))
lTwenty.append(smallShrub(436,575))
lTwenty.append(smallShrub(850,593))
lTwenty.append(smallShrub(973,585))
lTwenty.append(smallShrub(369,369))
lTwenty.append(smallShrub(295,369))
lTwenty.append(smallShrub(730,593))

lTwenty.append(TallShrub(501,238))
lTwenty.append(TallShrub(878,249))

lTwenty.append(GreenSpike(264,388))
lTwenty.append(GreenSpike(338,388))
lTwenty.append(GreenSpike(412,388))
lTwenty.append(GreenSpike(633,400))
lTwenty.append(GreenSpike(1010,466))
lTwenty.append(GreenLSpike(1049,187))

lTwenty.append(GreenSpike(501,726))
lTwenty.append(GreenSpike(537,726))
lTwenty.append(GreenSpike(572,726))
lTwenty.append(GreenSpike(609,726))
lTwenty.append(GreenSpike(646,726))
lTwenty.append(GreenSpike(683,726))
lTwenty.append(GreenSpike(720,726))
lTwenty.append(GreenSpike(757,726))
lTwenty.append(GreenSpike(794,726))
lTwenty.append(GreenSpike(831,726))
lTwenty.append(GreenSpike(868,726))
lTwenty.append(GreenSpike(905,726))
lTwenty.append(GreenSpike(942,726))
lTwenty.append(GreenSpike(979,726))
lTwenty.append(GreenSpike(1016,726))
lTwenty.append(GreenSpike(1053,726))
lTwenty.append(GreenSpike(1090,726))
lTwenty.append(GreenSpike(1127,726))
lTwenty.append(GreenSpike(1164,726))

l20mp1plat1 = Platform(664,534,37,29,ORANGE)
lTwenty.append(l20mp1plat1)
l20mp1sp1 = GreenDSpike(664,563)
lTwenty.append(l20mp1sp1)
l20mp1sp2 = GreenDSpike(809,563)
lTwenty.append(l20mp1sp2)
l20mp1 = MovePlatVert(809,534,37,29,458,597,[l20mp1plat1,l20mp1sp1,l20mp1sp2])
lTwenty.append(l20mp1)

l20mp2sp1 = GreenSpike(736,292)
lTwenty.append(l20mp2sp1)
l20mp2sp2 = GreenDSpike(736,354)
lTwenty.append(l20mp2sp2)
l20mp2 = MovePlatVert(736,325,37,29,280,370,[l20mp2sp1,l20mp2sp2])
lTwenty.append(l20mp2)

l20mp3p1 = Platform(240,198,37,29,ORANGE)
lTwenty.append(l20mp3p1)
l20mp3sp1 = GreenDSpike(240,227)
lTwenty.append(l20mp3sp1)
l20mp3sp2 = GreenDSpike(322,198)
lTwenty.append(l20mp3sp2)
l20mp3sh1 = smallShrub(234,146)
lTwenty.append(l20mp3sh1)
l20mp3sh2 = smallShrub(316,117)
lTwenty.append(l20mp3sh2)
l20mp3 = MovePlatVert(322,169,37,29,93,213,[l20mp3p1,l20mp3sp1,l20mp3sp2,l20mp3sh1,l20mp3sh2])
lTwenty.append(l20mp3)

l20mp4sp1 = GreenSpike(402,146)
lTwenty.append(l20mp4sp1)
l20mp4sp2 = GreenDSpike(402,207)
lTwenty.append(l20mp4sp2)
l20mp4 = MovePlatVert(402,179,37,29,131,250,[l20mp4sp1,l20mp4sp2])
lTwenty.append(l20mp4)

lTwenty.append(endSign(1150,147))
lTwenty.append(lBorderRight)
lTwenty.append(lBorderLeft)
levelTwenty=Level(lTwenty,15,650,"lvl-13-16-background.png")



def loadLevel(window, level):
    level.reset()
    level.object_list.append(fullScreenLeft)
    level.object_list.append(fullScreenBottom)
    level.object_list.append(fullScreenRight)    
    clock = pygame.time.Clock()
    background=level.background
    bg_image=level.bg_image
    playerOne=Player(level.init_x,level.init_y,30,64)
    check_size=(1200,800)
    timer.reset_timer()
    timer.start_timer()
    offset=0
    global last_pause_time
    last_pause_time = 0
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        playerOne.loop(FPS)
        level.loop(playerOne)
        screen_size=pygame.display.get_window_size()
        width=screen_size.__getitem__(0)
        if screen_size != check_size:
            offset=(abs((width-1200)))/2
        else:
            offset=0
        #       for object in level.object_list:
        #        object.rect.x=object.original_x+offset
        #elif offset !=0:
        #    for object in level.object_list:
        #        object.rect.x-=offset
        #    offset=0
        getInput(playerOne,level)
        draw(window, background, bg_image,playerOne,level,offset)
       
    pygame.quit()
    quit()

if __name__ == "__main__":
    display_main_menu(window)
