# environment setup taken from freeCodeCamp.org on Youtube: https://www.youtube.com/watch?v=6gLeplbqtqg
# basis for player movement/collision, background setup from same source
import os
import random
import math
import pygame
import sys
import tkinter
import json
from tkinter import messagebox
import requests

from gameObjects import Object, goldShears, Platform, Block, smallShrub, TallShrub, Spike, Water, FallPlat, Ladder, endSign, BlackSpike,SmallSpike,BlackLSpike,BlackRSpike,BlueSpike, SideSpike, ReverseSmallShrub, Void, MovePlat, MovePlatVert, MovePlatDiag, TallPinkShrub,TallPurpleShrub,TallRedShrub,SmallPinkShrub,SmallPurpleShrub,SmallRedShrub,RedSpike,BlueSpike,GoldSpike,GreenSpike,GoldDSpike,GoldLSpike,GoldRSpike,GreenDSpike,GreenLSpike,GreenRSpike, AnglePlat, AngleSpike
from MenuWidgets import *
from tutorial_page import show_tutorial
from pause_menu import show_pause_menu
from competitiveMainMenu import show_competitive_main_menu
from level_timer import *
import ntplib

from os import listdir
from os.path import isfile, join
#from pygame.sprite import _Group
from time import gmtime, strftime


pygame.init()

gameIcon = pygame.image.load("assets/Traps/SmallShrub/SmallShrub.png")
pygame.display.set_icon(gameIcon)

def assignVolume():
    vol_states = []   # Ex. [1, 1, False] -> music slider pos (start at 100%), sfx slider pos (start at 100%), checkbox status (starts unchecked)

    with open("assets/txt/al.txt", "r") as audioFile:
        for line in audioFile:
            line = line.strip()
            if line.lower() == "true":
                vol_states.append(True)
            elif line.lower() == "false":
                vol_states.append(False)
            # If not a boolean, try converting to float
            else:
                try:
                    vol_states.append(float(line))
                except ValueError:
                    print(f"Unexpected value (not bool or float): {line}")
    return vol_states

VOLUME_STATES = assignVolume()

# VOLUME_STATES = [1, 1, False]   # music slider pos (start at 100%), sfx slider pos (start at 100%), checkbox status (starts unchecked)
pygame.mixer.music.load("assets/audio/background_music.mp3")   # https://www.youtube.com/watch?v=cTDSFCC9rQ4
pygame.mixer.music.play(loops=-1)   # play and loop music indefinitely
pygame.mixer.music.set_volume(VOLUME_STATES[0])   # initialize max volume of music from assets/txt/al.txt

if VOLUME_STATES[2]:   # if previously muted is True
    pygame.mixer.music.pause()

hitTree = pygame.mixer.Sound("assets/audio/hitting-tree.mp3")   # https://pixabay.com/sound-effects/chopping-wood-96709/

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
user_name = ''

window = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)
global timer
global last_pause_time
global hertz_ee
global servers
servers = ['time.nist.gov', 'time.google.com', 'time.windows.com', 'pool.ntp.org', 'north-america.pool.ntp.org']

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

        self.feetBox=Platform(x+13,y+(height-3),width,10,WHITE)
        self.feetBox.surface=pygame.Surface((width,10))
        self.feetBox.mask= pygame.mask.from_surface(self.feetBox.surface)


    def reset(self,level):
        #print("RESET")
        self.rect=pygame.Rect(level.init_x, level.init_y,self.wO,self.hO)
        self.reachBox.x=self.rect.x-15
        self.reachBox.y=self.rect.y-15
        self.feetBox.rect.x=self.rect.x+13
        self.feetBox.rect.y=self.rect.y+(self.rect.height-3)
        self.x_velocity=0
        self.y_velocity=0
        self.update()
        level.reset()


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.reachBox.rect.x=self.rect.x-15
        self.reachBox.rect.y=self.rect.y-15

        self.feetBox.rect.x=self.rect.x+13
        self.feetBox.rect.y=self.rect.y+(self.rect.height-3)

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

    def end_chop(self):
        with open('assets/txt/al.txt', 'r') as audioFile:
            lines = audioFile.readlines()
        if lines[2].strip().lower() == "false":
            hitTree.set_volume(float(lines[1]))
            hitTree.play()

    def update_sprite(self):
        f = open("assets/txt/cc.txt", "r")
        current_character = f.read()

        if current_character == "":
            current_character = "Celia"
            f.close()
            f = open("assets/txt/cc.txt", "w")
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
            self.end_chop()

        self.fall_count += 1
        self.update_sprite()

    def draw(self, window, offset_x):
        #self.reachBox.draw(window,0)------------VISUALISE reachBox
        #self.feetBox.draw(window,0)#--------------VISUALISE feetBox
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
        ColorfulButton((screen_width/2, (screen_height/2)-120), (300, 54), "BEGIN YOUR QUEST", start_game),
        ColorfulButton((screen_width/2, (screen_height/2)-40), (300, 54), "LOAD LEVEL", load_level),
        ColorfulButton((screen_width/2, (screen_height/2)+40), (300, 54), "SETTINGS", settings),
        ColorfulButton((screen_width/2, (screen_height/2)+120), (300, 54), "QUIT", quit_game)
    ]

    global hertz_ee
    if hertz_ee:
        background_img = pygame.image.load("assets/Background/hertz_passion.png")
        for widget in widgets:
            widget.default_color = (137, 148, 153)
            widget.hover_color = (169, 169, 169)

    return widgets, background_img

def start_game():
    global timer
    timer = Timer()

    # Always Loads Level 1
    lvlf = open("assets/txt/cl.txt", "w")
    lvlf.write("1")
    lvlf.close()

    display_tut(window)

def load_level():
    global timer
    timer = Timer()

    # Loads level based on what current level you're on in
    lvlfile = open("assets/txt/cl.txt", "r")
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
        case "21":
            lvlf = open("assets/txt/cl.txt", "r")
            levelnum = int(lvlf.read())
            levelnum -= 1
            lvlf = open("assets/txt/cl.txt", "w")
            lvlf.write(str(levelnum))
            lvlf.close()
            loadLevel(window, levelTwenty)

    print("LOAD LEVEL " + currlvl)

def settings():
    display_settings_page(window)
    print("SETTINGS")

def leaderboard():
    display_leaderboard(window)
    print("LEADERBOARD")

def quit_game():
    pygame.quit()
    sys.exit()

konami = False
def display_main_menu(screen):
    global konami
    widgets, background_img = scale_window_main(screen)
    secret_code = [pygame.K_h, pygame.K_e, pygame.K_r, pygame.K_t, pygame.K_z]
    buffer = []

    maxlevelread = open("assets/txt/mu.txt", "r")
    max_level_unlocked = maxlevelread.read()

    KONAMI = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a]
    code, index = [], 0

    running = True
    while running:
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                widgets, background_img = scale_window_main(screen)   # rescales visuals for new resolution
            elif event.type == pygame.KEYDOWN:
                if len(buffer) == 0 or buffer[-1] != event.key:
                    buffer.append(event.key)

                    if len(buffer) > 5:
                        buffer.pop(0)

                    if buffer == secret_code:
                        global hertz_ee
                        hertz_ee = not hertz_ee
                        widgets, background_img = scale_window_main(screen)
                if konami == False:
                    if event.key == KONAMI[index]:
                        code.append(event.key)
                        index += 1
                        if code == KONAMI:
                            index = 0
                            if int(max_level_unlocked) < 15:
                                tkinter.messagebox.showinfo("A secret?","Check the character selection screen...")
                                print('KONAMI!')
                                konami = True
                            else:
                                tkinter.messagebox.showinfo("You did it!","You have already unlocked all 4 characters so the easter egg won't do anything, but good job finding it! :)")
                                konami = True
                    else:
                        code = []
                        index = 0



            # checks for buttons clicked
            for widget in widgets:
                widget.handle_event(event)

        # add background image and buttons to window
        screen.blit(background_img, (0, 0))

        for widget in widgets:
            widget.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def display_competitive_main_menu(screen):
    while True:
        global hertz_ee
        return_to, hertz_ee = show_competitive_main_menu(screen, hertz_ee)
        match return_to:
            case "START":
                start_game()
            case "LOAD":
                load_level()
            case"CHALLENGE MODE":
                if testConnection():
                    global timer
                    timer = CompetitiveTimer()
                    timer.start_timer()
                    loadLevel(screen,cOne)
                else:
                    tkinter.messagebox.showerror("Error", "Please connect to the Internet to play competitive mode.")
            case "LEADERBOARD":
                try:
                  info = retrieve_data_php()
                except:
                    tkinter.messagebox.showerror("Error", "Unable to connect to leaderboard. Please connect to the Internet.")
                    continue
                display_leaderboard(window, info)
            case "SETTINGS":
                settings()


# Function to insert data into the database via PHP endpoint
def insert_data_php(username, time, character):
    mode = 1
    data = retrieve_data_php()
    for lists in data:
        if username in lists and character in lists:
            mode = 2
    url = 'https://www-student.cse.buffalo.edu/CSE442-542/2023-Fall/cse-442ai/dbinteract.php'
    payload = {'username': username, 'time': time, 'character': character, 'mode': mode}
    response = requests.post(url, data=payload)



# Function to retrieve data from the database via PHP endpoint
def retrieve_data_php():
    url = 'https://www-student.cse.buffalo.edu/CSE442-542/2023-Fall/cse-442ai/dbinteract.php'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        ret = []
        for lists in data:
            add = []
            for vals in lists.values():
                add.append(vals)
            ret.append(add)
        print(ret)
        return ret


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
    sys.exit()

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
    lvlfile = open("assets/txt/cl.txt", "r")
    currlvl = lvlfile.read()
    lvlint = int(currlvl)
    if os.path.exists("competitive.txt"):
        display_competitive_main_menu(window)
    elif lvlint > 20:
        if user_name != '':
            nametaken = 0
            try:
                checkForName = retrieve_data_php()
            except:
                    tkinter.messagebox.showwarning("Warning","Please Connect to the Internet and Try Again.")
                    return
            for lists in checkForName:
                if user_name in lists:
                    nametaken = 1
            if nametaken == 1:
                tkinter.messagebox.showwarning("Warning","Sorry, the username you've entered is already in use, please try another name.")
            else:
                #name available, so need to add blank entry to db
                try:
                    insert_data_php(user_name, '999999', 'nameholder')
                except:
                    tkinter.messagebox.showwarning("Warning","Please Connect to the Internet and Try Again.")
                    return
                open("competitive.txt", "x").close()
                writeName = open("competitive.txt", "w")
                writeName.write(user_name)
                writeName.close()
                wlvlfile = open("assets/txt/cl.txt", "w")
                wlvlfile.write("1")
                wlvlfile.close()
                display_competitive_main_menu(window)
        else:
            tkinter.messagebox.showwarning("Warning","Please Enter a Name Before Returning to Menu")
    else:
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
    sys.exit()


##############################################################
##############################################################
#################### LEADERBOARD SCREEN ######################
##############################################################
##############################################################

class LeaderboardSlot:
    def __init__(self, pos: tuple, size: tuple, text: str, action=None):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(self.pos[0] - (self.size[0] / 2), self.pos[1] - (self.size[1] / 2), self.size[0],
                                self.size[1])
        self.text = text
        self.action = action
        self.color = (190, 190, 190)

    def draw(self, screen):
        button_surface = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA)
        button_surface.set_alpha(210)
        pygame.draw.rect(button_surface, self.color, (0, 0, self.size[0], self.size[1]), border_radius=7)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.size[0] / 2, self.size[1] / 2))
        button_surface.blit(text_surface, text_rect)
        button_rect = button_surface.get_rect(center=(self.pos[0], self.pos[1]))

        screen.blit(button_surface, button_rect)

def dummyReturn():
    return


def display_leaderboard(screen, data):
    sorted_entries = sorted(data, key=lambda x: float(x[1]))

    no_duplicates, logged = [], []
    for entry in sorted_entries:
        username = entry[0]
        if username not in logged:
            logged.append(username)
            no_duplicates.append(entry)

    top_10 = no_duplicates[:10]

    readName = open("competitive.txt", "r")
    current_user = readName.read()
    current_user_time, current_user_character, current_user_position = "N/A", "N/A", "N/A"
    readName.close()

    for entry in no_duplicates:
        if current_user in entry:
            if entry[1] != 999999 and entry[2] != "nameholder":
                current_user_time, current_user_character, current_user_position = entry[1], entry[2], no_duplicates.index(entry) + 1

    positions = []
    screen_width, screen_height = screen.get_size()
    background_img = pygame.image.load("assets/Background/BetlvlBackground.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))
    widgets = [
        LeaderboardSlot((screen_width/2, (screen_height*.185)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.255)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.325)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.395)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.465)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.535)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.605)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.685)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.755)), (screen_width*.7, 45), "", dummyReturn),
        LeaderboardSlot((screen_width/2, (screen_height*.825)), (screen_width*.7, 45), "", dummyReturn),

        LeaderboardSlot((screen_width/2, (screen_height*.935)), (screen_width*.7, 45), "", dummyReturn),

        Button((screen_width * .08, (screen_height * .06)), (150, 54), "MENU", return_main)
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = screen.get_size()
                widgets = [
                    LeaderboardSlot((screen_width/2, (screen_height*.185)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.255)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.325)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.395)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.465)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.535)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.605)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.685)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.755)), (screen_width*.7, 45), "", dummyReturn),
                    LeaderboardSlot((screen_width/2, (screen_height*.825)), (screen_width*.7, 45), "", dummyReturn),

                    LeaderboardSlot((screen_width/2, (screen_height*.935)), (screen_width*.7, 45), "", dummyReturn),

                    Button((screen_width * .08, (screen_height * .06)), (150, 54), "MENU", return_main)
                ]
                background_img = pygame.image.load("assets/Background/BetlvlBackground.png")
                background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

            for widget in widgets:
                if type(widget) == Button:
                    widget.handle_event(event)

            count = 0
            for widget in widgets:
                positions.append(widget.pos)
                count += 1
                if count == 10:
                    count = 0
                    break

        # render background and widgets
        screen.blit(background_img, (0, 0))

        draw_text("TOP 10 LEADERBOARD", pygame.font.Font(None, 50), (0, 0, 0), ((screen_width/2, (screen_height * .065))))
        draw_text("NAME", pygame.font.Font(None, 36), (0, 0, 0), ((screen_width * .18, (screen_height * .135))))
        draw_text("TIME", pygame.font.Font(None, 36), (0, 0, 0), ((screen_width * .5, (screen_height * .135))))
        draw_text("CHARACTER", pygame.font.Font(None, 36), (0, 0, 0), ((screen_width * .78, (screen_height * .135))))

        for widget in widgets:
            widget.draw(screen)

        leaderboard_entry_font = pygame.font.Font(None, 36)
        for i in zip(top_10, positions):
            user, user_time, character, height = i[0][0], i[0][1], i[0][2], i[1][1]

            userText = leaderboard_entry_font.render(user, False, (34, 90, 48))
            userTextRect = userText.get_rect()
            userTextRect.left, userTextRect.centery = screen_width * .16, height

            characterText = leaderboard_entry_font.render(character, False, (34, 90, 48))
            characterTextRect = characterText.get_rect()
            characterTextRect.right, characterTextRect.centery = screen_width * .84, height

            screen.blit(userText, userTextRect)
            correct_time = strftime("%M:%S", gmtime(float(user_time)))
            draw_text(correct_time, pygame.font.Font(None, 36), (34, 90, 48), (screen_width * .5, height))
            screen.blit(characterText, characterTextRect)

        first, second, third = pygame.image.load("assets/leaderboard/first.png"), pygame.image.load("assets/leaderboard/second.png"), pygame.image.load("assets/leaderboard/third.png")
        firstRect, secondRect, thirdRect = first.get_rect(), second.get_rect(), third.get_rect()
        firstRect.left, firstRect.centery = widgets[0].pos[0] * .21, widgets[0].pos[1]
        secondRect.left, secondRect.centery = widgets[1].pos[0] * .21, widgets[1].pos[1]
        thirdRect.left, thirdRect.centery = widgets[2].pos[0] * .21, widgets[2].pos[1]

        screen.blit(first, firstRect)
        screen.blit(second, secondRect)
        screen.blit(third, thirdRect)

        for i in range(3, 10):
            height = widgets[i].pos[1]
            draw_text("#" + str(i + 1), pygame.font.Font(None, 40), (0, 0, 0), ((screen_width * .125, (height))))


        height = widgets[10].pos[1]

        if current_user_position != "N/A":
            draw_text("#" + str(current_user_position), pygame.font.Font(None, 40), (0, 0, 0), ((screen_width * .125, (height))))

        userText = leaderboard_entry_font.render(current_user, False, (34, 90, 48))
        userTextRect = userText.get_rect()
        userTextRect.left, userTextRect.centery = screen_width * .16, height

        characterText = leaderboard_entry_font.render(current_user_character, False, (34, 90, 48))
        characterTextRect = characterText.get_rect()
        characterTextRect.right, characterTextRect.centery = screen_width * .84, height

        screen.blit(userText, userTextRect)

        if current_user_time == "N/A":
            draw_text(current_user_time, pygame.font.Font(None, 36), (34, 90, 48), (screen_width * .5, height))
        else:
            correct_time = strftime("%M:%S", gmtime(float(current_user_time)))
            draw_text(correct_time, pygame.font.Font(None, 36), (34, 90, 48), (screen_width * .5, height))

        screen.blit(characterText, characterTextRect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


##############################################################
##############################################################
################# CHOOSE CHARACTER SCREEN ####################
##############################################################
##############################################################

character_select_font = pygame.font.Font(None, 32)

f = open("assets/txt/cc.txt", "r")
current_character = f.read()
powerup_read, cooldown_read = "", ""

maxlevelread = open("assets/txt/mu.txt", "r")
max_level_unlocked = maxlevelread.read()
if current_character == "" or max_level_unlocked == "" or int(max_level_unlocked) < 5:
    current_character = "Celia"
    f.close()
    f = open("assets/txt/cc.txt", "w")
    f.write("Celia")
    f.close()
    f = open("assets/txt/cc.txt", "r")
    powerup_read = "N/A"
elif (current_character == "Malcolm" and int(max_level_unlocked) < 5) or (current_character == "Maia" and int(max_level_unlocked) < 10) or (current_character == "Oscar" and int(max_level_unlocked) < 15):
    current_character = "Celia"
    f.close()
    f = open("assets/txt/cc.txt", "w")
    f.write("Celia")
    f.close()
    f = open("assets/txt/cc.txt", "r")
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
character_text = character_select_font.render(current_character, False, char_text_color)
powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")
cooldown_text = character_select_font.render(cooldown_read, False, "Black")
print(current_character)

clevel = open("assets/txt/cl.txt", "r")
current_level = clevel.read()
max_level = str(int(current_level) - 1)
clevel.close()
maxlevelread.close()
if max_level_unlocked == "" or int(max_level_unlocked) < int(max_level):
    max_level_unlocked = max_level
    w_max = open("assets/txt/mu.txt", "w")
    w_max.write(str(max_level_unlocked))
    w_max.close()

# onClick events for each character and the OK button
def click_Celia():
    global konami
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
    global konami
    global current_character
    global character_text
    global selected_text
    global powerup_read
    global powerup_text
    global cooldown_read
    global cooldown_text

    maxlevelread = open("assets/txt/mu.txt", "r")
    max_level_unlocked = maxlevelread.read()

    if max_level_unlocked != "" and int(max_level_unlocked) >= 5 or konami == True:
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
    global konami

    maxlevelread = open("assets/txt/mu.txt", "r")
    max_level_unlocked = maxlevelread.read()

    if max_level_unlocked != "" and int(max_level_unlocked) >= 10 or konami == True:
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
    global konami

    maxlevelread = open("assets/txt/mu.txt", "r")
    max_level_unlocked = maxlevelread.read()

    if max_level_unlocked != "" and int(max_level_unlocked) >= 15 or konami == True:
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


# confirms player's selected choice, writes character's name to "assets/txt/cc.txt"
def click_OK():
    global current_character
    f = open("assets/txt/cc.txt", "w")
    f.write(current_character)
    f.close()
    f = open("assets/txt/cc.txt", "r")
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
    global konami

    check_unlocked_level()

    f = open("assets/txt/cc.txt", "r")
    current_character = f.read()
    print(current_character)
    maxlevelread = open("assets/txt/mu.txt", "r")
    max_level_unlocked = maxlevelread.read()

    if current_character == "":
        f.close()
        f = open("assets/txt/cc.txt", "w")
        f.write("Celia")
        f.close()
        f = open("assets/txt/cc.txt", "r")
        click_Celia()

    if konami == False:
        if max_level_unlocked == "" or int(max_level_unlocked) < 5:
            f.close()
            f = open("assets/txt/cc.txt", "w")
            f.write("Celia")
            f.close()
            f = open("assets/txt/cc.txt", "r")
            click_Celia()
        elif (current_character == "Malcolm" and int(max_level_unlocked) < 5) or (current_character == "Maia" and int(max_level_unlocked) < 10) or (current_character == "Oscar" and int(max_level_unlocked) < 15):
            f.close()
            f = open("assets/txt/cc.txt", "w")
            f.write("Celia")
            f.close()
            f = open("assets/txt/cc.txt", "r")
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
    elif konami == True:
        if current_character == "Celia":
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
    f = open("assets/txt/cc.txt", "r")
    selected_text = character_select_font.render("You are currently playing as", False, "Black")
    character_text = character_select_font.render(current_character, False, char_text_color)
    powerup_text = character_select_font.render("Power-up: " + str(powerup_read), False, "Black")
    cooldown_text = character_select_font.render(cooldown_read, False, "Black")
    print(current_character)


def check_unlocked_level():
    global current_character
    global konami

    maxlevelread = open("assets/txt/mu.txt", "r")
    max_level_unlocked = maxlevelread.read()

    if konami == False:
        if max_level_unlocked == "" or int(max_level_unlocked) < 5:
            current_character = "Celia"
            f = open("assets/txt/cc.txt", "w")
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

    # if konami == True:
    #     Celia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Celia.png'))
    #     Malcolm.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Malcolm.png'))
    #     Maia.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Maia.png'))
    #     Oscar.image = pygame.image.load(os.path.join('assets', 'CharacterProfiles', 'Oscar.png'))


def display_choose_character(window):
    global konami
    background = pygame.image.load("assets/Background/BetLvlBackground.png")
    size = pygame.display.get_window_size()
    screen_width, screen_height = size[0], size[1]
    background = pygame.transform.scale(background, size)
    widgets = [Button((screen_width/2, (screen_height/2) + 160), (300, 54), "OK", click_OK)]

    check_update()
    check_unlocked_level()

    print(konami, "Konami!")

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
    sys.exit()


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
    lvlf = open("assets/txt/cl.txt", "r")
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
    lvlf = open("assets/txt/cl.txt", "r")
    currlvl = lvlf.read()
    printlvl = str(int(currlvl) - 1)
    lvlf.close()

    maxlevelread = open("assets/txt/mu.txt", "r")
    max_level_unlocked = maxlevelread.read()
    maxlevelread.close()

    if max_level_unlocked == "" or int(max_level_unlocked) < int(printlvl):
        max_level_unlocked = printlvl
        w_max = open("assets/txt/mu.txt", "w")
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
    sys.exit()


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
        Button((screen_width/2, (screen_height/2)+100), (300, 54), "RETURN TO MAIN", return_main)
    ]

    return widgets, screen_width, screen_height, background_img


def display_endgame_level_page(screen):
    widgets, screen_width, screen_height, background_img = scale_window_endgame(screen)

    #get level num
    lvlf = open("assets/txt/cl.txt", "r")
    currlvl = lvlf.read()
    printlvl = str(int(currlvl) - 1)
    lvlf.close()

    currtime = str(round(timer.return_time(), 2))

    global user_name
    input_rect = pygame.Rect(screen_width/2-100,screen_height/2,200,50)
    boxcolor = pygame.Color(190,190,190)
    keycount = 0
    betweenlvl = True
    while betweenlvl:
        for event in pygame.event.get():
            #event handler
            if event.type == pygame.QUIT:
                betweenlvl=False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and keycount >= 1:
                    user_name = user_name[:-1]
                    keycount -= 1
                elif keycount < 12 and event.key != pygame.K_BACKSPACE and event.key != pygame.K_LSHIFT:
                    user_name += event.unicode
                    keycount +=1
            for widget in widgets:
                if type(widget) == Button or type(widget) == Checkbox:
                    widget.handle_event(event)
                elif type(widget) == Slider:
                    widget.handle_event(pygame.mouse.get_pos(), pygame.mouse.get_pressed())

        #message display code
        screen.blit(background_img, (0,0))

        draw_text("Congratulations!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-240))
        draw_text("You Have Beaten Shrubbery Quest!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-180))
        draw_text("Your Time For Level 20 Was: " + currtime + "s", pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-130))
        draw_text("You Can Now Access Challenge Mode!", pygame.font.Font(None, 56),(34, 90, 48), ((screen_width/2), (screen_height/2)-80))
        draw_text("First, Please Enter A Username And Then Return To Menu", pygame.font.Font(None, 42),(34, 90, 48), ((screen_width/2), (screen_height/2)-30))

        for widget in widgets:
            widget.draw(screen)

        #user input box code
        pygame.draw.rect(screen, boxcolor, input_rect)
        namefont = pygame.font.Font(None, 36)
        text_surface = namefont.render(user_name, True, (34, 90, 48))
        screen.blit(text_surface, (input_rect.x+10, input_rect.y+15))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

def display_level_twenty_page(screen):
    screen_width, screen_height = screen.get_size()

    background_img = pygame.image.load("assets\Background\BetlvlBackground.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

    widget = Button((screen_width/2, (screen_height/2)+20), (300, 54), "RETURN TO MAIN", return_main)

    currtime = str(round(timer.return_time(), 2))

    betweenlvl = True
    while betweenlvl:
        for event in pygame.event.get():
            #event handler
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            widget.handle_event(event)

        screen.blit(background_img, (0,0))
        draw_text("Congratulations!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-190))
        draw_text("You Beat Level 20!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-130))
        draw_text("Your Time Was: " + currtime + "s", pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-80))

        widget.draw(screen)
        pygame.display.flip()

def beat_competitive_page(screen):
    screen_width, screen_height = screen.get_size()

    background_img = pygame.image.load("assets\Background\BetlvlBackground.png")
    background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

    widget = Button((screen_width/2, (screen_height/2)+20), (300, 54), "RETURN TO MAIN", return_main)

    currtime = timer.return_time()
    try:
        namef = open("competitive.txt", "r")
        username = namef.read()
        namef.close()
        characterf = open("assets/txt/cc.txt", "r")
        character = characterf.read()
        characterf.close()
        insert_data_php(username, currtime, character)
    except:
        tkinter.messagebox.showerror("Error","You are unable to connect to the database, your data has not been saved to the leaderboard")

    minutes = math.floor(currtime / 60)
    seconds = round(currtime  - (minutes * 60), 2)
    hours = math.floor(minutes / 60)
    minutes = minutes  - (hours * 60)

    betweenlvl = True
    while betweenlvl:
        for event in pygame.event.get():
            #event handler
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            widget.handle_event(event)

        screen.blit(background_img, (0,0))
        draw_text("Congratulations!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-190))
        draw_text("You Finished Competitive Mode in:", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-130))
        if hours < 1:
            draw_text(str(minutes) + " minutes and " + str(seconds) + " seconds!", pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-80))
        else:
            if hours > 99:
                draw_text("99 hours 99 minutes and 99.99 seconds!", pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-80))
            else:
                draw_text(str(hours) + " hours " + str(minutes) + " minutes and " + str(seconds) + " seconds!", pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-80))

        widget.draw(screen)
        pygame.display.flip()


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
        self.is_comp=False
        self.next_level=None
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
    #for tile in background:
    #    offtile=(tile.__getitem__(0)+offset,tile.__getitem__(1))
    #    window.blit(bg_image, offtile)
    window.blit(bg_image, (offset,0))

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
                player.powerup_timer = 0
                player.cooldown_timer = 0
                player.powerup_active = False
                player.cooldown_active = False
                player.reset(level)
                continue
            elif(object.name == "void" or object.name=="water"):
                print("hit a void/water in vert")
                player.x_velocity=0
                player.y_velocity=0#Helps 0 out if gravity is huge
                player.powerup_timer = 0
                player.cooldown_timer = 0
                player.powerup_active = False
                player.cooldown_active = False
                player.reset(level)
                continue

            #keep from reseting Y
            elif dy > 0 and object.name!="ladder" and not player.on_ladder:
                if not (player.rect.bottom-2*player.y_velocity)>object.rect.top or object.name=="angle":#if the players bottom is not within 12 pixels of the object's top
                    player.rect.bottom = object.rect.top#put the player on top of the object
                    player.landed()
                else:
                    if player.rect.right>object.rect.right:#Falling off right side
                        #print("PUSHRDOWN")
                        #print("NAME",object.name)
                        player.rect.x=object.rect.right#(player.rect.right-object.rect.right)
                        player.rect.x+=1
                    elif player.rect.left<object.rect.left:#Falling of left side
                            #print("PUSHLDOWN")
                            #print("NAME",object.name)
                            player.rect.x+=(object.rect.left-player.rect.right)
                            player.rect.x-=1

            elif dy < 0 and object.name!="ladder" and not player.on_ladder:
                if object.name=="tall shrub" or object.name=="small shrub":
                    #if object.name=="small shrub":
                        #player.y_velocity=PLAYER_VEL*2
                        #player.hit_head()
                    if player.rect.right>object.rect.right:#Jumping into right side
                        #print("PUSHRUP")
                        #print("NAME",object.name)
                        player.rect.x=object.rect.right#(player.rect.right-object.rect.right)
                        player.rect.x+=1
                    elif player.rect.left<object.rect.left:#Jumping into left side
                        #print("PUSHLUP")
                        #print("NAME",object.name)
                        player.rect.x+=(object.rect.left-player.rect.right)
                        player.rect.x-=1
                else:
                    #print("BONK")
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
                player.powerup_timer = 0
                player.cooldown_timer = 0
                player.powerup_active = False
                player.cooldown_active = False
                player.reset(level)
            elif(object.name == "void" or object.name=="water"):
                print("hit water/void in collide")
                player.x_velocity=0
                player.y_velocity=0#Helps 0 out if gravity is huge
                player.powerup_timer = 0
                player.cooldown_timer = 0
                player.powerup_active = False
                player.cooldown_active = False
                player.reset(level)
                continue

            elif(object.name == "end sign"):
                # collided_object = object
                #PLAYER HAS REACHED END OF LEVEL
                # ADD ONE TO COMPLETED LEVELS
                #ENDLEVEL = True
                if level.is_comp:
                    if testConnection():
                        if level.next_level!=None:
                            loadLevel(window,level.next_level)#Move to the next competitive level
                        else:
                            timer.stop_timer()
                            beat_competitive_page(window)
                    else:
                        tkinter.messagebox.showerror("Error", "Lost Internet connection. Please reconnect to the Internet to play competitive mode.")
                        display_competitive_main_menu(window)
                else:
                    timer.stop_timer()
                    lvlf = open("assets/txt/cl.txt", "r")
                    levelnum = int(lvlf.read())
                    levelnum += 1
                    lvlf = open("assets/txt/cl.txt", "w")
                    lvlf.write(str(levelnum))
                    lvlf.close()
                    # THEN OPEN BETWEEN LEVEL MENU
                    if levelnum > 20:
                        if not os.path.exists("competitive.txt"):
                            display_endgame_level_page(window)
                        else:
                            display_level_twenty_page(window)
                    else:
                        display_between_level_page(window)
                break

    player.move(-dx, 0)

    player.x_velocity=0
    player.update()
    return collided_object

def checkOverlap(player, level):
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
                        player.rect.x=object.rect.x-15#set x value to Ladder x Valued  object.rect.x-object.rect.width/2?
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
            if timer.stop_timer() == False:
                tkinter.messagebox.showerror("Error", "Lost Internet connection. Please reconnect to the Internet to play competitive mode.")
                if os.path.exists("competitive.txt"):
                        display_competitive_main_menu(window)
                else:
                    display_main_menu(window)

            global last_pause_time
            time_since_last = timer.return_time() - last_pause_time
            if time_since_last > 0.40:
                if show_pause_menu(window, VOLUME_STATES):
                    if os.path.exists("competitive.txt"):
                        display_competitive_main_menu(window)
                    else:
                        display_main_menu(window)
                last_pause_time = timer.return_time()

            if timer.start_timer() == False:
                tkinter.messagebox.showerror("Error", "Lost Internet connection. Please reconnect to the Internet to play competitive mode.")
                if os.path.exists("competitive.txt"):
                        display_competitive_main_menu(window)
                else:
                    display_main_menu(window)

        if current_character == "Malcolm":
            if keys[pygame.K_q] and player.jump_count == 1 and player.in_air:
                player.jump()

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
fullScreenLeft=Void(-2000,0,1990,2000,BLACK,None)
fullScreenRight=Void(1210,0,2000,2000,BLACK,None)
fullScreenBottom=Void(-2000,801,5200,2000,BLACK,None)


##############################################################
######################## LEVEL 01 ############################
##############################################################
lOne=[]
lBorderLeft=Platform(-10,0,10,800,BLACK)
lBorderRight=Platform(1201,0,10,800,BLACK)
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

##############################################################
######################## LEVEL 02 ############################
##############################################################
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


##############################################################
######################## LEVEL 04 ############################
##############################################################
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


##############################################################
######################## LEVEL 05 ############################
##############################################################
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

##############################################################
######################## LEVEL 06 ############################
##############################################################
lSix=[]
lSix.append(Void(0,800,1050,15))
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

lSix.append(MovePlat(281, 405, 200, 51, 34, 825))#right bound changed from 860


fixSpike=BlackLSpike(830,410)
lSix.append(fixSpike)


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
lSix.append(Ladder(1078,770))
lSix.append(lBorderLeft)
lSix.append(lBorderRight)
# End Level 6
lSix.append(endSign(1086,730))
levelSix=Level(lSix,25,50,"CaveBackground1.png")

##############################################################
######################## LEVEL 07 ############################
##############################################################
lSeven=[]
lSeven.append(Void(0,800,1200,15))
lSeven.append(Void(884,-5,242,5))
lSeven.append(Ladder(1070,-1))
lSeven.append(Ladder(1070,97))
lSeven.append(Ladder(1070,194))
lSeven.append(Platform(926,295,200,51,WHITE))##Start
lSeven.append(Platform(0,0,890,105,GRAY))
lSeven.append(Platform(0,0,34,800,GRAY))
lSeven.append(Platform(1126,0,74,631,GRAY))
lSeven.append(Platform(1126,747,74,100,GRAY))

# Moving platform line 1
mp07_1 = []
mp07_1.append(smallShrub(95,363))
mp07_1.append(ReverseSmallShrub(245,466))
mp07_1.append(Ladder(145, 414))
mp7_1 = MovePlat(95, 415, 200, 51, 69, 1091, oList=mp07_1)

mpo7_2 = []
mpo7_2.append(smallShrub(641,363))
mpo7_2.append(ReverseSmallShrub(792,466))
mp7_2 = MovePlat(642, 415, 200, 51, 69, 1091, oList=mpo7_2, aList=[mp7_1])##original as 34, 1126
mp7_1.set_a([mp7_2])

lSeven.append(mp7_1)
lSeven.extend(mp07_1)
lSeven.append(mp7_2)
lSeven.extend(mpo7_2)

# Moving platform line 2
mp07_3 = []
mp07_3.append(smallShrub(330,528))
mp07_3.append(ReverseSmallShrub(330,631))
mp7_3 = MovePlat(178, 580, 200, 51, 69, 1091, oList=mp07_3)##original borders 34, 1126

mpo7_4 = []
mpo7_4.append(smallShrub(624,528))
mpo7_4.append(ReverseSmallShrub(624,631))
mpo7_4.append(Ladder(673, 580))
mpo7_4.append(smallShrub(786,528))
mp7_4 = MovePlat(634, 580, 200, 51, 69, 1091, oList=mpo7_4, aList=[mp7_3])
mp7_3.set_a([mp7_4])

lSeven.append(mp7_3)
lSeven.extend(mp07_3)
lSeven.append(mp7_4)
lSeven.extend(mpo7_4)

# Moving platform line 3
mpl3_y = 747
mpls3_y = 695
mp07_5 = []
mp07_5.append(smallShrub(320,mpls3_y))
mp07_5.append(smallShrub(472,mpls3_y))
mp7_5 = MovePlat(320, mpl3_y, 200, 51, 69, 1091,oList=mp07_5)
mpo7_6 = []
mpo7_6.append(smallShrub(786,mpls3_y))
mp7_6 =  MovePlat(792, mpl3_y, 200, 51, 69, 1091,oList=mpo7_6, aList=[mp7_5])
mp7_5.set_a([mp7_6])

lSeven.append(mp7_5)
lSeven.extend(mp07_5)
lSeven.append(mp7_6)
lSeven.extend(mpo7_6)

# End Level 7
lSeven.append(lBorderLeft)
lSeven.append(lBorderRight)

lSeven.append(endSign(1160,mpl3_y-40))
levelSeven=Level(lSeven,1040,225,"CaveBackground1.png")

##############################################################
######################## LEVEL 08 ############################
##############################################################
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

##############################################################
######################## LEVEL 09 ############################
##############################################################
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

##############################################################
######################## LEVEL 10 ############################
##############################################################
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
lTen.append(MovePlatDiag(715,676,127,33, 2,1.6,715, 1073, oList=[mpShrub10_2]))
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

##############################################################
######################## LEVEL 11 ############################
##############################################################
lEleven = []
#lEleven.append(Water(0,800,1200,1,BLACK))
lEleven.append(Platform(1026,147,174,33,WHITE))
lEleven.append(Platform(752,243,174,33,WHITE))
lEleven.append(Platform(545,324,205,33,WHITE))
lEleven.append(Platform(224,233,184,33,WHITE))
lEleven.append(Platform(336,266,25,191,WHITE))
lEleven.append(Platform(361,432,185,25,WHITE))
lEleven.append(Platform(0,395,224,33,WHITE))
lEleven.append(Platform(0,604,174,33,WHITE))

# falling platform object
lvl11FallSpike = BlueSpike(429,615)
lvl11FallShrub = SmallRedShrub(281,596)
lvl11FallPlat = FallPlat(278,648,188,33,PURPLE,[lvl11FallSpike,lvl11FallShrub])
lEleven.append(lvl11FallSpike)
lEleven.append(lvl11FallShrub)
lEleven.append(lvl11FallPlat)

lEleven.append(BlueSpike(889,210))
lEleven.append(BlueSpike(752,210))
lEleven.append(BlueSpike(713,291))
lEleven.append(BlueSpike(545,291))

lEleven.append(BlueSpike(509,399))
lEleven.append(BlueSpike(472,399))
lEleven.append(BlueSpike(435,399))
lEleven.append(BlueSpike(398,399))
lEleven.append(BlueSpike(361,399))

lEleven.append(BlueSpike(187,362))
lEleven.append(BlueSpike(37,362))
lEleven.append(BlueSpike(0,362))
lEleven.append(SmallRedShrub(610,272))
lEleven.append(SmallRedShrub(139,343))
lEleven.append(Ladder(375,233))
lEleven.append(Ladder(375,275))

lEleven.append(lBorderLeft)
lEleven.append(lBorderRight)
lEleven.append(endSign(10,564))

levelEleven=Level(lEleven,1125,80,"newlvl-11-12-background.png")

##############################################################
######################## LEVEL 12 ############################
##############################################################
lTwelve = []
#lTwelve.append(Water(0,800,1200,1,BLACK))
lTwelve.append(Platform(1017,604,183,33,WHITE))
lTwelve.append(Platform(652,604,327,33,WHITE))
lTwelve.append(Platform(309,395,174,33,WHITE))
lTwelve.append(Platform(9,662,230,33, WHITE))
lTwelve.append(Platform(14,465,206,33,WHITE))
lTwelve.append(Platform(195,246,25,219,WHITE))
lTwelve.append(Platform(163,416,33,19,WHITE))
lTwelve.append(Platform(0,173,152,33,WHITE))

# falling platform object
lvl12FallSpike = BlueSpike(572,508)
lvl12FallTallShrub = TallRedShrub(609,358)
lvl12FallPlat = FallPlat(483,541,174,33,PURPLE,[lvl12FallSpike,lvl12FallTallShrub])
lTwelve.append(lvl12FallSpike)
lTwelve.append(lvl12FallTallShrub)
lTwelve.append(lvl12FallPlat)

lTwelve.append(BlueSpike(941,571))
lTwelve.append(BlueSpike(652,571))
lTwelve.append(BlueSpike(139,629))
lTwelve.append(BlueSpike(117,432))
lTwelve.append(SmallRedShrub(148,364))
lTwelve.append(Ladder(450,395))
lTwelve.append(Ladder(309,395))
lTwelve.append(Ladder(309,451))
lTwelve.append(Ladder(14,465))
lTwelve.append(Ladder(14,562))
lTwelve.append(Ladder(119,173))
lTwelve.append(Ladder(119,230))

lTwelve.append(lBorderLeft)
lTwelve.append(lBorderRight)
lTwelve.append(endSign(10,133))

levelTwelve=Level(lTwelve,1125,536,"newlvl-11-12-background.png")

##############################################################
######################## LEVEL 13 ############################
##############################################################
lthirteen = []
#lthirteen.append(Water(0,800,1200,1,BLACK))
lthirteen.append(Platform(1061,173,139,33,WHITE))
lthirteen.append(Platform(394,579,67,32,WHITE))
lthirteen.append(Platform(250,611,96,32,WHITE))
lthirteen.append(Platform(46,765,111,32,WHITE))
lthirteen.append(Platform(45,603,111,33,WHITE))
lthirteen.append(Platform(45,472,113,33,WHITE))
lthirteen.append(Platform(152,505,6,131,WHITE))
lthirteen.append(Platform(0,241,138,33,WHITE))

# Moving platform
l13mpShrub = SmallPurpleShrub(724,400) # Moving platform shrub
lthirteen.append(l13mpShrub)
l13mp = MovePlat(668,452,99,26,555,810,[l13mpShrub], [])
lthirteen.append(l13mp)

lthirteen.append(GreenSpike(309,578))
lthirteen.append(GreenSpike(80,732))
lthirteen.append(GreenSpike(48,439))
lthirteen.append(SmallPurpleShrub(377,527))
lthirteen.append(SmallPurpleShrub(100,189))
lthirteen.append(Ladder(49,603))
lthirteen.append(Ladder(100,472))#x 104
lthirteen.append(Ladder(51,324))
lthirteen.append(Ladder(51,241))

lthirteen.append(lBorderLeft)
lthirteen.append(lBorderRight)
lthirteen.append(endSign(2,201))

levelThirteen=Level(lthirteen,1130,93,"newlvl-13-16-background.png")

##############################################################
######################## LEVEL 14 ############################
##############################################################
lFourteen = []
#lFourteen.append(Water(0,800,1200,1,BLACK))
lFourteen.append(Platform(1061,241,139,33,WHITE))
lFourteen.append(Platform(1025,106,67,33,WHITE))
lFourteen.append(Platform(499,425,145,33,WHITE))
lFourteen.append(Platform(0,426,134,33,WHITE))
lFourteen.append(Platform(0,264,101,33,WHITE))
lFourteen.append(Platform(0,128,138,33,WHITE))

lFourteen.append(MovePlatVert(702,347,22,59,228,458,[],[]))

lFourteen.append(FallPlat(945,161,56,33,BEIGE,[]))
lFourteen.append(FallPlat(862,201,56,33,BEIGE,[]))
lFourteen.append(FallPlat(786,334,56,33,BEIGE,[]))
lFourteen.append(FallPlat(303,493,135,33,BEIGE,[]))
lFourteen.append(FallPlat(149,585,135,33,BEIGE,[]))
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

lFourteen.append(GreenSpike(534,393))
lFourteen.append(GreenSpike(499,393))

lFourteen.append(TallPurpleShrub(558,243))
lFourteen.append(SmallPurpleShrub(31,374))
lFourteen.append(SmallPurpleShrub(68,76))

lFourteen.append(lBorderLeft)
lFourteen.append(lBorderRight)
lFourteen.append(endSign(10,88))

levelFourteen=Level(lFourteen,1125,174,"newlvl-13-16-background.png")

##############################################################
######################## LEVEL 15 ############################
##############################################################
lFifteen = []
#lFifteen.append(Water(60,800,1200,1,BLUE))
lFifteen.append(Platform(1124,128,76,33,WHITE))
lFifteen.append(Platform(662,142,82,19,WHITE))
lFifteen.append(Platform(634,250,142,33,WHITE))
lFifteen.append(Platform(454,501,218,15,WHITE))
lFifteen.append(Platform(0,767,48,33,WHITE))#End platform

lFifteen.append(FallPlat(452,429,222,15,BEIGE,[]))
lFifteen.append(GreenSpike(452,467))
lFifteen.append(GreenSpike(489,467))
lFifteen.append(GreenSpike(526,467))
lFifteen.append(GreenSpike(563,467))
lFifteen.append(GreenSpike(600,467))
lFifteen.append(GreenSpike(637,467))

lFifteen.append(FallPlat(795,275,390,33,BEIGE,[]))
lFifteen.append(FallPlat(885,516,74,33,BEIGE,[]))
lFifteen.append(FallPlat(993,622,74,33,BEIGE,[]))
lFifteen.append(FallPlat(885,684,74,33,BEIGE,[]))
lFifteen.append(FallPlat(321,142,302,19,BEIGE,[]))

lFifteen.append(MovePlatVert(310,716,6,139,625,855,[],[]))

l15small1 = SmallPurpleShrub(935,373)
lFifteen.append(l15small1)
l15small2 = SmallPurpleShrub(1051,373)
lFifteen.append(l15small2)
l15mp1 = MovePlat(948,425,139,22,857,1087,[l15small1,l15small2],[])
lFifteen.append(l15mp1)

l15small3 = TallPurpleShrub(754,517)
lFifteen.append(l15small3)
l15mp2 = MovePlat(708,700,139,22,617,847,[l15small3],[])
lFifteen.append(l15mp2)

l15small4 = SmallPurpleShrub(446,701)
lFifteen.append(l15small4)
l15spike1 = GreenSpike(405,720)
lFifteen.append(l15spike1)
l15mp3 = MovePlat(362,753,114,22,367,572,[l15small4,l15spike1],[])
lFifteen.append(l15mp3)

l15small5 = SmallPurpleShrub(185,701)
lFifteen.append(l15small5)
l15spike2 = GreenSpike(144,720)
lFifteen.append(l15spike2)
l15mp4 = MovePlat(145,753,114,22,54,259,[l15small5,l15spike2],[])
lFifteen.append(l15mp4)

lFifteen.append(Ladder(1124,128))
lFifteen.append(Ladder(711,142))
lFifteen.append(Ladder(634,250))
lFifteen.append(Ladder(15,767))#end ladder
lFifteen.append(SmallPurpleShrub(660,90))
lFifteen.append(SmallPurpleShrub(660,198))

lFifteen.append(Platform(247,234,33,10,WHITE))
lFifteen.append(GreenSpike(245,200))

lFifteen.append(Platform(95,328,33,10,WHITE))
lFifteen.append(GreenSpike(93,294))

lFifteen.append(Platform(366,330,33,10,WHITE))
lFifteen.append(GreenSpike(364,296))

lFifteen.append(Platform(24,443,33,10,WHITE))
lFifteen.append(GreenSpike(22,409))

lFifteen.append(Platform(297,514,33,10,WHITE))
lFifteen.append(GreenSpike(295,480))

lFifteen.append(Platform(247,376,33,10,WHITE))
lFifteen.append(GreenSpike(245,342))

lFifteen.append(Platform(192,454,33,10,WHITE))
lFifteen.append(GreenSpike(190,420))

lFifteen.append(Platform(362,605,33,10,WHITE))
lFifteen.append(GreenSpike(360,571))

lFifteen.append(Platform(207,591,33,10,WHITE))
lFifteen.append(GreenSpike(205,557))

lFifteen.append(Platform(63,588,33,10,WHITE))
lFifteen.append(GreenSpike(61,554))

lFifteen.append(lBorderLeft)
lFifteen.append(lBorderRight)
lFifteen.append(endSign(3,727))

levelFifteen=Level(lFifteen,1135,58,"newlvl-13-16-background.png")


##############################################################
######################## LEVEL 16 ############################
##############################################################
lSixteen = []
#lSixteen.append(Water(0,800,1200,1,BLUE))
lSixteen.append(Platform(0,118,440,30,WHITE))

#spike platform 1
lSixteen.append(GreenSpike(422,160))
lSixteen.append(GreenSpike(456,160))
lSixteen.append(GreenSpike(491,160))
lSixteen.append(GreenSpike(525,160))
lSixteen.append(GreenSpike(562,160))
lSixteen.append(GreenSpike(596,160))
lSixteen.append(GreenSpike(631,160))
lSixteen.append(GreenSpike(665,160))
lSixteen.append(Platform(422,193,280,14,WHITE))

#right side falling plats
lSixteen.append(FallPlat(808,302,44,33,BEIGE))
lSixteen.append(FallPlat(906,302,44,33,BEIGE))

lSixteen.append(Platform(974,326,133,33,WHITE))
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

#added in spike wall next to ladders
lSixteen.append(GreenRSpike(700,361))
lSixteen.append(GreenRSpike(700,395))
lSixteen.append(GreenRSpike(700,430))
lSixteen.append(GreenRSpike(700,464))
lSixteen.append(GreenRSpike(700,499))
lSixteen.append(GreenRSpike(700,533))
lSixteen.append(Platform(687,361,14,207,WHITE))

lSixteen.append(Ladder(582,390))
lSixteen.append(Ladder(582,460))
lSixteen.append(Ladder(633,560))
lSixteen.append(Ladder(633,630))
lSixteen.append(Ladder(1024,326))
lSixteen.append(Ladder(1024,396))
lSixteen.append(Ladder(1024,467))
lSixteen.append(Ladder(1024,537))
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
lSixteen.append(GreenRSpike(978,358))
lSixteen.append(GreenRSpike(978,392))
lSixteen.append(GreenRSpike(978,427))
lSixteen.append(GreenRSpike(978,461))
lSixteen.append(GreenRSpike(978,498))
lSixteen.append(GreenRSpike(978,532))
lSixteen.append(GreenRSpike(978,567))
lSixteen.append(GreenLSpike(1070,358))
lSixteen.append(GreenLSpike(1070,392))
lSixteen.append(GreenLSpike(1070,427))
lSixteen.append(GreenLSpike(1070,461))
lSixteen.append(GreenLSpike(1070,498))
lSixteen.append(GreenLSpike(1070,532))
lSixteen.append(GreenLSpike(1070,567))
lSixteen.append(Platform(974,328,14,280,WHITE))
lSixteen.append(Platform(1093,328,14,280,WHITE))
lSixteen.append(TallPinkShrub(446,375))

# mp 1
l16mp1shrub = SmallPinkShrub(685,71)
l16mp1spike = GreenSpike(570,90)
lSixteen.append(l16mp1shrub)
lSixteen.append(l16mp1spike)
l16mp1 = MovePlat(522,118,195,10,494,750,[l16mp1spike,l16mp1shrub],[])
lSixteen.append(l16mp1)

l16mp2shrub1 = SmallPinkShrub(958,131)
l16mp2sp1 = GreenSpike(820,150)
lSixteen.append(l16mp2shrub1)
lSixteen.append(l16mp2sp1)
l16mp2 = MovePlat(811,183,195,22,781,1069,[l16mp2shrub1,l16mp2sp1],[])
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

levelSixteen=Level(lSixteen,0,0,"newlvl-13-16-background.png")

##############################################################
######################## LEVEL 17 ############################
##############################################################
lSeventeen = []
#bottom level
#starting platforms
lSeventeen.append(Platform(1060,634,68,33,WHITE))
lSeventeen.append(Ladder(1090,634))
lSeventeen.append(Platform(1114,741,107,33,WHITE))
#lSeventeen.append(Water(0,800,1200,1,BLUE))
lSeventeen.append(FallPlat(747,694,33,25,BEIGE))
lSeventeen.append(FallPlat(653,711,33,25,BEIGE))
lSeventeen.append(FallPlat(559,711,33,25,BEIGE))
lSeventeen.append(FallPlat(330,719,33,25,BEIGE))
l17mp1 = MovePlat(882,644,42,22,835,1027)
lSeventeen.append(l17mp1)
l17mp2 = MovePlat(456,730,42,22,390,522)
lSeventeen.append(l17mp2)
lSeventeen.append(MovePlatVert(268,680,22,55,625,775))
lSeventeen.append(FallPlat(137,732,106,25,BEIGE))
lSeventeen.append(FallPlat(0,732,106,25,BEIGE))

#middle level
lSeventeen.append(Platform(0,548,68,33,WHITE))
lSeventeen.append(Ladder(36,548))
lSeventeen.append(Ladder(36,633))
lSeventeen.append(Platform(0,350,15,200,WHITE))
l17mp3 = MovePlat(222,500,35,25,93,245)
lSeventeen.append(l17mp3)
lSeventeen.append(Platform(0,327,567,33,WHITE))
lSeventeen.append(FallPlat(288,500,25,25,BEIGE))
lSeventeen.append(FallPlat(356,520,25,25,BEIGE))
lSeventeen.append(FallPlat(411,540,25,25,BEIGE))
lSeventeen.append(FallPlat(473,550,25,25,BEIGE))
lSeventeen.append(FallPlat(531,530,25,25,BEIGE))
lSeventeen.append(Platform(766,484,434,16,WHITE))

# top level

lSeventeen.append(SmallPurpleShrub(1064,432))
lSeventeen.append(SmallPurpleShrub(924,432))
lSeventeen.append(SmallPurpleShrub(774,432))
lSeventeen.append(GreenSpike(837,452))
lSeventeen.append(GreenSpike(871,452))
lSeventeen.append(GreenSpike(984,452))
lSeventeen.append(GreenSpike(1018,452))
lSeventeen.append(Platform(766,282,434,16,WHITE))
lSeventeen.append(FallPlat(1100,224,25,25,BEIGE))
lSeventeen.append(FallPlat(1060,197,25,25,BEIGE))
lSeventeen.append(FallPlat(1015,168,25,25,BEIGE))
lSeventeen.append(FallPlat(840,168,25,25,BEIGE))
lSeventeen.append(Ladder(1140,282))
lSeventeen.append(Ladder(1140,382))
l17mp9 = MovePlat(900,130,35,15,880,990)
lSeventeen.append(l17mp9)


#end platform
lSeventeen.append(Platform(0,256,52,16,WHITE))




l17mp4 = MovePlat(719,492,25,25,617,750)
lSeventeen.append(l17mp4)
l17mp6 = MovePlat(527,261,25,10,453,569)
lSeventeen.append(l17mp6)
l17mp7 = MovePlat(350,275,30,10,316,432)
lSeventeen.append(l17mp7)
l17mp8 = MovePlat(188,269,25,10,174,290)
lSeventeen.append(l17mp8)





#lSeventeen.append(FallPlat(840,300,25,16,BEIGE))

lSeventeen.append(FallPlat(118,277,25,10,BEIGE))
lSeventeen.append(FallPlat(72,270,25,10,BEIGE))

lSeventeen.append(MovePlatVert(684,277,55,20,200,350))
lSeventeen.append(MovePlatVert(600,207,55,20,200,312))

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

lSeventeen.append(GreenSpike(766,249))
lSeventeen.append(GreenSpike(800,249))
lSeventeen.append(GreenSpike(835,249))
lSeventeen.append(GreenSpike(869,249))
lSeventeen.append(GreenSpike(906,249))
lSeventeen.append(GreenSpike(940,249))
lSeventeen.append(GreenSpike(975,249))
lSeventeen.append(GreenSpike(1009,249))
lSeventeen.append(GreenSpike(1045,249))
lSeventeen.append(GreenSpike(1080,249))

# top spikes
lSeventeen.append(GreenDSpike(510,100))
lSeventeen.append(GreenDSpike(544,100))
lSeventeen.append(GreenDSpike(577,100))
lSeventeen.append(GreenDSpike(610,100))
lSeventeen.append(GreenDSpike(643,100))
lSeventeen.append(GreenDSpike(676,100))
lSeventeen.append(GreenDSpike(709,100))
lSeventeen.append(Platform(510,70,236,33,WHITE))

lSeventeen.append(endSign(5,216))
lSeventeen.append(lBorderRight)
lSeventeen.append(lBorderLeft)

#levelSeventeen=Level(lSeventeen,1120,100,"newlvl-17-18-background.png")
levelSeventeen=Level(lSeventeen,1120,650,"newlvl-13-16-background.png")



##############################################################
######################## LEVEL 18 ############################
##############################################################
lEighteen = []
#lEighteen.append(Water(0,800,1200,1,BLUE))

#top left
lEighteen.append(Platform(1129,259,74,16,WHITE))
lEighteen.append(MovePlat(1049,259,30,14,1018,1121))
lEighteen.append(MovePlat(949,259,30,14,898,1000))
lEighteen.append(MovePlatVert(793,251,77,12,100,279))

#roofspikes
lEighteen.append(GreenDSpike(760,0))
lEighteen.append(GreenDSpike(797,0))
lEighteen.append(GreenDSpike(834,0))
lEighteen.append(GreenDSpike(871,0))

#upperplatform right side
lEighteen.append(GreenSpike(780,294))
lEighteen.append(GreenSpike(815,294))
lEighteen.append(GreenSpike(849,294))
lEighteen.append(GreenSpike(886,294))
lEighteen.append(GreenSpike(920,294))
lEighteen.append(GreenSpike(955,294))
lEighteen.append(GreenSpike(989,294))
lEighteen.append(GreenSpike(1023,294))
lEighteen.append(GreenSpike(1060,294))
lEighteen.append(GreenSpike(1094,294))
lEighteen.append(GreenSpike(1129,294))
lEighteen.append(GreenSpike(1163,294))
lEighteen.append(Platform(782,327,418,33,WHITE))

#upper mid divider
lEighteen.append(Platform(747,155,36,205,WHITE))
lEighteen.append(smallShrub(735,103))

#upperplatform left side
lEighteen.append(GreenSpike(501,294))
lEighteen.append(GreenSpike(536,294))
lEighteen.append(GreenSpike(570,294))
lEighteen.append(GreenSpike(607,294))
lEighteen.append(GreenSpike(641,294))
lEighteen.append(GreenSpike(676,294))
lEighteen.append(GreenSpike(710,294))
lEighteen.append(Platform(501,327,246,33,WHITE))

#upper left side
lEighteen.append(MovePlat(663,155,30,14,612,715))
lEighteen.append(MovePlat(555,222,30,14,510,607))
lEighteen.append(smallShrub(431,170))
lEighteen.append(Platform(435,222,40,28,WHITE))
lEighteen.append(FallPlat(346,201,40,25,BEIGE))
lEighteen.append(FallPlat(254,168,40,25,BEIGE))
lEighteen.append(FallPlat(184,123,40,25,BEIGE))

#leftmid platform/spikes
lEighteen.append(GreenSpike(0,488))
lEighteen.append(GreenSpike(36,488))
lEighteen.append(GreenSpike(70,488))
lEighteen.append(GreenSpike(107,488))
lEighteen.append(GreenSpike(141,488))
lEighteen.append(GreenSpike(176,488))
lEighteen.append(GreenSpike(210,488))
lEighteen.append(Platform(0,521,246,33,WHITE))

lEighteen.append(GreenSpike(247,513))
lEighteen.append(GreenSpike(282,513))
lEighteen.append(GreenSpike(316,513))
lEighteen.append(GreenSpike(353,513))
lEighteen.append(GreenSpike(387,513))
lEighteen.append(GreenSpike(422,513))
lEighteen.append(GreenSpike(456,513))
lEighteen.append(Platform(247,543,246,33,WHITE))

#leftmid jumps
lEighteen.append(MovePlat(120,423,64,14,16,235))
lEighteen.append(FallPlat(282,446,40,25,BEIGE))
lEighteen.append(FallPlat(382,481,40,25,BEIGE))
lEighteen.append(Platform(455,478,40,28,WHITE))
lEighteen.append(smallShrub(451,426))

#vert movers
lEighteen.append(MovePlatVert(541,524,77,12,430,545))
lEighteen.append(MovePlatVert(647,486,77,12,430,555))
lEighteen.append(MovePlatVert(737,512,77,12,430,565))
lEighteen.append(MovePlatVert(840,465,77,12,430,550))
lEighteen.append(MovePlatVert(940,512,77,12,430,560))

#below movers plat/spikes
lEighteen.append(GreenSpike(493,566))
lEighteen.append(GreenSpike(528,566))
lEighteen.append(GreenSpike(562,566))
lEighteen.append(GreenSpike(599,566))
lEighteen.append(GreenSpike(633,566))
lEighteen.append(GreenSpike(668,566))
lEighteen.append(GreenSpike(702,566))
lEighteen.append(GreenSpike(739,566))
lEighteen.append(GreenSpike(774,566))
lEighteen.append(GreenSpike(808,566))
lEighteen.append(GreenSpike(845,566))
lEighteen.append(GreenSpike(879,566))
lEighteen.append(GreenSpike(914,566))
lEighteen.append(GreenSpike(948,566))
lEighteen.append(GreenSpike(985,566))
lEighteen.append(GreenSpike(1019,566))
lEighteen.append(GreenDSpike(860,629))
lEighteen.append(GreenDSpike(645,629))
lEighteen.append(Platform(493,596,561,33,WHITE))

#bottom level
lEighteen.append(Platform(1122,722,78,28,WHITE))

lEighteen.append(GreenSpike(962,725))
lEighteen.append(Platform(962,758,37,8,WHITE))

lEighteen.append(GreenSpike(756,722))
lEighteen.append(Platform(756,754,37,8,WHITE))

lEighteen.append(GreenSpike(544,722))
lEighteen.append(Platform(544,755,37,8,WHITE))

lEighteen.append(GreenSpike(128,722))
lEighteen.append(GreenSpike(167,722))
lEighteen.append(GreenSpike(206,722))
lEighteen.append(Platform(128,755,115,8,WHITE))

lEighteen.append(MovePlat(752,766,187,14,128,1187))

lEighteen.append(Platform(0,766,118,34,WHITE))

lEighteen.append(endSign(20,726))
lEighteen.append(lBorderRight)
lEighteen.append(lBorderLeft)
#levelEighteen=Level(lEighteen,1130,400,"newlvl-17-18-background.png")
levelEighteen=Level(lEighteen,1130,185,"newlvl-17-18-background.png")

##############################################################
######################## LEVEL 19 ############################
##############################################################
lNineteen = []

lNineteen.append(Platform(0,0,133,40,WHITE))
lNineteen.append(Platform(717,246,37,154,WHITE))
lNineteen.append(Platform(91,591,1109,15,WHITE))
lNineteen.append(Platform(1082,757,126,43,WHITE))

lNineteen.append(Ladder(50,0))

lNineteen.append(GreenRSpike(0,104))
lNineteen.append(GreenRSpike(0,139))
lNineteen.append(GreenRSpike(0,173))
lNineteen.append(GreenRSpike(0,210))
lNineteen.append(GreenRSpike(0,244))

lNineteen.append(FallPlat(0,300,85,15,BEIGE))
lNineteen.append(FallPlat(116,269,25,17,BEIGE))#moved left from x 121
lNineteen.append(smallShrub(110,217))#moved left from x 115

lNineteen.append(FallPlat(191,289,25,17,BEIGE))
lNineteen.append(FallPlat(262,230,25,17,BEIGE))
lNineteen.append(smallShrub(257,178))

lNineteen.append(FallPlat(331,280,25,17,BEIGE))
lNineteen.append(FallPlat(402,226,25,17,BEIGE))
lNineteen.append(smallShrub(397,174))

lNineteen.append(FallPlat(472,289,25,17,BEIGE))
lNineteen.append(FallPlat(533,260,25,17,BEIGE))
lNineteen.append(smallShrub(524,208))

lNineteen.append(FallPlat(613,272,25,17,BEIGE))
lNineteen.append(FallPlat(683,218,25,17,BEIGE))
lNineteen.append(smallShrub(678,166))

lNineteen.append(GreenSpike(0,320))
lNineteen.append(GreenSpike(37,320))
lNineteen.append(GreenSpike(75,320))
lNineteen.append(GreenSpike(110,320))
lNineteen.append(GreenSpike(145,320))
lNineteen.append(GreenSpike(180,320))
lNineteen.append(GreenSpike(214,320))
lNineteen.append(GreenSpike(251,320))
lNineteen.append(GreenSpike(285,320))
lNineteen.append(GreenSpike(320,320))
lNineteen.append(GreenSpike(354,320))
lNineteen.append(GreenSpike(392,320))
lNineteen.append(GreenSpike(429,320))
lNineteen.append(GreenSpike(466,320))
lNineteen.append(GreenSpike(503,320))
lNineteen.append(GreenSpike(539,320))
lNineteen.append(GreenSpike(576,320))
lNineteen.append(GreenSpike(610,320))
lNineteen.append(GreenSpike(645,320))
lNineteen.append(GreenSpike(681,320))
lNineteen.append(Platform(0,350,717,17,WHITE))
lNineteen.append(GreenSpike(717,213))

lNineteen.append(FallPlat(641,534,25,17,BEIGE))
lNineteen.append(FallPlat(605,520,25,17,BEIGE))
lNineteen.append(FallPlat(527,503,25,17,BEIGE))
lNineteen.append(FallPlat(397,529,25,17,BEIGE))
lNineteen.append(FallPlat(308,520,25,17,BEIGE))
lNineteen.append(FallPlat(224,503,25,17,BEIGE))
lNineteen.append(FallPlat(134,505,25,17,BEIGE))

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


lNineteen.append(GreenRSpike(-5,435))
lNineteen.append(GreenRSpike(-5,470))
lNineteen.append(GreenRSpike(-5,505))
lNineteen.append(GreenRSpike(-5,540))
lNineteen.append(GreenRSpike(-5,575))
lNineteen.append(GreenRSpike(-5,610))

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

sSpike=SmallSpike(352,710)
lNineteen.append(sSpike)
sSpike2=SmallSpike(503,710)
lNineteen.append(sSpike2)
sSpike9=SmallSpike(423,710)
lNineteen.append(sSpike9)
mp6plat1 = Platform(352,662,11,48,ORANGE)
lNineteen.append(mp6plat1)
mp6plat2 = Platform(503,662,11,48,ORANGE)
lNineteen.append(mp6plat2)
lNineteen.append(MovePlatVert(423,662,11,48,620,740,[mp6plat1, mp6plat2,sSpike,sSpike2,sSpike9]))

sSpike3=SmallSpike(583,710)
lNineteen.append(sSpike3)
sSpike4=SmallSpike(731,710)
lNineteen.append(sSpike4)
sSpike8=SmallSpike(657,710)
lNineteen.append(sSpike8)
mp7plat1 = Platform(583,662,11,48,ORANGE)
lNineteen.append(mp7plat1)
mp7plat2 = Platform(731,662,11,48,ORANGE)
lNineteen.append(mp7plat2)
lNineteen.append(MovePlatVert(657,662,11,48,620,740,[mp7plat1, mp7plat2,sSpike3,sSpike4,sSpike8]))

sSpike5=SmallSpike(884,710)
lNineteen.append(sSpike5)
sSpike6=SmallSpike(1035,710)
lNineteen.append(sSpike6)
sSpike7=SmallSpike(955,710)
lNineteen.append(sSpike7)
mp8plat1 = Platform(884,662,11,48,ORANGE)
lNineteen.append(mp8plat1)
mp8plat2 = Platform(1035,662,11,48,ORANGE)
lNineteen.append(mp8plat2)
lNineteen.append(MovePlatVert(955,662,11,48,620,740,[mp8plat1, mp8plat2,sSpike5,sSpike6,sSpike7]))
lNineteen.append(Platform(1190,0,10,591,WHITE))#fixes bug with right level border

lNineteen.append(endSign(1150,716))
lNineteen.append(lBorderRight)
lNineteen.append(lBorderLeft)
levelNineteen=Level(lNineteen,35,65,"newlvl-19-background.png")



##############################################################
######################## LEVEL 20 ############################
##############################################################
lTwenty = []

#lTwenty.append(Water(0,780,1200,40,BLUE))
lTwenty.append(Platform(0,757,120,43,WHITE))
lTwenty.append(Platform(598,645,311,22,WHITE))
lTwenty.append(Platform(598,432,311,22,WHITE))
lTwenty.append(Platform(973,637,218,22,WHITE))


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

#lTwenty.append(FallPlat(536,183,10,10,BEIGE))
lTwenty.append(FallPlat(586,161,10,10,BEIGE))
#lTwenty.append(FallPlat(661,157,10,10,BEIGE))
lTwenty.append(FallPlat(715,179,10,10,BEIGE))
#lTwenty.append(FallPlat(777,198,10,10,BEIGE))
#lTwenty.append(FallPlat(823,183,10,10,BEIGE))
lTwenty.append(FallPlat(864,167,10,10,BEIGE))
#lTwenty.append(FallPlat(930,196,10,10,BEIGE))
#lTwenty.append(FallPlat(970,238,10,10,BEIGE))
#lTwenty.append(FallPlat(1019,238,10,10,BEIGE))


lTwenty.append(Ladder(191,303))

lTwenty.append(smallShrub(261,595))
lTwenty.append(smallShrub(436,575))
lTwenty.append(smallShrub(850,593))
lTwenty.append(smallShrub(973,585))

lTwenty.append(smallShrub(730,593))


lTwenty.append(TallShrub(878,249))


lTwenty.append(GreenSpike(633,400))

lTwenty.append(GreenLSpike(1049,187))

#sideplatform
lTwenty.append(GreenSpike(1010,437))
lTwenty.append(GreenDSpike(973,487))
lTwenty.append(Platform(973,470,218,22,WHITE))
lTwenty.append(Ladder(1063,470))

#left lower platform
lTwenty.append(TallShrub(501,280))
lTwenty.append(GreenSpike(230,430))
lTwenty.append(GreenSpike(340,430))
lTwenty.append(GreenSpike(450,430))
lTwenty.append(smallShrub(375,410))
lTwenty.append(smallShrub(265,410))
lTwenty.append(Platform(184,461,365,22,WHITE))


l20mp1plat1 = Platform(664,534,37,29,ORANGE)#This shortcut is nice, but only fine if the player never stands on this moving platform
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

#l20mp3p1 = Platform(240,198,37,29,ORANGE)
#lTwenty.append(l20mp3p1)
l20mp3sp1 = GreenDSpike(240,227)
lTwenty.append(l20mp3sp1)
l20mp3sp2 = GreenDSpike(322,198)
lTwenty.append(l20mp3sp2)
l20mp3sh1 = smallShrub(234,146)
l20mp5p= MovePlatVert(240,198,37,29,93,213,[l20mp3sh1,l20mp3sp1])
lTwenty.append(l20mp5p)

lTwenty.append(l20mp3sh1)
l20mp3sh2 = smallShrub(316,117)
lTwenty.append(l20mp3sh2)
l20mp3 = MovePlatVert(322,169,37,29,93,213,[l20mp3sp2,l20mp3sh2])
lTwenty.append(l20mp3)

l20mp4sp1 = GreenSpike(402,146)
lTwenty.append(l20mp4sp1)
l20mp4sp2 = GreenDSpike(402,207)
lTwenty.append(l20mp4sp2)
l20mp4 = MovePlatVert(402,179,37,29,131,250,[l20mp4sp1,l20mp4sp2])
lTwenty.append(l20mp4)

lTwenty.append(goldShears(1150,147))
lTwenty.append(lBorderRight)
lTwenty.append(lBorderLeft)

# levelTwenty=Level(lTwenty,1120,5,"newlvl-20-background.png")
levelTwenty=Level(lTwenty,15,650,"newlvl-20-background.png")#Starting 15,650

# takes level list and replaces sign location with new (x,y)
def moveSigns(levelList, x, y):
    for i in range(len(levelList)):
        if type(levelList[i]) == endSign:
            levelList[i] = endSign(x, y)
    return levelList

lOne = moveSigns(lOne, -40,584)
lTwo = moveSigns(lTwo, -40,509)
lThree = moveSigns(lThree, 145,-40)
lFour = moveSigns(lFour, 20,-40)
lFive = moveSigns(lFive, 1200,74)

lSix = moveSigns(lSix, 1086,800)
lSix.append(Platform(884,770,194,30,WHITE))
lSix.append(BlackSpike(884, 737))
lSix.append(BlackSpike(922, 737))
lSix.append(BlackSpike(960, 737))
lSix.append(BlackSpike(998, 737))

lSeven = moveSigns(lSeven, 1200,mpl3_y-40)
lEight = moveSigns(lEight, 945,-40)
lNine = moveSigns(lNine, 22,-75)
lTen = moveSigns(lTen, -40,107)
lEleven = moveSigns(lEleven, -40,564)
lTwelve = moveSigns(lTwelve, -40,133)
lthirteen = moveSigns(lthirteen, -40,201)
lFourteen = moveSigns(lFourteen, -40,88)
lFifteen = moveSigns(lFifteen, 20,800)#ChangeThisOne
lSixteen = moveSigns(lSixteen, -40,700)
lSeventeen = moveSigns(lSeventeen, -40,190)
lEighteen = moveSigns(lEighteen, -40,726)
lNineteen = moveSigns(lNineteen, 1200,716)
#lTwenty = moveSigns(lTwenty, 1200,147)

lOne.append(lBorderRight)
lOne.append(lBorderLeft)
lTwo.append(lBorderRight)
lTwo.append(lBorderLeft)
lThree.append(lBorderRight)
lThree.append(lBorderLeft)
lFour.append(lBorderRight)
lFour.append(lBorderLeft)
lFive.append(lBorderRight)
lFive.append(lBorderLeft)
lFive.append(lBorderRight)
lSix.append(lBorderLeft)
lSix.append(lBorderRight)
lSeven.append(lBorderLeft)
lSeven.append(lBorderRight)
lEight.append(lBorderLeft)
lEight.append(lBorderRight)
lNine.append(lBorderLeft)
lNine.append(lBorderRight)
lTen.append(lBorderLeft)
lTen.append(lBorderRight)
lEleven.append(lBorderLeft)
lEleven.append(lBorderRight)
lTwelve.append(lBorderLeft)
lTwelve.append(lBorderRight)
lthirteen.append(lBorderLeft)
lthirteen.append(lBorderRight)
lFourteen.append(lBorderLeft)
lFourteen.append(lBorderRight)
lFifteen.append(lBorderLeft)
lFifteen.append(lBorderRight)
lSixteen.append(lBorderLeft)
lSixteen.append(lBorderRight)
lSeventeen.append(lBorderLeft)
lSeventeen.append(lBorderRight)
lEighteen.append(lBorderLeft)
lEighteen.append(lBorderRight)
lNineteen.append(lBorderLeft)
lNineteen.append(lBorderRight)



cOne=Level(lOne,1135,639,"Level 1 to 3 bkgrnd.png")#Comp Level One, uses same object list(Changed background path to remove tutorial)
cTwo=Level(lTwo,1135,538,"Level 1 to 3 bkgrnd.png")
cThree=Level(lThree,1100,470,"Level 1 to 3 bkgrnd.png")
cFour=Level(lFour,1100,635,"CaveBackground1.png")
cFive=Level(lFive,50,625,"CaveBackground1.png")
cSix=Level(lSix,25,50,"CaveBackground1.png")
cSeven=Level(lSeven,1050,15,"CaveBackground1.png")
cEight=Level(lEight,70,590,"mysticalBackground.png")
cNine=Level(lNine,918,685,"mysticalBackground.png")
cTen=Level(lTen,10,630,"mysticalBackground.png")
cEleven=Level(lEleven,1125,80,"newlvl-11-12-background.png")
cTwelve=Level(lTwelve,1125,536,"newlvl-11-12-background.png")
cThirteen=Level(lthirteen,1130,93,"newlvl-13-16-background.png")
cFourteen=Level(lFourteen,1125,174,"newlvl-13-16-background.png")
cFifteen=Level(lFifteen,1135,58,"newlvl-13-16-background.png")
cSixteen=Level(lSixteen,0,0,"newlvl-13-16-background.png")
cSeventeen=Level(lSeventeen,1120,650,"newlvl-13-16-background.png")
cEighteen=Level(lEighteen,1130,185,"newlvl-17-18-background.png")
cNineteen=Level(lNineteen,35,65,"newlvl-19-background.png")
cTwenty=Level(lTwenty,5,690,"newlvl-20-background.png")
cOne.is_comp=True
cOne.next_level=cTwo
cTwo.is_comp=True
cTwo.next_level=cThree
cThree.is_comp=True
cThree.next_level=cFour
cFour.is_comp=True
cFour.next_level=cFive
cFive.is_comp=True
cFive.next_level=cSix
cSix.is_comp=True
cSix.next_level=cSeven
cSeven.is_comp=True
cSeven.next_level=cEight
cEight.is_comp=True
cEight.next_level=cNine
cNine.is_comp=True
cNine.next_level=cTen
cTen.is_comp=True
cTen.next_level=cEleven
cEleven.is_comp=True
cEleven.next_level=cTwelve
cTwelve.is_comp=True
cTwelve.next_level=cThirteen
cThirteen.is_comp=True
cThirteen.next_level=cFourteen
cFourteen.is_comp=True
cFourteen.next_level=cFifteen
cFifteen.is_comp=True
cFifteen.next_level=cSixteen
cSixteen.is_comp=True
cSixteen.next_level=cSeventeen
cSeventeen.is_comp=True
cSeventeen.next_level=cEighteen
cEighteen.is_comp=True
cEighteen.next_level=cNineteen
cNineteen.is_comp=True
cNineteen.next_level=cTwenty
cTwenty.is_comp=True


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
    if not level.is_comp:
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
            #pygame.display.set_mode(full)
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
    sys.exit()

def testConnection():
    global servers
    if len(servers) == 0:
        servers = ['time.nist.gov', 'time.google.com', 'time.windows.com', 'pool.ntp.org', 'north-america.pool.ntp.org']
    server_copy = servers.copy()

    for server in servers:
        try:
            ntplib.NTPClient().request(server)
            servers = server_copy
            return True
        except:
            server_copy.remove(server)
    return False

if __name__ == "__main__":
    hertz_ee = False
    if os.path.exists("competitive.txt"):
        display_competitive_main_menu(window)
    else:
        display_main_menu(window)
