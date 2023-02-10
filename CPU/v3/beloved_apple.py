import pygame
import time

from pygame.locals import *

from apple2 import Apple2

myApple = Apple2(None)
pygame.init()
display_screen = pygame.display.set_mode((560, 384))


def main():
    quit = False
    while not quit:
        myApple.cpu.exec_command()

        for event in pygame.event.get():
              if event.type == pygame.QUIT:
                    quit = True


if __name__ == "__main__":
    main()