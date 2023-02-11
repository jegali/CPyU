# Display
Last status: The emulation of the Apple rom is running and it beeps at startup. Now, of course, 
it would be nice to have an output on the screen as well. Spoiler in advance: The display of the video output is anything but simple...

## The RAM layout
Before we can look at how the graphics output looks in the Apple ][, it makes sense to look at the RAM layout of the Apple. The following lines are from the book "Inside the Apple IIe" by Gary Little:

"The area of RAM memory that is most often used on the //e extends from locations $0000 to $BFFF and is contained in eight memory chips built in to the system motherboard. As indicated in Figure 2-3, some regions within this range are dedicated for special uses. Here is a summary of the usage of the internal (or 'main') RAM memory locations:
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

The motherboard also contains an additional 16K of RAM mem- ory that is located from $D000 to $FFFF (the 4K block from $D000 to $DFFF is duplicated). The ProDOS disk operating system oc- cupies most of this area but if DOS 3.3 is being used, this area is free for use by a program. This 16K area is called bank-switched RAM and will be discussed in detail in Chapter 8.
If you have a standard 80-column text card installed in the aux- iliary slot of the lie, another IK of RAM memory suddenly becomes available to the 6502. This memory extends from $400 to $7FF and is used to support the lie's special 80-column text display mode and double-width low-resolution graphics mode (see Chapter 7).
If an extended 80-column text card is in the auxiliary slot, then a total of 64K of auxiliary RAM memory is added to the lie. This memory occupies the same address spaces as the 64K of built-in RAM memory and so can be thought of as a "twin" memory space. There are slight differences, however, in how some of the areas within this memory are interpreted. For example, the two memory areas corresponding to the page2 video areas in main memory are not reserved for those purposes in auxiliary memory. Furthermore, the two areas corresponding to page! video areas are not used for video display purposes unless 80-column text mode is active or unless a double-width graphics mode is active. These differences will be discussed in greater detail in Chapter 7.

The lie's I/O memory space corresponds to those addresses from $C000 to $C0FF. Although these addresses may be read from or written to in exactly the same way as normal RAM or ROM memory locations, there is no memory stored at these locations. Instead, whenever these locations are accessed, a physical change in the system can be effected (e.g., the graphics display can be turned on, the character set can be changed, or the disk drive motor can be turned on), the status of an I/O device can be read, or data can be transferred to or from the I/O device. This method of handling I/O operations is called memory-mapped I/O.
For example, consider the lie's keyboard. The keyboard has been wired into the system in such a way that it can be be controlled by using the locations $C000 and $C010 (see Chapter 6). To deter- mine whether a key has been entered, address $C000 is examined; if bit 7 at this "location" (the keyboard strobe bit) is 1, then a key has indeed been entered. Address $C010 is accessed to clear the keyboard strobe bit. Even though an address is referred to in order to read and clear the keyboard, there is no memory chip on the //e that corresponds to this address.
All of the //e's I/O memory locations will be discussed in later chapters. A summary of the meaning of each of these locations is contained in Appendix III.

As you can see from Figure 2-4, ROM memory on the //e extends from locations $C100 to $FFFF. However, part of this memory space (from $C100 to $CFFF) is duplicated: one area represents built-in internal ROM, and the other represents memory contained on devices connected to the //e's seven peripheral slots. Here is a summary of ROM memory usage:

- **$C100-$C7FF**. This is the peripheral-card ROM space. One page of ROM is reserved for use at each slot: $C100 . . . $C1FF for slot 1, $C200 . . . $C2FF for slot 2, and so on (see Chapter 11).
- **$C800-$CFFF**. This is the peripheral-card expansion ROM space. Each peripheral card can contain a block of memory that uses these addresses (see Chapter 11).
- **$C100-$CFFF**. This is the internal 80-column firmware ROM that contains extensions to the system monitor, subroutines to support the 80-column text display, and self-test subroutines.
- **$D000-$F7FF**. This is the Applesoft ROM space (see Chapter 4).
- **$F800-$FFFF**. This is the standard system monitor ROM space (see Chapter 3).


## How the display works

