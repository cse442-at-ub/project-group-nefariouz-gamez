import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

#Window parameteres
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shrubbery Quest: Between Screen Menu Demo')

#main loop
run = True
while run:
    # event handler
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run=False
    pygame.display.update()
pygame.quit()
