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
PLAYER_VEL=5 #Player Movement speed
WHITE=(255,255,255)


window = pygame.display.set_mode((WIDTH, HEIGHT))
def flip_image(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(directory1, directory2, width, height, direction=False):
    path = join("assets", directory1, directory2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
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

def get_block(size,ipath):#added path so it's not always terrain.png
    path = join("assets",  "Terrain", ipath)
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)

    return pygame.transform.scale2x(surface)

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

        self.reachBox=Platform(x-15,y-15,width*3,height*1.5,WHITE)#Invisible bounding box for interacting with objects
        self.reachBox.surface=pygame.Surface((width*3,height*1.5))
        self.reachBox.mask = pygame.mask.from_surface(self.reachBox.surface)


    def reset(self):
        self.rect.x=self.xO
        self.rect.y=self.yO


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
        self.y_velocity = -self.GRAVITY * 5
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

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, path=None,name=None):
        super().__init__()
        self.ipath=path
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width, self.height, self.name = width, height, name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))
    
class Platform(Object):
    def __init__(self, x, y, width, height,col, path=None, name=None):
        super().__init__(x, y, width, height, path, name)
        self.color=col
        self.surface=pygame.Surface((width,height))
        self.surface.fill(self.color)
        self.mask = pygame.mask.from_surface(self.surface)
    def draw(self, window,offset_x):
        pygame.draw.rect(window,self.color,self.rect)

class Block(Object):
    def __init__(self, x, y, size,path):
        super().__init__(x, y, size, size,path)
        block = get_block(size,path)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class smallShrub(Object):
    def __init__(self,x,y):
        super().__init__(x,y,48,52)
        self.name="small shrub"
        self.image=pygame.image.load("assets\Traps\SmallShrub\SmallShrub.png")
        self.mask=pygame.mask.from_surface(self.image)

    def destroy(self):
        self.image=pygame.image.load("assets\Traps\Empty\empty.png")
        self.mask=pygame.mask.from_surface(self.image)

class TallShrub(Object):
    def __init__(self,x,y):
        super().__init__(x,y,48,183)
        self.name="tall shrub"
        self.image=pygame.image.load("assets\Traps\TallShrub\TallShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.health=50
    def destroy(self):
        if self.health==1:
            self.image=pygame.image.load("assets\Traps\Empty\empty.png")
            self.mask=pygame.mask.from_surface(self.image)
        if self.health!=1:
            self.health-=1

class Spike(Object):
    def __init__(self,x,y):
        super().__init__(x,y,40,34)
        self.name="spike"
        self.image=pygame.image.load("assets\Traps\Spikes\Spike.png")
        self.mask=pygame.mask.from_surface(self.image)

class Water(Platform):
    def __init__(self, x, y, width, height, col, path=None, name="spike"):
        super().__init__(x, y, width, height, col, path, name)

class Ladder(Object):
    def __init__(self,x,y):
        super().__init__(x,y,33,100)
        self.name="ladder"
        self.xO=x
        self.image=pygame.image.load("assets\Special\Ladder.png")
        self.mask=pygame.mask.from_surface(self.image)


def draw(window, background, bg_image,player,objects):
    for tile in background:
        window.blit(bg_image, tile)
    
    

    for object in objects:
        
        object.draw(window,0)

    player.draw(window,0)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            if(object.name=="spike"):
                player.reset()
            if dy > 0 and object.name!="ladder":
                player.rect.bottom = object.rect.top
                player.landed()
            elif dy < 0 and object.name!="ladder" and not player.on_ladder:
                player.rect.top = object.rect.bottom
                player.hit_head()

            collided_objects.append(object)
    
    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for object in objects:
        if pygame.sprite.collide_mask(player, object) and object.name!="ladder":
            collided_object = object
            if(collided_object.name=="spike"):
                player.reset()
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object

def getOverlap(player, reachBox, objects):
    for object in objects:
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
            


def getInput(player, objects):
    keys=pygame.key.get_pressed()
    collide_left = collide(player, objects, -PLAYER_VEL*2)
    collide_right = collide(player, objects, PLAYER_VEL*2)
    if player.on_ladder:
        player.y_velocity=0
        if keys[pygame.K_w]:
            g=0
            #Move up on ladder
            #check if still on ladder
            player.move_up(PLAYER_VEL)
            for object in objects:
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
            for object in objects:
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
            getOverlap(player,player.reachBox,objects)
            
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
            getOverlap(player,player.reachBox,objects)
        if keys[pygame.K_q]:
            x=0#placeholder
    
    vertical_collide = handle_vertical_collision(player, objects, player.y_velocity)
    


lOne=[]
start=Platform(890,645,152,75,WHITE)
base=Platform(0,720,1200,80,WHITE)
plat2=Platform(502,645,264,75,WHITE)
plat3=Platform(0,624,361,96,WHITE)
sShrub1=smallShrub(610,593)
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

BROWN=(100,65,23)
BLUE=(0,0,255)
lTwo=[]
lTwo.append(Platform(1031,344,57,436,BROWN))#May just do this in the future
post2=Platform(729,364,57,436,BROWN)
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


def main(window, level):
    clock = pygame.time.Clock()
    background,bg_image = get_background("Level 1 to 3 bkgrnd.png")
    playerOne=Player(1135,655,30,64)
    block_size = 96
    
    
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
    main(window,lTwo)