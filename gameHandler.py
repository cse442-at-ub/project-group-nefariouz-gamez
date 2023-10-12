# environment setup taken from freeCodeCamp.org on Youtube: https://www.youtube.com/watch?v=6gLeplbqtqg
# basis for player movement/collision, background setup from same source
import os
import random
import math
import pygame

from gameObjects import Object, Platform, Block, smallShrub, TallShrub, Spike, Water, FallPlat, Ladder
from playerObject import Player

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

window = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)

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
            if(object.name=="spike"):
                player.reset(level)
            if dy > 0 and object.name!="ladder" and not player.on_ladder:
                player.rect.bottom = object.rect.top
                player.landed()
            elif dy < 0 and object.name!="ladder" and not player.on_ladder:
                #player.rect.top = object.rect.bottom
                player.rect.y+=2
                player.y_vel=-PLAYER_VEL*2
                #player.rect.y=player.rect.y+5
                print("BONK?")
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
        if keys[pygame.K_w]:
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
        
        if keys[pygame.K_w]:
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
levelTwo=Level(lTwo,1135,655,"Level 1 to 3 bkgrnd.png")

GRAY=(192,192,192)
lThree=[]
#Player Starting position (1100,559)
lThree.append(Platform(1096,599,57,176,BROWN))#POST 1
lThree.append(Platform(975,599,57,176,BROWN))#POST 2
lThree.append(Platform(643,573,57,176,BROWN))#POST 3
lThree.append(Platform(330,523,57,237,BROWN))#POST 4
lThree.append(Platform(0,0,131,800,GRAY))#MOUNTAINSIDE
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
levelThree=Level(lThree,1100,559,"Level 1 to 3 bkgrnd.png")

lFour=[]
#background,bg_image = get_background("CaveBackground1.png")


def main(window, level):
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
        getInput(playerOne,level)
        draw(window, background, bg_image,playerOne,level)
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window,levelOne)