import pygame
from os import listdir
from os.path import isfile, join

FPS=60
GRAVITY=1
BLACK=(0,0,0)
ORANGE=(255, 102, 0)

pygame.mixer.init()
platformBreak = pygame.mixer.Sound("assets/audio/platform-breaking.mp3")   # https://www.fesliyanstudios.com/royalty-free-sound-effects-download/wooden-impact-133

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, path=None,name=None):
        super().__init__()
        self.ipath=path
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width, self.height, self.name = width, height, name
        self.original_image=pygame.Surface((width, height), pygame.SRCALPHA)
        self.original_x=x
        self.original_y=y#possible use in resizing
    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x+offset_x, self.rect.y))
        #self.rect.x=self.original_x+offset_x



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
    def __init__(self, x, y, width, height,col, path=None, name="plat"):
        super().__init__(x, y, width, height, path, name)
        self.color=col
        self.surface=pygame.Surface((width,height))
        self.surface.fill(self.color)
        self.mask = pygame.mask.from_surface(self.surface)
    def draw(self, window,offset_x):
        #self.rect.x=self.original_x+offset_x
        pygame.draw.rect(window,self.color,(self.rect.x + offset_x, self.rect.y,self.rect.width,self.rect.height))
        #if offset_x!=0:
           # self.mask = pygame.mask.from_surface(self.surface)
    def reset(self):
        self.rect.x=self.original_x
        self.rect.y=self.original_y

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
        self.broken=False
        self.original_x=x
        self.original_y=y
        self.image=pygame.image.load("assets\Traps\SmallShrub\SmallShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\SmallShrub\SmallShrub.png")
    def destroy(self):
        self.broken=True
        self.image=pygame.image.load("assets\Traps\Empty\empty.png")
        self.mask=pygame.mask.from_surface(self.image)
    def reset(self):
        self.broken=False
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
        self.broken=False
        self.original_x=x#THIS
        self.original_y=y#THIS
        self.image=pygame.image.load("assets\Traps\TallShrub\TallShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\TallShrub\TallShrub.png")
        self.health=2

    def destroy(self):
        if self.health==1:
            self.broken=True
            self.image=pygame.image.load("assets\Traps\Empty\empty.png")
            self.mask=pygame.mask.from_surface(self.image)
        if self.health!=1:
            self.health-=1

    def reset(self):
        self.broken=False
        self.image=self.original_image
        self.mask=self.original_mask
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.health=2

class Spike(Object):
    def __init__(self,x,y):
        super().__init__(x,y,40,34)
        self.name="spike"
        self.original_x=x#THIS
        self.original_y=y#THIS
        self.image=pygame.image.load("assets\Traps\Spikes\Spike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\Spike.png")

    def destroy(self):
        self.image=pygame.image.load("assets\Traps\Empty\empty.png")
        self.mask=pygame.mask.from_surface(self.image)

    def reset(self):
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.image=self.original_image
        self.mask=self.original_mask

class SmallRedShrub(smallShrub):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\SmallShrub\SmallRedShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\SmallShrub\SmallRedShrub.png")

class SmallPurpleShrub(smallShrub):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\SmallShrub\SmallPurpleShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\SmallShrub\SmallPurpleShrub.png")

class SmallPinkShrub(smallShrub):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\SmallShrub\SmallPinkShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\SmallShrub\SmallPinkShrub.png")

class TallRedShrub(TallShrub):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\TallShrub\TallRedShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\TallShrub\TallRedShrub.png")

class TallPurpleShrub(TallShrub):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\TallShrub\TallPurpleShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\TallShrub\TallPurpleShrub.png")

class TallPinkShrub(TallShrub):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\TallShrub\TallPinkShrub.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\TallShrub\TallPinkShrub.png")

class BlackSpike(Spike):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\BlackSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\BlackSpike.png")

class BlackLSpike(Spike):##LEFT FACING BLACK SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.transform.rotate(pygame.image.load("assets\Traps\Spikes\BlackSpike.png"), 90)
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.transform.rotate(pygame.image.load("assets\Traps\Spikes\BlackSpike.png"), 90)

class BlackRSpike(Spike):##RIGHT FACING BLACK SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.transform.rotate(pygame.image.load("assets\Traps\Spikes\BlackSpike.png"), -90)
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.transform.rotate(pygame.image.load("assets\Traps\Spikes\BlackSpike.png"), -90)

class RedSpike(Spike):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\RedSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\RedSpike.png")

class BlueSpike(Spike):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\BlueSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\BlueSpike.png")

class GreenSpike(Spike):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\GreenSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\GreenSpike.png")

    def reset(self):
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.image=self.original_image
        self.mask=self.original_mask

class GreenDSpike(Spike):##DOWN FACING GREEN SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\DownGreenSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\DownGreenSpike.png")

class GreenLSpike(Spike):##LEFT FACING GREEN SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\LeftGreenSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\LeftGreenSpike.png")

class GreenRSpike(Spike):##RIGHT FACING GREEN SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\RightGreenSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\RightGreenSpike.png")

class GoldSpike(Spike):
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\GoldSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\GoldSpike.png")

class GoldDSpike(Spike):##DOWN FACING GOLD SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\GoldDSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\GoldDSpike.png")

class GoldLSpike(Spike):##LEFT FACING GOLD SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\GoldLSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\GoldLSpike.png")

class GoldRSpike(Spike):##RIGHT FACING GOLD SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\GoldRSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\GoldRSpike.png")

class SmallSpike(Spike):##RIGHT FACING GOLD SPIKE
    def __init__(self,x,y):
        super().__init__(x,y)
        self.image=pygame.image.load("assets\Traps\Spikes\SmallDSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\SmallDSpike.png")

class SideSpike(Spike):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image=pygame.image.load("assets\Traps\Spikes\Lvl3SidewaysSpike.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_mask=pygame.mask.from_surface(self.image)
        self.original_image=pygame.image.load("assets\Traps\Spikes\Lvl3SidewaysSpike.png")

class Water(Platform):
    def __init__(self, x, y, width, height, col, path=None, name="water"):
        super().__init__(x, y, width, height, col, path, name)
    def reset(self):
        x=0#water has nothing that would really need to be reset

class Void(Platform):
    def __init__(self, x, y, width, height, col=BLACK, path=None, name="void"):
        super().__init__(x, y, width, height, col, path, name)
    def reset(self):
        x=0#water has nothing that would really need to be reset

PURPLE=(128,0,128)

class FallPlat(Platform):
    def __init__(self, x, y, width, height, col=PURPLE,oList=[], path=None,name="fall"):
        super().__init__(x, y, width, height, col, path, name)
        self.surface=pygame.Surface((width,height))
        self.original_x=x
        self.original_y=y
        self.original_width=width
        self.original_height=height
        self.timer=0
        self.falling=False
        self.object_list=oList
        self.copy_list=oList.copy()
        self.destroyCount = 0

    def destroy(self):
        self.destroyCount += 1
        self.rect.width=0
        self.rect.height=0
        self.surface=pygame.Surface((self.rect.width,self.rect.height))
        self.mask = pygame.mask.from_surface(self.surface)

    def check_time(self,player):
        c=0
        if pygame.sprite.collide_mask(player.reachBox, self):
            c=1
            self.timer+=1
        else:
            for object in self.object_list:
                if pygame.sprite.collide_mask(player.reachBox, object) and c==0:
                    c=1
                    self.timer+=1
                    break
        if self.timer>250: #5 Seconds time limit, 60 frame x 5 Second limit = 300
            #self.falling=True
            #self.rect.y+=2
            self.destroy()
            if self.destroyCount == 1:
                with open('assets/txt/al.txt', 'r') as audioFile:
                    lines = audioFile.readlines()
                if lines[2].strip().lower() == "false":
                    platformBreak.set_volume(float(lines[1]))
                    platformBreak.play()
            for object in self.object_list:
                #object.rect.y+=2
                object.destroy()
            return True #True means should fall
        return False

    def reset(self):
        self.timer=0
        self.falling=False
        self.destroyCount = 0
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.rect.width=self.original_width
        self.rect.height=self.original_height
        self.object_list=self.copy_list.copy()
        self.surface=pygame.Surface((self.rect.width,self.rect.height))
        self.mask = pygame.mask.from_surface(self.surface)



class Ladder(Object):
    def __init__(self,x,y):
        super().__init__(x,y,33,100)
        self.player_on=False
        self.name="ladder"
        self.xO=x
        self.yO=y
        self.image=pygame.image.load("assets\Special\Ladder.png")
        self.mask=pygame.mask.from_surface(self.image)
    def reset(self):
        self.rect.x=self.xO
        self.rect.y=self.yO
        self.image=pygame.image.load("assets\Special\Ladder.png")
        self.mask=pygame.mask.from_surface(self.image)
    def destroy(self):
        self.image=pygame.image.load("assets\Traps\Empty\empty.png")
        self.mask=pygame.mask.from_surface(self.image)

class MovePlat(Platform):
    def __init__(self, x, y, width, height,lbound,rbound,oList=[],aList=[], path=None,name="move",col=ORANGE,):
        super().__init__(x,y,width,height,col,path,name)
        #self.name="move"
        self.surface=pygame.Surface((width,height))
        self.right_bound=rbound
        self.left_bound=lbound
        self.original_x=x
        self.original_y=y
        self.original_width=width
        self.original_height=height
        self.object_list=oList#list of objects moving with platform
        self.copy_list=oList.copy()
        self.adjacent_list=aList#list of platforms on same line
        self.copya_list=aList.copy()
        self.direction=True#True means right, False means left, all start going right

    def set_a(self,platlist):
        self.adjacent_list =platlist
        self.copya_list = self.adjacent_list.copy()

    def loop(self,player):
        c=0
        if self.direction:#If moving right
            self.rect.x+=2
            if pygame.sprite.collide_mask(player.feetBox, self) and player.rect.bottom<self.rect.bottom:# and player.rect.bottom-10<self.rect.top:
                player.rect.x+=2
                player.reachBox.rect.x+=2
                player.feetBox.rect.x+=2
                c=1
            else:
                for object in self.object_list:
                    if pygame.sprite.collide_mask(player, object) and c==0:
                        player.rect.x+=2
                        player.reachBox.rect.x+=2
                        player.feetBox.rect.x+=2
                        c=1
                        break
            if(self.rect.right==self.right_bound or self.rect.right>self.right_bound):#If platform has reached the right bound
               self.direction=False#platform is now going left
               for plat in self.adjacent_list:
                   plat.direction=False#This platform has changed direction, every platform on this line must as well
            for object in self.object_list:
                object.rect.x+=2
        else:#if moving left
            self.rect.x-=2
            if pygame.sprite.collide_mask(player.feetBox, self) and player.rect.bottom<self.rect.bottom:# and player.rect.bottom-10<self.rect.top:
                player.rect.x-=2
                player.reachBox.rect.x-=2
                player.feetBox.rect.x-=2
                c=1
                c=1
            else:
                for object in self.object_list:
                    if pygame.sprite.collide_mask(player, object) and c==0:
                        player.rect.x-=2
                        player.reachBox.rect.x-=2
                        player.feetBox.rect.x-=2
                        c=1
                        break
            if(self.rect.left==self.left_bound or self.rect.left<self.left_bound):
                self.direction=True#platform is now going right
                for plat in self.adjacent_list:
                   plat.direction=True#All platforms change direction together
            for object in self.object_list:
                object.rect.x-=2

    def reset(self):
        self.timer=0
        self.direction=True
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.object_list=self.copy_list.copy()
        self.adjacent_list=self.copya_list.copy()
        self.surface=pygame.Surface((self.rect.width,self.rect.height))
        self.mask = pygame.mask.from_surface(self.surface)


class MovePlatVert(Platform):
    def __init__(self, x, y, width, height,hbound,lbound,oList=[],aList=[], path=None,name="move",col=ORANGE,):
        super().__init__(x, y, width, height, col, path, name)
        #self.name="move"
        self.surface=pygame.Surface((width,height))
        self.high_bound=hbound
        self.low_bound=lbound
        self.original_x=x
        self.original_y=y
        self.original_width=width
        self.original_height=height
        self.object_list=oList#list of objects moving with platform
        self.copy_list=oList.copy()
        self.adjacent_list=aList#list of platforms on same line
        self.copya_list=aList.copy()
        self.direction=True#True means up, False means down, all start going UP

    def set_a(self,platlist):
        self.adjacent_list =platlist
        self.copya_list = self.adjacent_list.copy()

    def loop(self,player):
        c=0
        if self.direction:#If moving UP
            self.rect.y-=2
            if pygame.sprite.collide_mask(player.feetBox, self) and player.rect.bottom<self.rect.bottom:# and player.rect.bottom-10<self.rect.top:
                player.rect.y-=2
                player.reachBox.rect.y-=2
                player.feetBox.rect.y-=2
                c=1
            else:
                for object in self.object_list:
                    if pygame.sprite.collide_mask(player.feetBox, object) and c==0:
                        player.rect.y-=2
                        player.reachBox.rect.y-=2
                        player.feetBox.rect.y-=2
                        c=1
                        break
            if(self.rect.top==self.high_bound or self.rect.top<self.high_bound):#If platform has reached the high bound
               self.direction=False#platform is now going DOWN
               for plat in self.adjacent_list:
                   plat.direction=False#This platform has changed direction, every platform on this line must as well
            for object in self.object_list:
                object.rect.y-=2
        else:#if moving DOWN
            self.rect.y+=2
            if pygame.sprite.collide_mask(player.feetBox, self) and player.rect.bottom<self.rect.bottom:#and player.rect.bottom-10<self.rect.top:
                player.rect.y+=2
                player.reachBox.rect.y+=2
                player.feetBox.rect.y+=2
                c=1
                c=1
            else:
                for object in self.object_list:
                    if pygame.sprite.collide_mask(player.feetBox, object) and c==0:
                        player.rect.y+=2
                        player.reachBox.rect.y+=2
                        player.feetBox.rect.y+=2
                        c=1
                        break
            if(self.rect.bottom==self.low_bound or self.rect.bottom>self.low_bound):
                self.direction=True#platform is now going UP
                for plat in self.adjacent_list:
                   plat.direction=True#All platforms change direction together
            for object in self.object_list:
                object.rect.y+=2


    def reset(self):
        self.timer=0
        self.direction=True
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.object_list=self.copy_list.copy()
        self.adjacent_list=self.copya_list.copy()
        self.surface=pygame.Surface((self.rect.width,self.rect.height))
        self.mask = pygame.mask.from_surface(self.surface)

class MovePlatDiag(Platform):
    def __init__(self, x, y, width, height,rise, run,lbound,rbound,oList=[],aList=[], path=None,name="move",col=ORANGE,):
        super().__init__(x, y, width, height, col, path, name)
        self.surface=pygame.Surface((width,height))
        self.right_bound=rbound
        #self.name="move"
        self.dy=rise#vertical speed
        self.dx=run#horizontal speed
        #By using negative values for rise and/or run, diagonal direction can be changed.
        self.left_bound=lbound
        self.original_x=x
        self.original_y=y
        self.original_width=width
        self.original_height=height
        self.object_list=oList#list of objects moving with platform
        self.copy_list=oList.copy()
        self.adjacent_list=aList#list of platforms on same line
        self.copya_list=aList.copy()
        self.direction=True#True means right, False means left, all start going right

    def set_a(self,platlist):
        self.adjacent_list =platlist
        self.copya_list = self.adjacent_list.copy()

    def loop(self,player):
        c=0
        if self.direction:#If moving right
            self.rect.x+=self.dx
            self.rect.y-=self.dy
            if pygame.sprite.collide_mask(player.feetBox, self) and player.rect.bottom<self.rect.bottom:
                player.rect.x+=self.dx
                player.reachBox.rect.x+=self.dx
                player.feetBox.rect.x+=self.dx
                player.rect.y-=self.dy
                player.reachBox.rect.y-=self.dy
                player.feetBox.rect.y-=self.dy
                c=1
            else:
                for object in self.object_list:
                    if pygame.sprite.collide_mask(player, object) and c==0:
                        player.rect.x+=self.dx
                        player.reachBox.rect.x+=self.dx
                        player.feetBox.rect.x+=self.dx
                        player.rect.y-=self.dy
                        player.reachBox.rect.y-=self.dy
                        player.feetBox.rect.y-=self.dy
                        c=1
                        break
            if(self.rect.right==self.right_bound or self.rect.right>self.right_bound):#If platform has reached the right bound
               self.direction=False#platform is now going left
               for plat in self.adjacent_list:
                   plat.direction=False#This platform has changed direction, every platform on this line must as well
            for object in self.object_list:
                object.rect.x+=self.dx
                object.rect.y-=self.dy
        else:#if moving left
            self.rect.x-=self.dx
            self.rect.y+=self.dy
            if pygame.sprite.collide_mask(player.feetBox, self) and player.rect.bottom<self.rect.bottom:
                player.rect.x-=self.dx
                player.rect.y+=self.dy
                player.reachBox.rect.y+=self.dy
                player.reachBox.rect.x-=self.dx
                player.feetBox.rect.x-=self.dx
                player.feetBox.rect.y+=self.dy
                c=1
                c=1
            else:
                for object in self.object_list:
                    if pygame.sprite.collide_mask(player, object) and c==0:
                        player.rect.x-=self.dx
                        player.reachBox.rect.x-=self.dx
                        player.feetBox.rect.x-=self.dx
                        player.rect.y+=self.dy
                        player.reachBox.rect.y+=self.dy
                        player.feetBox.rect.y+=self.dy
                        c=1
                        break
            if(self.rect.left==self.left_bound or self.rect.left<self.left_bound):
                self.direction=True#platform is now going right
                for plat in self.adjacent_list:
                   plat.direction=True#All platforms change direction together
            for object in self.object_list:
                object.rect.x-=self.dx
                object.rect.y+=self.dy

    def reset(self):
        self.timer=0
        self.direction=True
        self.rect.x=self.original_x
        self.rect.y=self.original_y
        self.object_list=self.copy_list.copy()
        self.adjacent_list=self.copya_list.copy()
        self.surface=pygame.Surface((self.rect.width,self.rect.height))
        self.mask = pygame.mask.from_surface(self.surface)

class endSign(Object):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.name = "end sign"
        self.image=pygame.image.load("assets/Special/EndSign.png")
        self.mask= pygame.mask.from_surface(self.image)
        self.original_x=x#THIS
        self.original_y=y#THIS
        self.original_mask = pygame.mask.from_surface(self.image)
        self.original_image = pygame.image.load("assets/Special/EndSign.png")

class compSign(Object):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.name = "end sign"
        self.image=pygame.image.load("assets/Special/EndSign.png")
        self.mask= pygame.mask.from_surface(self.image)
        self.original_x=x#THIS
        self.original_y=y#THIS
        self.original_mask = pygame.mask.from_surface(self.image)
        self.original_image = self.image

    def draw(self, window, offset_x):
        pass


class goldShears(Object):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.name = "end sign"
        self.image=pygame.image.load("assets\Special\GoldenShears.png")
        self.mask= pygame.mask.from_surface(self.image)
        self.original_x=x#THIS
        self.original_y=y#THIS
        self.original_mask = pygame.mask.from_surface(self.image)
        self.original_image = pygame.image.load("assets\Special\GoldenShears.png")

class AnglePlat(Object):#205 125
    def __init__(self, x, y):
        super().__init__(x,y,205,125)
        self.name = "angle"
        self.image=pygame.image.load("assets\Terrain\AngledPlatform.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_x=x#THIS
        self.original_y=y#THIS
        self.original_mask = pygame.mask.from_surface(self.image)
        self.original_image = pygame.image.load("assets\Terrain\AngledPlatform.png")

class AngleSpike(Object):
    def __init__(self, x, y):
        super().__init__(x,y,41,41,None,"spike")
        self.name = "spike"
        self.image=pygame.image.load("assets\Traps\Spikes\GreenSpikeAngled.png")
        self.mask=pygame.mask.from_surface(self.image)
        self.original_x=x#THIS
        self.original_y=y#THIS
        self.original_mask = pygame.mask.from_surface(self.image)
        self.original_image = pygame.image.load("assets\Traps\Spikes\GreenSpikeAngled.png")
    def destroy(self):
        self.image=pygame.image.load("assets\Traps\Empty\empty.png")
        self.mask=pygame.mask.from_surface(self.image)

    def reset(self):
        self.rect.x=self.original_x#THIS
        self.rect.y=self.original_y#THIS
        self.image=self.original_image
        self.mask=self.original_mask