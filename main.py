# environment setup taken from freeCodeCamp.org on Youtube: https://www.youtube.com/watch?v=6gLeplbqtqg
# basis for player movement/collision, background setup from same source

import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
#from pygame.sprite import _Group

pygame.init()

pygame.display.set_caption("Shrubbery Quest")
GRAVITY=1#Rate at which objects and players fall
WIDTH, HEIGHT = 1200, 800 #Exact size of figma levels, 1-1 for design purposes
FPS = 60
PLAYER_VEL=4 #Player Movement speed


window = pygame.display.set_mode((WIDTH, HEIGHT))

class Player(pygame.sprite.Sprite):
    COLOR=(0,255,0)
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x,y,w,h)
        self.x_pos=x
        self.y_pos=y
        self.inair=False
        self.x_vel=0
        self.y_vel=0
        self.air_time=0
        self.mask=None

    def move(self, dx, dy):
        self.rect.x +=dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel= -vel
        #Futue: Handle direction change
    def move_right(self, vel):
        self.x_vel= vel
        #Future: Handle direction change

    def loop(self, fps):
        self.y_vel+=min(1,(self.air_time/fps)*GRAVITY)
        self.move(self.x_vel,self.y_vel)
        self.air_time+=1

    def landed(self):
        self.air_time = 0
        self.y_vel = 0
        self.inair=False

    def hit_head(self):
        self.count = 0
        self.y_vel = 0

    def jump(self):
        self.y_vel=-GRAVITY*10
        self.inair=True

    def draw(self, win):
        pygame.draw.rect(win,self.COLOR, self.rect)

def get_background(name):
    image = pygame.image.load(join("Backgrounds",name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width+1):
        for j in range(HEIGHT // height+1):
            pos = (i * width+1, j * height+1)
            tiles.append(pos)
    return tiles, image

class Object(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h,ipath):
        self.rect=pygame.Rect(x,y,w,h)
        self.x_pos=x
        self.y_pos=y
        self.width=w
        self.height=h
        self.x_vel=0
        self.y_vel=0
        self.image=pygame.image.load(join("Blocks",ipath))#Get the image file
        _,_,iwidth,iheight= self.image.get_rect()
        self.tiles=[]
        for i in range(self.width // iwidth+1):#Get image to cover entire size
            for j in range(self.height // iheight+1):
                pos = (i * iwidth+1, j * iheight+1)
                self.tiles.append(pos)
    def draw(self, win):
        for tile in self.tiles:
            x,y=tile
            win.blit(self.image,(x+self.x_pos,y+self.y_pos))
        


def draw(window, background, bg_image,player,objects):
    for tile in background:
        window.blit(bg_image, tile)
    
    player.draw(window)

    for object in objects:
        object.draw(window)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_rect(player,obj):#Collide mask?
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects


def getInput(player, objects):
    keys=pygame.key.get_pressed()
    player.x_vel=0 #Reset
    if keys[pygame.K_w]:
        if player.inair==False:
            player.jump()
    if keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VEL)
    handle_vertical_collision(player,objects,player.y_vel)

def main(window):
    clock = pygame.time.Clock()
    background,bg_image = get_background("Level 1 to 3 bkgrnd.png")
    playerOne=Player(100,100,30,64)

    objects=[]
    start=Object(890,645,152,75,"LogPlatform.png")
    base=Object(0,720,1200,80,"LogPlatform.png")
    plat2=Object(502,645,264,75,"LogPlatform.png")
    plat3=Object(0,624,361,96,"LogPlatform.png")
    objects.append(start)
    objects.append(base)
    objects.append(plat2)
    objects.append(plat3)

    
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        playerOne.loop(FPS)
        getInput(playerOne,objects)
        draw(window, background, bg_image,playerOne,objects)
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)