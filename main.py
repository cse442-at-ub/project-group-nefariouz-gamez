# environment setup taken from freeCodeCamp.org on Youtube: https://www.youtube.com/watch?v=6gLeplbqtqg

import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Shrubbery Quest")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1080, 720
FPS = 60
PLAYER_VEL = 5
PLAYER_X_POS=0
PLAYER_Y_POS=0

window = pygame.display.set_mode((WIDTH, HEIGHT))

def main(window):
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)