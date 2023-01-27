# Command-line disassembler
Before I tackled the graphical version of the disassembler, I had already created a command line version. This version can be found in this directory and will be presented here.<br/><br/>
To be able to test the finished program version, I disassembled the Apple ][ Rom and compared it with the book in which it was printed at that time. I found the Rom version here:

https://mirrors.apple2.org.za/ftp.apple.asimov.net/emulators/rom_images/

For the later emulation it is important that it is a Rom that is 12 KB in size. This should be taken into account when downloading.

## Error handling in the command line version
In order to make the program user-friendly, it was important to me to react adequately to incorrect user input. The only possibility of interaction with the user is when the program is called. Therefore the error sources lie exclusively in the passing of the appropriate parameters with the call. For the handling of user input Python provides the helpful class argparse.
