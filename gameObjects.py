import pygame
from os import listdir
from os.path import isfile, join

FPS=60
GRAVITY=1
BLACK=(0,0,0)

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, path=None,name=None):
        super().__init__()
        self.ipath=path
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width, self.height, self.name = width, height, name
        self.original_image=pygame.Surface((width, height), pygame.SRCALPHA)
        self.original_x=0
        self.original_y=0#possible use in resizing
    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))
    
    def reset(self):
        x=0

def get_block(size,ipath):#added path so it's not always terrain.png
    path = join("assets",  "Terrain", ipath)
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)

    return pygame.transform.scale2x(surface)


class Platform(Object):
    def __init__(self, x, y, width, height,col, path=None, name=None):
        super().__init__(x, y, width, height, path, name)
        self.color=col
        self.surface=pygame.Surface((width,height))
        self.surface.fill(self.color)
        self.mask = pygame.mask.from_surface(self.surface)
    def draw(self, window,offset_x):
        pygame.draw.rect(window,self.color,self.rect)
    def reset(self):
        x=0

class Block(Object):
    def __init__(self, x, y, size,path):
        super().__init__(x, y, size, size,path)
        block = get_block(size,path)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)
    def reset(self):
        x=0

class smallShrub(Object):
    def __init__(self,x,y):
        super().__init__(x,y,48,52)
        self.name="small shrub"
        self.original_x=x
        self.original_y=y
        self.image=pygame.image.load("assets\Traps\SmallShrub\SmallShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\SmallShrub\SmallShrub.png")
    def destroy(self):
        self.image=pygame.image.load("assets\Traps\Empty\empty.png")
        self.mask=pygame.mask.from_surface(self.image)
    def reset(self):
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.image=self.original_image
        self.mask=self.original_mask

class ReverseSmallShrub(Object):
    def __init__(self,x,y):
        super().__init__(x,y,48,52)
        self.name="small shrub"
        self.original_x=x
        self.original_y=y
        self.image=pygame.image.load("assets\Traps\SmallShrub\iSmallShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\SmallShrub\iSmallShrub.png")

    def destroy(self):
        self.image=pygame.image.load("assets\Traps\Empty\empty.png")
        self.mask=pygame.mask.from_surface(self.image)
    def reset(self):
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.image=self.original_image
        self.mask=self.original_mask

class TallShrub(Object):
    def __init__(self,x,y):
        super().__init__(x,y,48,183)
        self.name="tall shrub"
        self.image=pygame.image.load("assets\Traps\TallShrub\TallShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\TallShrub\TallShrub.png")
        self.health=2
        
    def destroy(self):
        if self.health==1:
            self.image=pygame.image.load("assets\Traps\Empty\empty.png")
            self.mask=pygame.mask.from_surface(self.image)
        if self.health!=1:
            self.health-=1

    def reset(self):
        self.image=self.original_image
        self.mask=self.original_mask
        self.health=2

class Spike(Object):
    def __init__(self,x,y):
        super().__init__(x,y,40,34)
        self.name="spike"
        self.image=pygame.image.load("assets\Traps\Spikes\Spike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\Spike.png")

    def reset(self):
        self.image=self.original_image
        self.mask=self.original_mask

class BlackSpike(Object):
    def __init__(self,x,y):
        super().__init__(x,y,40,34)
        self.name="spike"
        self.image=pygame.image.load("assets\Traps\Spikes\BlackSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\BlackSpike.png")

    def reset(self):
        self.image=self.original_image
        self.mask=self.original_mask


class SideSpike(Object):
    def __init__(self, x, y, path=None, name=None):
        super().__init__(x, y, 34,40)
        self.image=pygame.image.load("assets\Traps\Spikes\Lvl3SidewaysSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\Lvl3SidewaysSpike.png")

    def reset(self):
        self.image=self.original_image
        self.mask=self.original_mask


class Water(Platform):
    def __init__(self, x, y, width, height, col, path=None, name="spike"):
        super().__init__(x, y, width, height, col, path, name)
    def reset(self):
        x=0#water has nothing that would really need to be reset

class Void(Platform):
    def __init__(self, x, y, width, height, col=BLACK, path=None, name="spike"):
        super().__init__(x, y, width, height, col, path, name)
    def reset(self):
        x=0#water has nothing that would really need to be reset

PURPLE=(128,0,128)

class FallPlat(Platform):
    def __init__(self, x, y, width, height, col=PURPLE,oList=[], path=None,name="fall"):
        super().__init__(x, y, width, height, col, path, name)
        self.original_x=x
        self.original_y=y
        self.timer=0
        self.falling=False
        self.object_list=oList
        self.copy_list=oList.copy()
        

    def check_time(self):
        if self.timer>40: #5 Seconds time limit, 60 frame x 5 Second limit = 300
            self.falling=True
            self.rect.y+=2
            for object in self.object_list:
                object.rect.y+=2
            return True #True means should fall
        return False

    def reset(self):
        self.timer=0
        self.falling=False
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.object_list=self.copy_list.copy()
    
    

class Ladder(Object):
    def __init__(self,x,y):
        super().__init__(x,y,33,100)
        self.name="ladder"
        self.xO=x
        self.yO=y
        self.image=pygame.image.load("assets\Special\Ladder.png")
        self.mask=pygame.mask.from_surface(self.image)
    def reset(self):
        self.rect.x=self.xO
        self.rect.y=self.yO


class endSign(Object):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.name = "end sign"
        self.image=pygame.image.load("assets/Special/EndSign.png")
        self.mask= pygame.mask.from_surface(self.image)
        self.original_mask = pygame.mask.from_surface(self.image)
        self.original_image = pygame.image.load("assets/Special/EndSign.png")