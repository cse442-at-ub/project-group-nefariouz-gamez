# environment setup taken from freeCodeCamp.org on Youtube: https://www.youtube.com/watch?v=6gLeplbqtqg
# basis for player movement/collision, background setup from same source
import os
import random
import math
import pygame
import sys

from gameObjects import Object, Platform, Block, smallShrub, TallShrub, Spike, Water, FallPlat, Ladder, endSign, BlackSpike, SideSpike, ReverseSmallShrub, Void
from MenuWidgets import *

from os import listdir
from os.path import isfile, join
#from pygame.sprite import _Group

pygame.init()

pygame.display.set_caption("Shrubbery Quest")
GRAVITY=1#Rate at which objects and players fall
WIDTH, HEIGHT = 1200, 800 #Exact size of figma levels, 1-1 for design purposes
FPS = 60
PLAYER_VEL=5 #Player Movement speed
WHITE=(255,255,255)
PURPLE=(128,0,128)
ENDLEVEL = False

window = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)

##############################################################
##############################################################
###################### PLAYER OBJECT #########################
##############################################################
##############################################################

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

    # would actually read this value from file/however we end up doing it
    SPRITES = load_sprite_sheets("Characters", "Celia", 32, 32, True)
    ANIMATION_DELAY = 3
    GRAVITY = 1

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.xO=x#For respawning purposes
        self.yO=y
        self.x_velocity, self.y_velocity = 0, 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.inair=False
        self.on_ladder=False
        self.e_timer=0

        self.reachBox=Platform(x-15,y-15,width*2.5,height*1.2,WHITE)#Invisible bounding box for interacting with objects
        self.reachBox.surface=pygame.Surface((width*3,height*1.5))
        self.reachBox.mask = pygame.mask.from_surface(self.reachBox.surface)


    def reset(self,level):
        self.rect.x=self.xO
        self.rect.y=self.yO
        level.reset()


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.reachBox.rect.x=self.rect.x-15
        self.reachBox.rect.y=self.rect.y-15

    def move_left(self, velocity):
        self.x_velocity = -velocity
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, velocity):
        self.x_velocity = velocity
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    def move_up(self, velocity):
        self.y_velocity=-velocity
    def move_down(self, velocity):
        self.y_velocity=velocity
    # does not allow double jump
    def jump(self):
        self.inair=True#anti=double jump
        self.y_velocity = -self.GRAVITY * 4.5
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def landed(self):
        self.inair=False
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

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.y_velocity < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_velocity > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_velocity != 0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
    
    def loop(self, fps):
        # gravity
        if self.e_timer!=0:
            self.e_timer-=1
        if not self.on_ladder:#only apply gravity when not on ladder
            self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()
 
    def draw(self, window, offset_x):
        #self.reachBox.draw(window,0)------------VISUALISE reachBox
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

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
    loadLevel(window, levelOne)
    print("BEGIN YOUR QUEST")

def load_level():
    # Loads level based on what current level you're on in
    lvlfile = open("currentLevel.txt", "r")
    currlvl = lvlfile.read()
    if currlvl == "2":
        loadLevel(window, levelTwo)
    elif currlvl == "3":
        loadLevel(window, levelThree)
    elif currlvl == "4":
        loadLevel(window, levelFour)
    elif currlvl == "5":
        loadLevel(window, levelFive)
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
######################## SETTINGS ############################
##############################################################
##############################################################

def scale_window_settings(screen):
    screen_width, screen_height = screen.get_size()   # find screen dimensions

    background_img = pygame.image.load("assets\Background\BetLvlBackground.png")
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
    window.blit(img, centered_pos)

def tutorial():
    print("TUTORIAL")

def choose_character():
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
    if currlvl == "2":
        loadLevel(window, levelTwo)
    elif currlvl == "3":
        loadLevel(window, levelThree)
    elif currlvl == "4":
        loadLevel(window, levelFour)
    elif currlvl == "5":
        loadLevel(window, levelFive)
    print("CONTINUE")


def display_between_level_page(screen):
    widgets, screen_width, screen_height, background_img = scale_window_between(screen)

    #get level num
    lvlf = open("currentLevel.txt", "r")
    currlvl = lvlf.read()
    printlvl = str(int(currlvl) - 1)
    lvlf.close()

    timef = open("levelTime.txt", "r")
    currtime = timef.read()
    timef.close()

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

        #draw text
        screen.blit(background_img, (0,0))
        draw_text("Congratulations!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-190))
        draw_text("You Beat Level " + printlvl + "!", pygame.font.Font(None, 72),(34, 90, 48), ((screen_width/2), (screen_height/2)-130))
        draw_text("Your Time Was: " + currtime, pygame.font.Font(None, 48),(34, 90, 48), ((screen_width/2), (screen_height/2)-70))
        
        #input buttons
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
    def loop(self):
        for object in self.object_list:
            if object.name=="fall":
                object.check_time()

def draw(window, background, bg_image,player,level):
    for tile in background:
        window.blit(bg_image, tile)

    for object in level.object_list:
        object.draw(window,0)

    player.draw(window,0)

    pygame.display.update()
    

def handle_vertical_collision(player, level, dy):
    collided_objects = []
    for object in level.object_list:
        if pygame.sprite.collide_mask(player, object):
            if(object.name=="fall"):
                object.timer+=1
            if(object.name=="spike"):
                player.reset(level)
            if dy > 0 and object.name!="ladder" and not player.on_ladder:
                player.rect.bottom = object.rect.top
                if(object.name=="fall"):
                    object.timer+=1
                    object.check_time()
                player.landed()
            elif dy < 0 and object.name!="ladder" and not player.on_ladder:
                #player.rect.top = object.rect.bottom
                player.rect.y+=2
                player.y_vel=-PLAYER_VEL*2
                #player.rect.y=player.rect.y+5
                player.hit_head()

            collided_objects.append(object)
    
    return collided_objects

def collide(player, level, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for object in level.object_list:
        if pygame.sprite.collide_mask(player, object) and object.name!="ladder":
            collided_object = object
            if(collided_object.name=="spike"):
                player.reset(level)
            if(collided_object.name == "end sign"):
                #PLAYER HAS REACHED END OF LEVEL
                # ADD ONE TO COMPLETED LEVELS
                #ENDLEVEL = True
                lvlf = open("currentLevel.txt", "r")
                levelnum = int(lvlf.read())
                levelnum += 1
                lvlf = open("currentLevel.txt", "w")
                lvlf.write(str(levelnum))
                lvlf.close()
                # THEN OPEN BETWEEN LEVEL MENU
                display_between_level_page(window)
                print("END LEVEL")
            break
    
    player.move(-dx, 0)
    
    player.x_vel=0
    player.update()
    return collided_object

def getOverlap(player, reachBox, level):
    for object in level.object_list:
        if pygame.sprite.collide_mask(reachBox,object):
            if object.name=="ladder":
                #Handle Ladder behavior
                if player.on_ladder:
                    player.on_ladder=False
                player.y_velocity=0#stop all y movement
                player.x_velocity=0#stop all x movement
                player.on_ladder=True
                player.rect.x=object.xO-15#set x value to Ladder x Valued
                player.rect.y=player.rect.y+1#Make the masks overlap. If you grab the bottom 1 pixel of a ladder irl, you're falling
                return#only do 1 interact at a time
            if object.name=="small shrub":
                #Handle small shrub behavior
                object.destroy()
                return
            if object.name=="tall shrub":
                #Handle tall shrub behavior
                object.destroy()
                return
            
def getInput(player, level):
    keys=pygame.key.get_pressed()
    collide_left = collide(player, level, -PLAYER_VEL*2)
    collide_right = collide(player, level, PLAYER_VEL*2)
    if player.on_ladder:
        player.y_velocity=0
        if keys[pygame.K_w]or keys[pygame.K_SPACE]:
            g=0
            #Move up on ladder
            #check if still on ladder
            player.move_up(PLAYER_VEL)
            for object in level.object_list:
                if pygame.sprite.collide_mask(player.reachBox,object):
                    if object.name=="ladder":
                        g=1
            if g==0:
                player.on_ladder=False
        if keys[pygame.K_s]:
            #Move down on ladder
            #check if still on ladder
            g=0
            player.move_down(PLAYER_VEL)
            for object in level.object_list:
                if pygame.sprite.collide_mask(player,object):
                    if object.name=="ladder":
                        g=1
            if g==0:
                player.on_ladder=False
        if keys[pygame.K_a] and not collide_left:
            player.on_ladder=False
            player.move_left(PLAYER_VEL)

        if keys[pygame.K_d] and not collide_right:
            player.move_right(PLAYER_VEL)
            
        if keys[pygame.K_e]:
            if player.e_timer==0:
                player.e_timer=8
                getOverlap(player,player.reachBox,level)
        if keys[pygame.K_q]:
            x=0#placeholder
            
    if not player.on_ladder:
        player.x_velocity=0 #Reset
        
        if keys[pygame.K_w]or keys[pygame.K_SPACE]:
            if player.inair==False:
                player.jump()
        if keys[pygame.K_a] and not collide_left:
            player.move_left(PLAYER_VEL)
        if keys[pygame.K_d] and not collide_right:
            player.move_right(PLAYER_VEL)
        if keys[pygame.K_e]:
            if player.e_timer==0:
                player.e_timer=8
                getOverlap(player,player.reachBox,level)
        if keys[pygame.K_q]:
            x=0#placeholder
        if keys[pygame.K_ESCAPE]:
            x=0#Placeholder for pause
    
    vertical_collide = handle_vertical_collision(player, level, player.y_velocity)
    


lOne=[]
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
levelOne=Level(lOne,1135,644,"Level 1 to 3 bkgrnd.png")

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
lTwo.append(endlvl2)
levelTwo=Level(lTwo,1135,655,"Level 1 to 3 bkgrnd.png")

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
lThree.append(Platform(131,420,65,15,WHITE))#PLAT 3
lThree.append(Platform(131,103,200,23,WHITE))#PLAT 4
lThree.append(TallShrub(587,340))#TALLSHRUB 1
lThree.append(Ladder(255,229))#LADDER 1
lThree.append(Ladder(255,103))#LADDER 2
lThree.append(Ladder(255,201))#LADDER 3
lThree.append(Ladder(145,0))#LADDER 4
lThree.append(endSign(180,63)) # END SIGN
levelThree=Level(lThree,1100,559,"Level 1 to 3 bkgrnd.png")

lFour=[]
#Player starting position (1100, 644)
#background,bg_image = get_background("CaveBackground1.png")
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
lFour.append(Platform(960,720,244,80,WHITE))
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
lFour.append(FallPlat(620,495,257,30))#Third platform
lFour.append(FallPlat(223,435,257,15))#Fourth platform
lFour.append(Platform(0,116,200,80,WHITE))
lFour.append(Ladder(108,286))
lFour.append(Ladder(108,216))
lFour.append(Platform(0,118,200,80,WHITE))
lFour.append(Ladder(108,116))
lFour.append(Ladder(23,0))
lFour.append(endSign(23,76)) # END SIGN
levelFour=Level(lFour,1100,700,"CaveBackground1.png")

lFive=[]
lFive.append(Void(85,785,1115,15))
lFive.append(Platform(0,700,200,80,WHITE))
lFive.append(Ladder(21,700))
lFive.append(FallPlat(298,649,200,51))
lFive.append(Platform(600, 598, 200, 51,WHITE))
lFive.append(Platform(889,573,200,51,WHITE))
lFive.append(Platform(889,373,200,51,WHITE))
lFive.append(Ladder(1011,373))
lFive.append(Ladder(1011, 473))
lFive.append(Platform(600,432,200,51,WHITE))
lFive.append(ReverseSmallShrub(750,483))
lFive.append(TallShrub(752,249))
lFive.append(FallPlat(298,384,200,51))
lFive.append(Platform(56,190,200,51,WHITE))
lFive.append(Ladder(215,190))
lFive.append(Ladder(215,204))
fpShrub1=smallShrub(345,91)
fpShrub2=smallShrub(404,91)
fallGroupFive1=[fpShrub1,fpShrub2]
fiveFPlat1=FallPlat(298,143,200,51,PURPLE,fallGroupFive1)
lFive.append(fpShrub1)
lFive.append(fpShrub2)
lFive.append(fiveFPlat1)

fpShrub3=smallShrub(652,91)
fpShrub4=smallShrub(704,91)
fallGroupFive2=[fpShrub3,fpShrub4]
fiveFPlat2=FallPlat(597,143,200,51,PURPLE,fallGroupFive2)
lFive.append(fpShrub3)
lFive.append(fpShrub4)
lFive.append(fiveFPlat2)

fpShrub5=smallShrub(948,91)
fpShrub6=smallShrub(1003,91)
fallGroupFive3=[fpShrub5,fpShrub6]
fiveFPlat3=FallPlat(889,143,200,51,PURPLE,fallGroupFive3)
lFive.append(fpShrub5)
lFive.append(fpShrub6)
lFive.append(fiveFPlat3)

lFive.append(Platform(1097,114,103,58,WHITE))
lFive.append(endSign(1140,74)) # END SIGN

levelFive=Level(lFive,50,750,"CaveBackground1.png")

def loadLevel(window, level):
    clock = pygame.time.Clock()
    background=level.background
    bg_image=level.bg_image
    playerOne=Player(level.init_x,level.init_y,30,64)
    
    
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        playerOne.loop(FPS)
        level.loop()
        getInput(playerOne,level)
        draw(window, background, bg_image,playerOne,level)
    pygame.quit()
    quit()

if __name__ == "__main__":
    display_main_menu(window)