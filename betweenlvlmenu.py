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
background_img = pygame.image.load("Assets/Background.png").convert_alpha()
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
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        #set mouse click so click only register once
        self.clicked = False
        self.changeScale = scale

    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check if mouse over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        #reset mouse click
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        #draw button on screen
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

continue_button = Button(450, 400, continue_btn_img, 1)
exitToMain_button = Button(450, 520, exitToMain_btn_img, 1)

#main loop
betweenlvl = True
while betweenlvl:

    #set background
    screen.blit(background_img, (0,0))
    
    #draw buttons
    if continue_button.draw():
        print("CONTINUE")
    if exitToMain_button.draw():
        print("EXIT")

    # event handler
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            betweenlvl=False
    pygame.display.update()
pygame.quit()
