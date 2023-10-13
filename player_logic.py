import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

WIDTH, HEIGHT = 1200, 800
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

FPS = 60
PLAYER_VELOCITY = 5

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


def get_block(size):
    path = join("assets",  "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)

    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):  
    f = open("CurrentCharacter.txt", "r")
    current_character = f.read()

    if current_character == "":
        current_character = "Celia"
        f.close()
        f = open("CurrentCharacter.txt", "w")
        f.write("Celia")
    print("Spritesheet to be opened:", current_character)

    SPRITES = load_sprite_sheets("Characters", current_character, 32, 32, True)
    ANIMATION_DELAY = 8
    GRAVITY = 1

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_velocity, self.y_velocity = 0, 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.chop_count = 0
        self.hit = False
        self.hit_count = 0
        self.chop = False
        self.chop_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

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

    # does allow double jump
    def jump(self):
        self.y_velocity = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def landed(self):
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

    def do_chop(self):
        self.animation_count = 0
        self.chop = True

    def end_chop(self):
        self.chop_count = 0
        self.chop = False

    def update_sprite(self):
        keys = pygame.key.get_pressed()
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.chop:
            sprite_sheet = "chop"
            self.chop_count += 1
        elif self.y_velocity < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            # elif self.jump_count == 2:
            #     sprite_sheet = "double_jump"
        elif self.y_velocity > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_velocity != 0:
            sprite_sheet = "run"
        elif (keys[pygame.K_w]) or (keys[pygame.K_UP]):
            sprite_sheet = "climb"
        elif (keys[pygame.K_s]) or (keys[pygame.K_DOWN]):
            sprite_sheet = "climb"
        
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
        self.y_velocity += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_velocity, self.y_velocity)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        # FIXED NO LOOP YAY!!!!! :D
        if self.chop_count > 60:
            self.end_chop()

        self.fall_count += 1
        self.update_sprite()
 
    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width, self.height, self.name = width, height, name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)



# can be made into spikes with similar functionality
class Fire(Object):
    ANIMATION_DELAY = 4

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def fire_on(self):
        self.animation_name = "on"

    def fire_off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        # don't do in Player class if double jump
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


# emphasized in tutorial - need to run this code from directory it exists in
def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for object in objects:
        object.draw(window,offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


# collisions
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            if dy > 0:
                player.rect.bottom = object.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = object.rect.bottom
                player.hit_head()

            collided_objects.append(object)
    
    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            collided_object = object
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object

# handling player movement
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_velocity = 0
    collide_left = collide(player, objects, -PLAYER_VELOCITY * 2)
    collide_right = collide(player, objects, PLAYER_VELOCITY * 2)

    if (keys[pygame.K_LEFT] and not collide_left) or (keys[pygame.K_a] and not collide_left):
        player.move_left(PLAYER_VELOCITY)
    if (keys[pygame.K_RIGHT] and not collide_right) or (keys[pygame.K_d] and not collide_right):
        player.move_right(PLAYER_VELOCITY)
    
    vertical_collide = handle_vertical_collision(player, objects, player.y_velocity)
    to_check = [collide_left, collide_right, *vertical_collide]
    for object in to_check:
        if object and object.name == "fire":
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Green.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.fire_on()
    
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]
    
    # scrolling background at edge, this (or something similar) could most likely be used for speedrun mode
    offset_x = 0
    scroll_area_width = 200

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_e:
                    player.do_chop()
        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        # scrolling background at edge
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_velocity > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_velocity < 0):
            offset_x += player.x_velocity
    
    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
