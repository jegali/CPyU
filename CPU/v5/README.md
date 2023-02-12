# Display
Last status: The emulation of the Apple rom is running and it beeps at startup. Now, of course, 
it would be nice to have an output on the screen as well. Spoiler in advance: The display of the video output is anything but simple...

## The RAM layout
Before we can look at how the graphics output looks in the Apple ][, it makes sense to look at the RAM layout of the Apple. 

- **$0000-$00FF**. This is the 6502 zero page and it is used exten- sively by all parts of the lie's operating system, including the system monitor (see Chapter 3), the Applesoft interpreter (see Chapter 4), and the disk operating system (see Chapter 5). Those locations available for use by your own programs are set out in Table 2-5.
- **$0100-$01FF**. This is the 6502 stack area and is also used for temporary data storage by the Applesoft interpreter (see Chap- ter 4).
- **$0200-$02FF**. This area of memory is normally used as an input buffer whenever character information is entered from the key- board or from diskette (see Chapter 6).
- **$0300-$03CF**. This area of memory is not used by any of the built-iil programs in the lie and so is available for use by your own programs. It is an ideal location for storing small assem- bly-language programs that are called from Applesoft and most of the examples presented in this book are to be loaded here.
- **$03D0-$03FF**. This area of memory is used by the disk oper- ating system, Applesoft, and the system monitor for the pur- pose of storing position-independent vectors to important sub- routines that can be located anywhere in memory (such as interrupt-handling subroutines). See Appendix IV for a com- plete description of how this area is used.
- **$0400-$07FF**. This is pagel of video memory that is used for displaying both the primary text screen and the primary low- resolution graphics screen (see Chapter 7). It is also used for displaying one-half of the text screen when in 80-column mode.
- **$0800-$0BFF**. This is page2 of video memory that is used for displaying both the secondary text screen and the secondary low-resolution graphics screen (see Chapter 7). Since page2 is rarely used, this area of memory is normally used for program storage; in fact, the default starting position for an Applesoft program is $801.
- **$0C00-$1FFF**. This area of memory is free for use.
- **$2000-$3FFF**. This is pagel of video memory that is used for displaying the primary high-resolution graphics screen (see Chapter 7).
- **$4000-$5FFF**. This is page2 of video memory that is used for displaying the secondary high-resolution graphics screen (see Chapter 7).
- **$6000-$BFFF**. This area of memory is normally free for use. However, the upper part of it (above $9600) will be used if a disk operating system is installed (see Chapter 5).
- **$C100-$C7FF**. This is the peripheral-card ROM space. One page of ROM is reserved for use at each slot: $C100 . . . $C1FF for slot 1, $C200 . . . $C2FF for slot 2, and so on (see Chapter 11).
- **$C800-$CFFF**. This is the peripheral-card expansion ROM space. Each peripheral card can contain a block of memory that uses these addresses (see Chapter 11).
- **$C100-$CFFF**. This is the internal 80-column firmware ROM that contains extensions to the system monitor, subroutines to support the 80-column text display, and self-test subroutines.
- **$D000-$F7FF**. This is the Applesoft ROM space (see Chapter 4).
- **$F800-$FFFF**. This is the standard system monitor ROM space (see Chapter 3).

## The Text Display ($400-$7FF)
The text display is what this version of the emulator is about. We will see that the addressing of the display is not linear - but we don't want to think about why this is so. Only this much: It was the cheapest and most ingenious variant Woz came up with in the 70s. 

A standard II+ is capable of displaying text in a 40-column-by-24-row mode only. However, 40 x 24 results in 960, and 1024 bytes are reserved for the display - so there is some wastage here that is not used for the display - but another ingenious solution here is that these RAM bytes not used for the display are used for expansion cards as scratchpad.

For the display the available memory of 1024 Bytes is chunked into 128 bytes. Each of these 128 byte chunks is divided into three 40 byte areas representing three lines with each line using 40 bytes. The remaining 8 bytes (3 x 40 = 120) serve as scratchpad. However, the three 40-byte blocks are not in consecutive lines. The following table shows the structure of the display and the memory arrangement. As said, Woz had to save transistor gates when creating the Apple II, and the multiplexer circuit he designed just delivered this result.

![display-memory](/images/display-memory-layout.png)

Here you can see very well that the screen is divided into three areas of 8 lines each: the top area, the middle area and the bottom area. Each 128 byte block starts in its own line from 0-7. The 128 byte blocks are divided into three areas for three lines, each of which is displayed on the screen at an offset of 8 lines.

Now we just need a formula to map any memory location to the corresponding screen location. From the books of Winston Gyler and Jim Sather you can learn a lot about the multiplexer Woz designed and used. In the end, this process and the bit manipulation carried out with it only have to be undone. For this purpose I wrote a small Jupyter notebook and developed the following formula: 

```bash
start_text = 0x400
address = 0x488

# Sicherstellen, dass die Adresse auch auf der Textseite liegt
if start_text <= address <= start_text + 0x3FF:
    # base beinhaltet das Offset, bzw. die Position auf der Textseite
    base = address - start_text
    # hi beinhaltet die Nummer des 128-Byte-Blocks, in dem sich die Adresse befindet (0-7)
    # lo ist das Offset innerhalb des 128-Byte-Blocks
    hi, lo = divmod(base, 0x80)
    # es gibt drei Bereiche in dem 128 Byte Block: Zeile 1, 2, 3, und der Overscanbereich
    # column geht von 0-39 und ist die Spalte in der jeweiligen Zeile
    # row_group 0, 1, 2 ist OK. 3 ist der Overscanbereich
    row_group, column = divmod(lo, 0x28)
    row = hi + 8 * row_group
    
print("address:", hex(address))
print ("base:", base)
print("hi:", hi)
print("lo:", lo)
print("row_group:", row_group)
print("column:", column)
print("row:", row)

address: 0x488
base: 136
hi: 1
lo: 8
row_group: 0
column: 8
row: 1
```

Very good - the memory can now be addressed and read out appropriately. Now only an output routine for the text display is missing. And of course the appropriate font...

## The Apple font
To make the emulation as authentic as possible, I decided to use the original Apple ][ font, of course. After some research on the internet I found it on Wikipedia (https://en.wikipedia.org/wiki/Apple_II_character_set).
The original Signetics 2513 character generator chip has 64 glyphs for upper case, numbers, symbols, and punctuation characters. Each 5x7 pixel bitmap matrix is displayed in a 7x8 character cell on the text screen. The 64 characters can be displayed in INVERSE in the range $00 to $3F, FLASHing in the range $40 to $7F, and NORMAL mode in the range $80 to $FF. Normal mode characters are repeated in the $80 to $FF range.

![Apple-Font](/images/Apple_II_character_set.gif)

A search for signetics and in particular the 2513 produced a data sheet on the Internet at this address http://www.bitsavers.org/components/signetics/_dataBooks/1972_Signetics_MOS.pdf, in which the 2513 was also described, which is used as a character generator in Apple is used. Ideally, the data sheet also included a drawing showing the bit pattern used for the characters.

![Apple-Font](/images/font-bitpattern.png)

With the help of this graphic I was able to develop a character set for the display. I stored the information in a bit array. Each character is stored line by line in this array.

```bash
class Display:
   
    # Dies ist das Characterset, wie es vom signetics 2513 erzeugt wird.
    # http://www.bitsavers.org/components/signetics/_dataBooks/1972_Signetics_MOS.pdf

    characters = [
        [0b00000, 0b01110, 0b10001, 0b10101, 0b10111, 0b10110, 0b10000, 0b01111],
        [0b00000, 0b00100, 0b01010, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01111, 0b10000, 0b10000, 0b10000, 0b10011, 0b10001, 0b01111],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11111],
        [0b00000, 0b00000, 0b10000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00000],
        [0b00000, 0b11111, 0b00011, 0b00011, 0b00011, 0b00011, 0b00011, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b01010, 0b10001, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
        [0b00000, 0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010],
        [0b00000, 0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
        [0b00000, 0b11000, 0b11001, 0b00010, 0b00100, 0b01000, 0b10011, 0b00011],
        [0b00000, 0b01000, 0b10100, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b01000, 0b10000, 0b10000, 0b10000, 0b01000, 0b00100],
        [0b00000, 0b00100, 0b00010, 0b00001, 0b00001, 0b00001, 0b00010, 0b00100],
        [0b00000, 0b00100, 0b10101, 0b01110, 0b00100, 0b01110, 0b10101, 0b00100],
        [0b00000, 0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100],
        [0b00000, 0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000],
        [0b00000, 0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
        [0b00000, 0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
        [0b00000, 0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00111, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b11100],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010],
        [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000],
        [0b00000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b00010, 0b00100, 0b00100, 0b00000, 0b00100]
    ]
...
```
## How the display works
Rather, it should read: How the emulation of the display works. But that's a quibble. Several points should be considered here: 

- First, the Apple does not build the entire screen at once, or even 50-60 times a second. When a character in the screen RAM changes, a softswitch is triggered, which in turn causes that memory location to be drawn on our virtual screen.
- Secondly, we need an algorithm that calculates the corresponding location. We have already described this above and will use it now.
- Third: The corresponding character from the signetics charset must be drawn on the virtual screen.
- Fourth: Within the game loop of pygame the screen must be updated. 

I decided to draw the single characters on small pygame surfaces, and when a memory cell is changed, to flash them to a pygame surface, which then represents the virtual monitor.

The whole thing is done in the monochrome charm of the 70s 80s - I didn't have money for a color monitor. Most monitors back then were green, mine was amber. A search on the Internet brought this page to light: https://retrocomputing.stackexchange.com/questions/12835/exactly-what-color-was-the-text-on-monochrome-terminals-with-green-on-black-and

I record the values suggested there for green (#33FF33) and amber (#FFB000) and use them as a rough guide. If the colors are too intense, I will adjust the color value. So at this point the emulation is more my personal feeling than a correct color choice. 

I also have to take into account the monitor size or video resolutions of today. A display of 40x24, where each character to be displayed has a resolution of 7x8, resulting in a total resolution of 280x192 pixels, is hardly bigger than a medium button on a web page. Therefore I doubled the display size to 560x384. 

The characters were adjusted as known from the "good old" times: in X-direction I doubled the pixels, in Y-direction I shot in one empty line each to create that well known raster line look.

Here is the new class display.py which only controls normal text mode at the moment:

```bash
import pygame
import numpy
import time

from pygame.locals import *


class Display:

    # Dies ist das Characterset, wie es vom signetics 2513 erzeugt wird.
    # http://www.bitsavers.org/components/signetics/_dataBooks/1972_Signetics_MOS.pdf

    characters = [
        [0b00000, 0b01110, 0b10001, 0b10101, 0b10111, 0b10110, 0b10000, 0b01111],
        [0b00000, 0b00100, 0b01010, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01111, 0b10000, 0b10000, 0b10000, 0b10011, 0b10001, 0b01111],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11111],
        [0b00000, 0b00000, 0b10000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00000],
        [0b00000, 0b11111, 0b00011, 0b00011, 0b00011, 0b00011, 0b00011, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b01010, 0b10001, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
        [0b00000, 0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010],
        [0b00000, 0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
        [0b00000, 0b11000, 0b11001, 0b00010, 0b00100, 0b01000, 0b10011, 0b00011],
        [0b00000, 0b01000, 0b10100, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b01000, 0b10000, 0b10000, 0b10000, 0b01000, 0b00100],
        [0b00000, 0b00100, 0b00010, 0b00001, 0b00001, 0b00001, 0b00010, 0b00100],
        [0b00000, 0b00100, 0b10101, 0b01110, 0b00100, 0b01110, 0b10101, 0b00100],
        [0b00000, 0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100],
        [0b00000, 0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000],
        [0b00000, 0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
        [0b00000, 0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
        [0b00000, 0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00111, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b11100],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010],
        [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000],
        [0b00000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b00010, 0b00100, 0b00100, 0b00000, 0b00100]
    ]

    def __init__(self):
        # auf diese Surface wird anstelle des Screens gezeichnet
        # Die surface wird dann im update_new auf den Screen geblittet und
        # so vergrößert dargestellt
        self.screen = pygame.display.set_mode((560,384))

        self.page = 1
        self.text = True
        self.colour = False
        
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
                inv = False

                self.screen.blit(self.chargen[ch][self.colour][inv], (2 * (column * 7), 2 * (row * 8)))
 
```

To be able to switch between the individual modes Text 1, Lores, Text 2, Hires 1 and Hires 2, softswitches are again necessary. I have provided these in the class softswitches according to the documentation of Woz' Reference Manual, but not yet implemented. 

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
        # elif address == 0xC050:
        #     self.display.txtclr()
        # elif address == 0xC051:
        #     self.display.txtset()
        # elif address == 0xC052:
        #     self.display.mixclr()
        # elif address == 0xC053:
        #     self.display.mixset()
        # elif address == 0xC054:
        #     self.display.lowscr()
        # elif address == 0xC055:
        #     self.display.hiscr()
        # elif address == 0xC056:
        #     self.display.lores()
        # elif address == 0xC057:
        #     self.display.hires()

        else:
            pass
        return 0x00
```

Also, when testing the display class, I could see that the Apple was booting and also beeping, but no prompt appeared. I could not find any error in the display class. After a bit of walking up and down I had an idea: What if the "bus" waits for or accesses the keyboard but gets no response because the keyboard is not yet implemented?

Exactly this was the solution, therefore the softswitches for 0xC000 and 0xC010 are already implemented. Now the Apple boots to the prompt. A keyboard input is not possible yet, we will take care of that in the next version.

![Apple-Boot](/images/apple-boot.png)

The friendly blinking cursor is also still missing. These are points that I will take care of in the meantime. Next on the agenda is the keyboard. Then I will improve and expand the display.

## Main class
The main emulation class, beloved-apple.py, has also undergone some changes. I go into more detail in this section.

```bash
import pygame
import numpy
import time

from pygame.locals import *

from apple2 import Apple2
from speaker import Speaker
from display import Display
from softswitches import SoftSwitches
```

New is the import of the newly created classes, in this case import display... must be added

```bash
import pygame
import numpy
import time

from pygame.locals import *


myApple = Apple2(None)
display = Display()
speaker = Speaker()
softswitches = SoftSwitches(speaker, display, myApple)
update_cycle = 0
update_cycle_bus = 0
quit = False
```

Here the individual I/O blocks are initialized. New is that softswitches gets a reference to the class myApple in addition to the references to the speaker and the display. This is unfortunately necessary, because for the keyboard emulation not only reading is done, but also writing to the bus is required. In the Apple, this is handled by the hardware through the control of gates; in the emulation, this must be done by the software.

```bash
def main():
    global update_cycle
    global quit
    pygame.display.set_caption("CPyU - Jens' Apple Window")
    
    quit = False
    update_cycle = 0
    update_cycle_bus = 0
    while not quit:
        update_new()
```

In order to be able to test different variants of a main loop, I have outsourced the main loops to individual methods. The current one is update_new() - this is also the only one in this source code.

```bash
def update_new():
    global update_cycle
    global update_cycle_bus
    global quit

    # 75% CPU Zeit
    update_cycle_bus += 1
    if update_cycle_bus < 4:
        myApple.cpu.exec_command()
    # 25% I/O Zeit
    else:    
        update_cycle_bus = 0
        # I/O Kanäle laufen über den Speicherbereich 0xc000-0xcfff
        # die Methode write_byte / read_byte überprüft die Adresse und erzeugt ein
        # Datenpaket mit Adresse, Wert und aktuellem Taktzyklus und speichert das
        # in einer queue
        # Hier wird die queue abgearbeitet
        if myApple.memory.bus_queue.qsize() > 0:
            bus_packet = myApple.memory.bus_queue.get()
            bus_cycle = bus_packet.cycle
            bus_address = bus_packet.address
            bus_value = bus_packet.value
            bus_rw = bus_packet.rw

            # wurde vom bus gelesen?
            if bus_rw == 0:
                softswitches.read_byte(bus_cycle, bus_address)
            # oder geschrieben
            elif bus_rw == 1:
                # später kommt hier das display
                display.update(bus_address, bus_value)
                pass

            # alle 1024 Zyklen wird das Display
            # upgedatet und der Lautsprecher abgefragt
            update_cycle += 1
            if update_cycle >= 1024:
                #display.flash()
                pygame.display.flip()
                if speaker:
                    speaker.update(bus_cycle)
                update_cycle = 0

        # Tastatur und Fenster-Funktionen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                print("quit")

if __name__ == "__main__":
    main()
```
