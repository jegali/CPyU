# CPU
In this folder the emulation of the 6502 CPU is created. The subprojects [Disassembler](https://github.com/jegali/CPyU/tree/main/Disassembler) and [Assembler](https://github.com/jegali/CPyU/tree/main/Assembler) were only the first step towards the emulation.

I designed this module directly in Qt Designer without going through a console application. To emulate the CPU, I created another program window that can open the disassembler and assembler window if needed.

The following figure shows the program window. The interface is not yet fully developed, more an accumulation of "functions" that can be called via buttons and menu items.

![CPU-v1](/images/emulator-v1.png)

## Status
This part of the application in particular is still in development. Therefore, there will always be changes before new versions are released. Each subfolder in this directory represents its own version. The development of the CPU module is chronologically from V1, V2, ... , Vn.

### V1
This version represents the basic framework of the application. Using QT Designer, the graphical user interface was created and converted into executable Python source code by pyuic6.

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/CPU/v1)

### V2
This version extends the basic classes RAM, ROM and Memory with methods for handling words, which are needed for address access. A view for the currently edited command has been added. The emulation is able to execute individual commands at the push of a button. The methods for the emulation of the address modes and the opcodes have been implemented.

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/CPU/v2)

### V3
The step-by-step emulation from V2 showed me where there were still bugs in the code, as Python pointed out the errors very elegantly and with extensive stacktrace. After I fixed these bugs and the emulation ran stable over many steps, I wrote a routine to run the emulation "by itself and all the time". There were no more error messages, however this approach is unfortunately too slow for a real emulation. Therefore I wrote V3. 

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/CPU/v3)

### V4 
Let's talk about the speaker here

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/CPU/v4)

### V5
The display is also a tough nut to crack. Or ingeniously solved. In any case, it is worth a look. Here is the basic emulation of the display, at the moment for text mode.

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/CPU/v5)

### V6
Although the keayboard was the first thing I dealt with, I mention it only at this point. For didactic reasons it would not have made sense further ahead - without the possibility to see something. .

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/CPU/v6)
