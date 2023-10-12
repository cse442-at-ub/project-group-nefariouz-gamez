import pygame
from os import listdir
from os.path import isfile, join
from gameObjects import Platform

WHITE = (255,255,255)

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
