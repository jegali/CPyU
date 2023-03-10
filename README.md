# CPyU - an emulation project for the 6502 CPU

by Jens Gaulke, 2022-2023 <br/><br/>
This is an emulation project for the 6502 CPU, hopefully expanding to the emulation of a complete Apple ][ computer. Started 2022, updated continously
The project is completely written in python.

In order to test the emulation, and also to groove myself for further work on the Apple ][ emulator, I used the Apple ][+ ROM to test the emulation functions. The ROM is available in single pieces here: https://mirrors.apple2.org.za/Apple%20II%20Documentation%20Project/Computers/Apple%20II/Apple%20II%20plus/ROM%20Images/. To assemble the parts, I used Powershell to concatenate the files: 

```bash
cmd /c copy /b part-D0.bin + part-D8.bin + part-E0.bin + ... + part-F8.bin output.bin
```

## Credits
Some 6502 Code came from the ApplePy repository https://github.com/jtauber/applepy of James Tauber http://jtauber.com. The creation of the methods for the individual CPU commands is a diligence task for someone who has slain father and mother - therefore I have helped myself here with jtauber's code and directly removed two more bugs from it.  

## Why Python
I decided to go with python because I wanted a platform independent language for this project. Execution speed of the interpreter should be fast enough to emulate the CPU step by step, and hopefully it is fast enough to emulate a complete computer like the Apple ][.

## Needed libraries
The project makes use of Qt, so PyQt has to be installed. I also used the pyqt-tools and the QT-Designer

```bash
pip install pyqt6
pip install pyqt6-tools
pip install PyQt5Designer
```

## Approach
The project is divided in several subparts I wanted to development independently from another.
Of course I thought about the structure of the project and the functions to be implemented, but the focus here is clearly on the learning factor and not on commercial software development. Therefore, I have deliberately avoided principles like Scrum or iterative models like the waterfall model. It is clear to me that this approach potentially leads to the need to restructure or even redevelop parts of the code. In order to be able to trace the development steps and perhaps even derive a pedagogical concept for an online course from them, I have stored the individual evolutionary stages in subdirectories.

## Used sources
Most of the sources are books about the Apple ][ from the 80s. Some of them I own in print, which I am very proud of, the other sources are either https://mirrors.apple2.org.za/ftp.apple.asimov.net/documentation/ or the massive archive of archive.org, where Ij found for example this Apple ][e as PDF: https://archive.org/details/Inside_the_Apple_IIe. Anyway - the most important books in the creation of the CPU and later also the Apple ][ emulator are:
- Programming the 6502, Rodnay Zaks, https://archive.org/details/Programming_the_6502_OCR
- Inside the Apple IIe, Gary Little, https://archive.org/details/Inside_the_Apple_IIe/mode/2up
- What's where in the Apple, Vol I, found at [amazon](https://www.amazon.de/Whats-Where-APPLE-Enhanced-Guide/dp/1716405270/ref=sr_1_2?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=B45NUY2GW1NW&keywords=what%27s+where+in+the+apple&qid=1676018598&sprefix=what%27s+where+in+the+apple%2Caps%2C77&sr=8-2)
- What's where in the Apple, Vol II, found at [amazon](https://www.amazon.de/Whats-Where-APPLE-Enhanced-Gazetteer/dp/1716405211/ref=sr_1_1?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=B45NUY2GW1NW&keywords=what%27s+where+in+the+apple&qid=1676018598&sprefix=what%27s+where+in+the+apple%2Caps%2C77&sr=8-1)
- The Apple II circuit description, Winston Gayler, https://archive.org/details/apple-ii-circuit-description
- Understanding the Apple II, Jim Sather, https://archive.org/details/understanding_the_apple_ii
- Apple Assembly Lines: The coplete Book, https://ia600304.us.archive.org/9/items/AssemblyLinesCompleteWagner/AssemblyLinesCompleteWagner.pdf

I am very interested in seeing the last two books (Gayler & Sather) as print on my bookshelf. If you want to help me, I would be very pleased. I will also gladly accept donations to my paypal account to purchase these books. Send money to jens@jensgaulke.de.

## Status
2022-12-08: I started developing the [disassemble unit](https://github.com/jegali/CPyU/tree/main/Disassembler)<br/>
2022-12-09: [Disassembler V1](https://github.com/jegali/CPyU/tree/main/Disassembler/v1) - Designed the UI for the disassemble unit with QT Designer<br/>
2022-12-10: [Disassembler V2](https://github.com/jegali/CPyU/tree/main/Disassembler/v2) - Implemented a command line parser module for disassembling<br/>
2022-12-11: [Disassembler V3](https://github.com/jegali/CPyU/tree/main/Disassembler/v3) - Optimizied the command line parser module for disassembling<br/>
2022-12-12: [Disassembler V4](https://github.com/jegali/CPyU/tree/main/Disassembler/v4) - Integrated the cmd version with a GUI<br/>
2022-12-13: I started developing the [assembly unit](https://github.com/jegali/CPyU/tree/main/Assembler)<br/>
2022-12-14: [Assembler V1](https://github.com/jegali/CPyU/tree/main/Assembler/v1) - Designed the UI for the disassemble unit with QT Designer<br/>
2022-12-14: [Assembler V2](https://github.com/jegali/CPyU/tree/main/Assembler/v2) - Wrote the Assemble unit<br/>
2022-12-28: Changed the Qt PlainTextEdit for the QScintilla component<br/>
2022-12-29: Started creating the [Emulator View](https://github.com/jegali/CPyU/tree/main/CPU)<br/>
2022-12-30: Created the RAM, the ROM and memory classes<br/>
2022-12-31: Created the menu functionality and learned how to open more windows and pass data to them<br/> 
2023-01-27: Started this repository and wrote the documentation<br/>
2023-02-04: [Disassembler V5](https://github.com/jegali/CPyU/tree/main/Disassembler/v5) - Changed the disassembly unit to make use of lambda functions<br/>
2023-02-05: [Disassembler V6](https://github.com/jegali/CPyU/tree/main/Disassembler/v6) - Extended the disassembly unit to disassemble single commands.<br/>
2023-02-06: [Disassembler V6](https://github.com/jegali/CPyU/tree/main/Disassembler/v6) - disassembler works as a submodule of EmulatorWindow<br/>
2023-02-06: Updated the RAM, the RAM and memory classes and implemented single step emulation [CPU v2](https://github.com/jegali/CPyU/blob/main/CPU/v2)<br/>
2023-02-06: Switched the Emulation from step to pygame [CPU v3](https://github.com/jegali/CPyU/blob/main/CPU/v3)<br/>
2023-02-07: Implemented the speaker [CPU v4](https://github.com/jegali/CPyU/blob/main/CPU/v4)<br/>
2023-02-08: Implemented the bus struct and updated the memory class [CPU v4](https://github.com/jegali/CPyU/blob/main/CPU/v4)<br/>
2023-02-09: Implemented the softswitches and changed the main emulation loop [CPU v4](https://github.com/jegali/CPyU/blob/main/CPU/v4)<br/>
2023-02-10: Implemented the Display and the font [CPU v5](https://github.com/jegali/CPyU/blob/main/CPU/v5)<br/>
2023-02-11: Implemented the keyboard emulation [CPU v6](https://github.com/jegali/CPyU/blob/main/CPU/v6)<br/>
2023-02-12: Enhanced the display - flash, lores, hires [CPU v7](https://github.com/jegali/CPyU/blob/main/CPU/v7)<br/>
2023-02-14: Implemented a clipboard function to be able to paste source code to the apple [CPU v8](https://github.com/jegali/CPyU/blob/main/CPU/v8)<br/>

## Which functions should the emulation possess
- ~~Basic Disassembler~~
- ~~Step by Step disassembling~~
- ~~Basic Assembler~~
- ~~Basic GUI for emulation~~
- ~~6502 emulation~~
- ~~Woz' ROM Emulation~~
- ~~Speaker emulation~~
- Testing speaker functionality in games
- ~~Keyboard Emulation~~
- ~~Clipboard functionality~~
- Cassette Emulation
- Disk Emulation
- ~~Text Display Emulation~~
- ~~LoRes Display Emulation~~
- ~~HiRes Display Emulation~~
- Extension Slot Emulation
