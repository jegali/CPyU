# Standalone Emulation
The step-by-step emulation from V2 showed me where there were still bugs in the code, as Python pointed out the errors very elegantly and with extensive stacktrace. After I fixed these bugs and the emulation ran stable over many steps, I wrote a routine to run the emulation "by itself and all the time". There were no more error messages, however this approach is unfortunately too slow for a real emulation. Therefore I wrote this version.

## Time measurement
The original Apple ][ ran with a clock frequency of 1.020... MHz, so about 1 MHz. Conversely, this means that a timing signal (aka clock cycle) is generated a million times per second or - expressed the other way around - every microsecond. I wrote a timer which outputs the number of processed clock cycles per second for my pyQt application. It was far below the required 1 million - so I decided to abandon the graphical user interface and switch to pygame for the real-time simulation. By means of pygame - so I thought - I have also directly the possibility to write the screen module of the Apple and to realize the sound output.

```bash
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
```

This is the base emulation that gives the framework for the entire program. In the next versions we will build up this emulation piece by piece.

Attention: 
There is only one file in this directory. However, this is not the complete emulator, just the pygame class that starts the emulator. All other files from V2 are still required!

## Usage
Start the emulation by typing in:

```bash
python beloved_apple.py
```
