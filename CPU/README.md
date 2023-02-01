# CPU
In this folder the emulation of the 6502 CPU is created. The subprojects [Disassembler](https://github.com/jegali/CPyU/tree/main/Disassembler) and [Assembler](https://github.com/jegali/CPyU/tree/main/Assembler) were only the first step towards the emulation.

I designed this module directly in Qt Designer without going through a console application. To emulate the CPU, I created another program window that can open the disassembler and assembler window if needed.

The following figure shows the program window. The interface is not yet fully developed, more an accumulation of "functions" that can be called via buttons and menu items.

![CPU-v1](/images/emulator-v1.png)
