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

For the display the available memory of 1024 Bytes is chunked into 128 bytes. Each of these 128 byte chunks is divided into three 40 byte areas representing one line. The remaining 8 bytes (3 x 40 = 120) serve as scratchpad. However, the three 40-byte blocks are not in consecutive lines. The following table shows the structure of the display and the memory arrangement. As said, Woz had to save transistor gates when creating the Apple II, and the multiplexer circuit he designed just delivered this result.

![display-memory](/images/display-memory-layout.png)

## How the display works

