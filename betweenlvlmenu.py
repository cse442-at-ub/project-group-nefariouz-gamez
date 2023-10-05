import os
import random
import math
from typing import Any
import pygame
from os import listdir
#from os.path import isfile, join

#Window parameteres
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shrubbery Quest: Between Screen Menu Demo')

#load images
continue_btn_img = pygame.image.load("Assets/ContinueButton.png").convert_alpha()
exitToMain_btn_img = pygame.image.load("Assets/ExitToMainBut.png").convert_alpha()
background_img = pygame.image.load("Assets/Bakckground.png").convert_alpha()
# bg = Background()

# #background Class
# class Background(pygame.sprite.Sprite):
#     def __init__(self, image_file, location):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.image.load(image_file)
#         self.rect = self.image.get_rect()
#         self.rect.left, self.rect.top = location

#button Class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

continue_button = Button(100, 200, continue_btn_img)
exitToMain_button = Button(450, 200, exitToMain_btn_img)

#main loop
run = True
while run:

    screen.blit(background_img, (0,0))


    # event handler
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run=False
    pygame.display.update()
pygame.quit()
