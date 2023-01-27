# Command-line disassembler
Before I tackled the graphical version of the disassembler, I had already created a command line version. This version can be found in this directory and will be presented here.<br/><br/>
To be able to test the finished program version, I disassembled the Apple ][ Rom and compared it with the book in which it was printed at that time. I found the Rom version here:

https://mirrors.apple2.org.za/ftp.apple.asimov.net/emulators/rom_images/

For the later emulation it is important that it is a Rom that is 12 KB in size. This should be taken into account when downloading.

## Error handling in the command line version
In order to make the program user-friendly, it was important to me to react adequately to incorrect user input. The only possibility of interaction with the user is when the program is called. Therefore the error sources lie exclusively in the passing of the appropriate parameters with the call. For the handling of user input Python provides the helpful class argparse.<br/>

The following code represents the check of the input parameters - sorry, the error handling is german for my convenience:

```bash
from argparse import ArgumentParser

import sys

# Den Parser initialisieren
parser = ArgumentParser()
# Die Option für die Eingabedatei festlegen
parser.add_argument("-i", type=str, help="Die Eingabedatei zum Disassemblieren. apple2.rom ist default", required=True)
# Die Option für die Ausgabedatei festlegen
parser.add_argument("-o", type=str, help="stdout, falls kein Dateiname angegeben wird", required=False)
# Die Startadresse für das Listing festlegen. Das AppleRom begint bei f800
parser.add_argument("-a", type=str, help="Adresse als Hexadezimalzahl (D000 als Beispiel für Apple II)", required=False)

cmdargs = parser.parse_args()

# Ausgabedatei festlegen
if cmdargs.o:
    try:
        output_file = open("dis.txt", "x")
    except OSError as e:
        print("FEHLER: Datei existiert bereits")
        exit(1)
else:
    output_file = sys.stdout

# Eingabedatei festlegen
if cmdargs.i:
    try:
        input_file = open(cmdargs.i, "rb")
    except OSError as e:
        print("FEHLER: Eingabedatei konnte nicht geöffnet werden: " + cmdargs.i)
        exit(1)
else:
    input_file = sys.stdin

# Startadresse festlegen
if cmdargs.a:
    address = int(cmdargs.a, 16)
else:
    address = 0
```

## The translation table
The following lines are from the page https://dewiki.de/Lexikon/Disassembler
and shall briefly describe the functionality of a disassembler:

"A disassembler is a computer program that converts the binary-coded machine language of an executable program into a more human-readable assembly language. Its functionality is opposite to that of an assembler.

For each processor instruction there exists a corresponding instruction in assembly language, a mnemonic. Also the individual arguments of the processor instructions, like register numbers or memory addresses, can be transferred one to one into assembly code. So a disassembler translates the binary representations of the processor instructions back into human readable assembly language.

In the case of a program written in assembler, the original code can generally not be restored afterwards in the original text, but only functionally the same. Pseudo instructions, labels and comments are chosen by the programmer and therefore have at least no direct, i.e. clearly reversible, equivalent in the machine code, which makes exact textual reconstruction impossible. With a program, which was written in a higher programming language, the compiler usually made various optimizations, which accelerate the program execution, but make the machine code more complex.

A disassemblat is thus usually clearly worse readable than the original assembler code. Also for this reason it is meaningful and usual with more complex program sections to make the Disassemblierung not in a single run fully automatic, but in repetitions with manual intermediate steps. Here from gradual experience and realization increasingly identifiers for jump marks, subroutines, variables, constants as well as comments can be refined manually and specified for optimization in subsequent runs."

With this it should be clear: a table, which translates each bytecode into the corresponding mnemonic (opcode) and ideally provides additional information like address mode, description and clock cycles, is the actual main part of the disassembler.
