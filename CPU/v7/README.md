# More Graphics enhancements
This version is all about some polishing and enhancements, mainly on the graphics / display module. Please do not mind the sources for disk-controller and floppy. They will be discussed soon.

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

This concludes the flash-routine

## Low resolution graphics
In this mode, the apple is able to display graphics with a resolution of 40x40 pixels. In X-direction there is no change to our current routine, only in Y-direction the pixel has to be divided into two parts, because only 20 lines of the text display are used for the graphic. The other 3 lines are still available for input.

I've read a lot about the way the Apple works in graphics mode and how it displays colors. Interestingly, the Apple doesn't actually have any color representation at all, only via a trick the NTSC system common in America is fooled into thinking there is color information in the video signal. This results in such strange combinations as color pixels that cannot be displayed next to each other because they belong to different "color palettes".

Again, I was convinced I had to recreate all the hardware, but that's actually all done. I only have to calculate the half pixels, query the softswitches and set the pixel blocks. Oh yes, the Apple colors still have to be defined. Let's start directly with the definition of colors:

```bash
class Display:

    # Dies ist das Characterset, wie es vom signetics 2513 erzeugt wird.
    # http://www.bitsavers.org/components/signetics/_dataBooks/1972_Signetics_MOS.pdf

    characters = [
        [0b00000, 0b01110, 0b10001, 0b10101, 0b10111, 0b10110, 0b10000, 0b01111],
        ...
    ]

    lores_colours = [
        (0, 0, 0),  # black
        (208, 0, 48),  # magenta / dark red
        (0, 0, 128),  # dark blue
        (255, 0, 255),  # purple / violet
        (0, 128, 0),  # dark green
        (128, 128, 128),  # gray 1
        (0, 0, 255),  # medium blue / blue
        (96, 160, 255),  # light blue
        (128, 80, 0),  # brown / dark orange
        (255, 128, 0),  # orange
        (192, 192, 192),  # gray 2
        (255, 144, 128),  # pink / light red
        (0, 255, 0),  # light green / green
        (255, 255, 0),  # yellow / light orange
        (64, 255, 144),  # aquamarine / light green
        (255, 255, 255),  # white
    ]

    def __init__(self):
        ...

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
            if self.text or not self.mix or not row < 20:
                # Aus dem übergebenen Wert den Charactr auslesen
                # Über 0x40 wird ermittelt, ob es sich um einen normalen, 
                # inversen oder flashenden Character handelt
                mode, ch = divmod(value, 0x40)
                
                if mode == 0:
                    inv = True
                elif mode == 1:
                    inv = self.flash_on
                else:
                    inv = False

                self.screen.blit(self.chargen[ch][self.colour][inv], (2 * (column * 7), 2 * (row * 8)))
 # NEW ->
            else:
                pixels = pygame.PixelArray(self.screen)
                if not self.high_res:
                    lower, upper = divmod(value, 0x10)
                    # double the width, same as with chars
                    for dx in range(14):
                        for dy in range(8):
                            x = column * 14 + dx
                            y = row * 16 + dy
                            pixels[x][y] = self.lores_colours[upper]
                        for dy in range(8, 16):
                            x = column * 14 + dx
                            y = row * 16 + dy
                            pixels[x][y] = self.lores_colours[lower]
                del pixels


    def flash(self):
        ...


    def txtclr(self):
        self.text = False

    def txtset(self):
        self.text = True
        self.colour = False

    def mixclr(self):
        self.mix = False

    def mixset(self):
        self.mix = True
        self.colour = True

    def lowscr(self):
        self.page = 1

    def hiscr(self):
        self.page = 2

    def lores(self):
        self.high_res = False

    def hires(self):
        self.high_res = True
```

In the softswitches-class you don't have to remove the comments in front of the already introduced switches:

```bash
class SoftSwitches:

    def __init__(self, speaker, display, myApple):
        self.kbd = 0x00
        self.myApple = myApple
        self.speaker = speaker
        self.display = display

    def read_byte(self, cycle, address):
        assert 0xC000 <= address <= 0xCFFF
        if address == 0xC000:
            self.myApple.memory.write_byte(cycle, address, self.kbd)
            return self.kbd
        elif address == 0xC010:
            self.kbd = self.kbd & 0x7F
            self.myApple.memory.write_byte(cycle, 0xc000, self.kbd)
        elif address == 0xC030:
            if self.speaker:
                self.speaker.toggle(cycle)
        elif address == 0xC050:
            self.display.txtclr()
        elif address == 0xC051:
            self.display.txtset()
        elif address == 0xC052:
            self.display.mixclr()
        elif address == 0xC053:
            self.display.mixset()
        elif address == 0xC054:
            self.display.lowscr()
        elif address == 0xC055:
            self.display.hiscr()
        elif address == 0xC056:
            self.display.lores()
        elif address == 0xC057:
            self.display.hires()

        else:
            pass
        return 0x00
```

And that's actually it. I have tested the Lores mode with two small programs:

```bash
10  GR
20  FOR C = 0 TO 14
30  COLOR= C + 1
40  FOR Y = C * 2 TO C * 2 + 10
50  FOR X = C * 2 TO C * 2 + 10
60  PLOT X,Y
70  NEXT X
80  NEXT Y
90  NEXT C
```

![lores-1](/images/lores-1.png)

```bash
100 GR
130 COLOR = RND(16)     # for Integer Basic
130 COLOR = RAND(1)*16  # for Applesoft Basic
150 X = RND(40)         # see above
160 Y = RND(40)         # see above
180 PLOT X,Y
200 GOTO 130
```

![lores-2](/images/lores-2.png)

With the BASIC dialects Integer- and Applesoft-Basic it has to be considered how for example the RND function for the calculation of random functions works. While in Integer-Basic RND(40) returns a number between 0 and 39, the same command in Applesoft returns a number between 0 and 1. Therefore for Applesoft the determined random number must still be multiplied by 40 to get a number between 0 ud 39.

Besides, there was a "stumble" when running the first program. After adjusting the queue in the main-loop in belioved-apple.py this changed though, the program now runs smoothly:

```bash
           # alle 1024 Zyklen wird das Display
            # upgedatet und der Lautsprecher abgefragt
            update_cycle += 1
            # if update_cycle >= 1024:   <-- OLD
            if update_cycle >= 16:
                display.flash()
                pygame.display.flip()
                if speaker:
                    speaker.update(bus_cycle)
                update_cycle = 0

```

## Usage
Start the emulation by typing in:

```bash
python beloved_apple.py
```
