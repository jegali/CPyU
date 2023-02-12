# More Graphics enhancements
This version is all about some polishing and enhancements, mainly on the graphics / display module

## Flash
Ah-ah<br/>
He's a miracle<br/>
(Queen, Flash Gordon)<br/>

What is a display without a blinking cursor - or without a cursor at all? The user can't see "where he is" and it looks bad too. Therefore, in this section, we will take care of character blinking. [Wikipedia](https://en.wikipedia.org/wiki/Apple_II_character_set) is helpful here:

"The original Signetics 2513 character generator chip has 64 glyphs for upper case, numbers, symbols, and punctuation characters. Each 5x7 pixel bitmap matrix is displayed in a 7x8 character cell on the text screen. The 64 characters can be displayed in INVERSE in the range $00 to $3F, FLASHing in the range $40 to $7F, and NORMAL mode in the range $80 to $FF. Normal mode characters are repeated in the $80 to $FF range."

So we have an alphabet of 64 characters that is repeated four times in memory. Sounds like a bit manipulation task. We can use the divmod() function here - as well as when calculating the memory address on the display. Here is a small source code snippet:

```bash
value = 0x82
mode, ch = divmod(value, 0x40)
print ("mode", mode)
print ("ch", ch)
```

And some sample runs of the program:

```bash
value = 0x82
mode: 2
ch: 2

value = 0x42
mode: 1
ch: 2

value = 0x02
mode: 0
ch: 2
```

The emulation of the graphics output of the Apple works in such a way that whenever a point in the screen memory changes, a soft switch is triggered. So only one character is changed at a time. We would now only have to examine the entire memory area from 0x400-0x7FF, where a "flashing" character is located, and update this location in our graphics emulation. However, this would mean that many bus accesses would be thrown. I want to avoid that. So I create a buffer area where I keep a current copy of the screen memory. this is queried in every update or let's say every 0.5 seconds and all chars with flashbit are rewritten into the screen memory.

There is a change from normal character to inverse character and back again. Since we have already generated the inverse chars during character generation, we only have to choose the appropriate index from the two-dimensional char array and blitte the corresponding character. Here are the changes to the display.py class:

```bash
import pygame
import numpy
import time

from pygame.locals import *


class Display:

...

    def __init__(self):
        # auf diese Surface wird anstelle des Screens gezeichnet
        # Die surface wird dann im update_new auf den Screen geblittet und
        # so vergrößert dargestellt
        self.screen = pygame.display.set_mode((560,384))

        self.page = 1
        self.text = True
        self.colour = False
        
        # N E W
        
        # timer for the flash interval
        self.flash_time = time.time()
        self.flash_on = False
        # offscreen buffer for two text pages
        self.flash_chars = [[0] * 0x400] * 2
        
        self.chargen = []
        for c in self.characters:
            chars = [[pygame.Surface((14, 16)), pygame.Surface((14, 16))],
                     [pygame.Surface((14, 16)), pygame.Surface((14, 16))]]
            for colour in (0, 1):
                #hue = (255, 255, 255) if colour else (0, 200, 0)
                hue = (255, 255, 255) if colour else (255, 176, 0)
                for inv in (0, 1):
                    pixels = pygame.PixelArray(chars[colour][inv])
                    off = hue if inv else (0, 0, 0)
                    on = (0, 0, 0) if inv else hue
                    for row in range(8):
                        b = c[row] << 1
                        for col in range(7):
                            bit = (b >> (6 - col)) & 1
                            pixels[2 * col][2 * row] = on if bit else off
                            pixels[2 * col + 1][2 * row] = on if bit else off
                    del pixels
            self.chargen.append(chars)


    def update(self, address, value):
        if self.page == 1:
            start_text = 0x400
        elif self.page == 2:
            start_text = 0x800
        else:
            return
        
        # Sicherstellen, dass die Adresse auch auf der Textseite liegt
        if start_text <= address <= start_text + 0x3FF:
            # base beinhaltet das Offset, bzw. die Position auf der Textseite
            base = address - start_text
            
            # N E W
            
            # update the offscreen buffer
            self.flash_chars[self.page - 1][base] = value
            # hi beinhaltet die Nummer des 128-Byte-Blocks, in dem sich die Adresse befindet (0-7)
            # lo ist das Offset innerhalb des 128-Byte-Blocks
            hi, lo = divmod(base, 0x80)
            # es gibt drei Bereiche in dem 128 Byte Block: Zeile 1, 2, 3, und der Overscanbereich
            # column geht von 0-39 und ist die Spalte in der jeweiligen Zeile
            # row_group 0, 1, 2 ist OK. 3 ist der Overscanbereich
            row_group, column = divmod(lo, 0x28)
            row = hi + 8 * row_group

            # Overscanbereich. Hier gibt es nichts darzustellen
            if row_group == 3:
                return

            # Wir sind im Text (only) Modus
            if self.text:
                # Aus dem übergebenen Wert den Charactr auslesen
                # Über 0x40 wird ermittelt, ob es sich um einen normalen, 
                # inversen oder flashenden Character handelt
                mode, ch = divmod(value, 0x40)
                
                # N E W
                
                if mode == 0:
                    inv = True
                elif mode == 1:
                    inv = self.flash_on
                else:
                    inv = False

                self.screen.blit(self.chargen[ch][self.colour][inv], (2 * (column * 7), 2 * (row * 8)))

    # N E W
    
    def flash(self):
        # geblinkt wird alle 0,5 sekunden
        if time.time() - self.flash_time >= 0.5:
            # toggle für an / aus
            self.flash_on = not self.flash_on
            # gehe den gesamten offscreen buffer durcg
            for offset, char in enumerate(self.flash_chars[self.page - 1]):
                # wenn es einen flashenden char gibt, updaten
                if (char & 0xC0) == 0x40:
                    self.update(0x400 + offset, char)
            self.flash_time = time.time()

```

Of course, the Flash must also be called. This is done in the main loop in the beloved_apple.py class. Please note the line display.flash()

```bash
            update_cycle += 1
            if update_cycle >= 1024:
                display.flash()
                pygame.display.flip()
                if speaker:
                    speaker.update(bus_cycle)
                update_cycle = 0

```
