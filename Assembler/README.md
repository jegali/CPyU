# Assembler
The creation of the assembler was the logical consequence after the completion of the disassembler. In principle, an assembler does the exact opposite of a disassembler. It translates the mnemonics into the bytecode which can be processed by the processor.

The page https://www.dev-insider.de/was-ist-ein-assembler-a-756636/ knows about assemblers: 

"An assembler translates code written in assembly language directly into binary code, where the code may be manual or machine-generated. For example, some compilers first convert program code into assembly code and then call an assembler. This in turn acts as a compiler itself and creates the machine code as a final step.

Assembler programs can use the complete instruction set of a processor, because for each assembler instruction there is exactly one counterpart at machine level. Modern high-level languages, on the other hand, are limited to a selection from the instruction set. Therefore, some languages offer the possibility to integrate assembler code if required.

Each processor has its own architecture and its own instruction set with which it can be addressed. Therefore each processor needs its own assembler including its own assembly language.

Only code written in this language can be understood and translated by the corresponding assembler. A program for processor A can therefore not be used by processor B without modifications - assembler programs are strongly platform dependent. In some cases, individual assembly languages differ only minimally."

## Prerequisites
As inspiration I used the disassembler/assembler/emulator from Masswerk, which is available on the internet and can be found at https://www.masswerk.at/6502/assembler.html.

![Masswerk_Disassembler](/images/masswerk-assembler.png)

I rebuilt the interface in PyQT. For that, you have to install PyQT6 via the pip command in Powershell or terminal under MacOS / Linux. Interestingly enough, the PyQT-install also installs a tool called pyuic (pyuic6 for version 6) and a version of the qt-designer. The designer is used to build the GUI and pyuic is used to transform the GUI-Metadata to python code. Pyuic is not installed on the main path under Windows, but during the install you are informed where the file is stored.

For more information on istannling the python libryries and extensions have a look at the disassembler section of this project:
https://github.com/jegali/CPyU/tree/main/Disassembler

## Status
this part of the project has a long history. Each subfolder in this directory represents its own version. The development of the assembler module is chronologically from V1, V2, ... , Vn.

### V1
This version represents the basic framework of the application. Using QT Designer, the graphical user interface was created and converted into executable Python source code by pyuic6.

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/Assembler/v1)

### V2
This version concludes the basis asssembly unit. The UI was changed to include the qscintilla component, the code was rewritten two times to the actual state.

[Go to the directory here](https://github.com/jegali/CPyU/tree/main/Assembler/v2)
