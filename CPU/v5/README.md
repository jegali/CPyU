# Display
Last status: The emulation of the Apple rom is running and it beeps at startup. Now, of course, 
it would be nice to have an output on the screen as well. Spoiler in advance: The display of the video output is anything but simple...

## The RAM layout
Before we can look at how the graphics output looks in the Apple ][, it makes sense to look at the RAM layout of the Apple. The following lines are from the book "Inside the Apple IIe" by Gary Little:

"The area of RAM memory that is most often used on the //e extends from locations $0000 to $BFFF and is contained in eight memory chips built in to the system motherboard. As indicated in Figure 2-3, some regions within this range are dedicated for special uses. Here is a summary of the usage of the internal (or 'main') RAM memory locations:
• $0000-$00FF. This is the 6502 zero page and it is used exten- sively by all parts of the lie's operating system, including the system monitor (see Chapter 3), the Applesoft interpreter (see Chapter 4), and the disk operating system (see Chapter 5). Those locations available for use by your own programs are set out in Table 2-5.
• $0100-$01FF. This is the 6502 stack area and is also used for temporary data storage by the Applesoft interpreter (see Chap- ter 4).
• $0200-$02FF. This area of memory is normally used as an input buffer whenever character information is entered from the key- board or from diskette (see Chapter 6).
• $0300-$03CF. This area of memory is not used by any of the built-iil programs in the lie and so is available for use by your own programs. It is an ideal location for storing small assem- bly-language programs that are called from Applesoft and most of the examples presented in this book are to be loaded here.
• $03D0-$03FF. This area of memory is used by the disk oper- ating system, Applesoft, and the system monitor for the pur- pose of storing position-independent vectors to important sub- routines that can be located anywhere in memory (such as interrupt-handling subroutines). See Appendix IV for a com- plete description of how this area is used.
• $0400-$07FF. This is pagel of video memory that is used for displaying both the primary text screen and the primary low- resolution graphics screen (see Chapter 7). It is also used for displaying one-half of the text screen when in 80-column mode.
• $0800-$0BFF. This is page2 of video memory that is used for displaying both the secondary text screen and the secondary low-resolution graphics screen (see Chapter 7). Since page2 is rarely used, this area of memory is normally used for program storage; in fact, the default starting position for an Applesoft program is $801.
• $0C00-$1FFF. This area of memory is free for use.
• $2000-$3FFF. This is pagel of video memory that is used for displaying the primary high-resolution graphics screen (see Chapter 7).
• $4000-$5FFF. This is page2 of video memory that is used for displaying the secondary high-resolution graphics screen (see Chapter 7).


## How the display works

