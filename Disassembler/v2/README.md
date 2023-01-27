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

With this it should be clear: a table, which translates each bytecode into the corresponding mnemonic (opcode) and ideally provides additional information like address mode, description and clock cycles, is the actual main part of the disassembler. In this version of the disassembler this is solved somewhat awkwardly but understandably - in the following versions we will optimize this. The cycle-table is not yet valid and contains only 1 cycle per instruction. That would be nice, but is totally ridiculous.

```bash
mnemonics = [
    "BRK", "ORA", "???", "???", "TSB", "ORA", "ASL", "???", "PHP", "ORA", "ASL", "???", "TSB", "ORA", "ASL", "???",
    "BPL", "ORA", "ORA", "???", "TRB", "ORA", "ASL", "???", "CLC", "ORA", "INC", "???", "TRB", "ORA", "ASL", "???",
    "JSR", "AND", "???", "???", "BIT", "AND", "ROL", "???", "PLP", "AND", "ROL", "???", "BIT", "AND", "ROL", "???",
    "BMI", "AND", "AND", "???", "BIT", "AND", "ROL", "???", "SEC", "AND", "DEC", "???", "BIT", "AND", "ROL", "???",
    "RTI", "EOR", "???", "???", "???", "EOR", "LSR", "???", "PHA", "EOR", "LSR", "???", "JMP", "EOR", "LSR", "???",
    "BVC", "EOR", "EOR", "???", "???", "EOR", "LSR", "???", "CLI", "EOR", "PHY", "???", "???", "EOR", "LSR", "???",
    "RTS", "ADC", "???", "???", "STZ", "ADC", "ROR", "???", "PLA", "ADC", "ROR", "???", "JMP", "ADC", "ROR", "???",
    "BVS", "ADC", "ADC", "???", "STZ", "ADC", "ROR", "???", "SEI", "ADC", "PLY", "???", "JMP", "ADC", "ROR", "???",
    "BRA", "STA", "???", "???", "STY", "STA", "STX", "???", "DEY", "BIT", "TXA", "???", "STY", "STA", "STX", "???",
    "BCC", "STA", "STA", "???", "STY", "STA", "STX", "???", "TYA", "STA", "TXS", "???", "STZ", "STA", "STZ", "???",
    "LDY", "LDA", "LDX", "???", "LDY", "LDA", "LDX", "???", "TAY", "LDA", "TAX", "???", "LDY", "LDA", "LDX", "???",
    "BCS", "LDA", "LDA", "???", "LDY", "LDA", "LDX", "???", "CLV", "LDA", "TSX", "???", "LDY", "LDA", "LDX", "???",
    "CPY", "CMP", "???", "???", "CPY", "CMP", "DEC", "???", "INY", "CMP", "DEX", "???", "CPY", "CMP", "DEC", "???",
    "BNE", "CMP", "CMP", "???", "???", "CMP", "DEC", "???", "CLD", "CMP", "PHX", "???", "???", "CMP", "DEC", "???",
    "CPX", "SBC", "???", "???", "CPX", "SBC", "INC", "???", "INX", "SBC", "NOP", "???", "CPX", "SBC", "INC", "???",
    "BEQ", "SBC", "SBC", "???", "???", "SBC", "INC", "???", "SED", "SBC", "PLX", "???", "???", "SBC", "INC", "???"
]

adressmode = [
    'imp', 'inx', 'imp', 'imp', 'imp', 'zpg', 'zpg', 'imp', 'imp', 'imm', 'acc', 'imp', 'imp', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'imp', 'zpx', 'zpx', 'imp', 'imp', 'aby', 'imp', 'imp', 'imp', 'abx', 'abx', 'imp',
    'abs', 'inx', 'imp', 'imp', 'zpg', 'zpg', 'zpg', 'imp', 'imp', 'imm', 'acc', 'imp', 'abs', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'imp', 'zpx', 'zpx', 'imp', 'imp', 'aby', 'imp', 'imp', 'imp', 'abx', 'abx', 'imp',
    'imp', 'inx', 'imp', 'imp', 'imp', 'zpg', 'zpg', 'imp', 'imp', 'imm', 'acc', 'imp', 'abs', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'imp', 'zpx', 'zpx', 'imp', 'imp', 'aby', 'imp', 'imp', 'imp', 'abx', 'abx', 'imp',
    'imp', 'inx', 'imp', 'imp', 'imp', 'zpg', 'zpg', 'imp', 'imp', 'imm', 'acc', 'imp', 'ind', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'imp', 'zpx', 'zpx', 'imp', 'imp', 'aby', 'imp', 'imp', 'imp', 'abx', 'abx', 'imp',
    'imp', 'inx', 'imp', 'imp', 'zpg', 'zpg', 'zpg', 'imp', 'imp', 'imp', 'imp', 'imp', 'abs', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'zpx', 'zpx', 'zpy', 'imp', 'imp', 'aby', 'imp', 'imp', 'imp', 'abx', 'imp', 'imp',
    'imm', 'inx', 'imm', 'imp', 'zpg', 'zpg', 'zpg', 'imp', 'imp', 'imm', 'imp', 'imp', 'abs', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'zpx', 'zpx', 'zpy', 'imp', 'imp', 'aby', 'imp', 'imp', 'abx', 'abx', 'aby', 'imp',
    'imm', 'inx', 'imp', 'imp', 'zpg', 'zpg', 'zpg', 'imp', 'imp', 'imm', 'imp', 'imp', 'abs', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'imp', 'zpx', 'zpx', 'imp', 'imp', 'aby', 'imp', 'imp', 'imp', 'abx', 'abx', 'imp',
    'imm', 'inx', 'imp', 'imp', 'zpg', 'zpg', 'zpg', 'imp', 'imp', 'imm', 'imp', 'imp', 'abs', 'abs', 'abs', 'imp',
    'rel', 'iny', 'imp', 'imp', 'imp', 'zpx', 'zpx', 'imp', 'imp', 'aby', 'imp', 'imp', 'imp', 'abx', 'abx', 'imp' 
]

adressmode2 = [
    'Implicit', 'X Indexed, indirect', 'Implicit', 'Implicit', 'Implicit', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Immediate', 'Accumulator', 'Implicit', 'Implicit', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Absolute, X Indexed', 'Implicit',
    'Absolute', 'X Indexed, indirect', 'Implicit', 'Implicit', 'Zero Page', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Immediate', 'Accumulator', 'Implicit', 'Absolute', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Absolute, X Indexed', 'Implicit',
    'Implicit', 'X Indexed, indirect', 'Implicit', 'Implicit', 'Implicit', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Immediate', 'Accumulator', 'Implicit', 'Absolute', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Absolute, X Indexed', 'Implicit',
    'Implicit', 'X Indexed, indirect', 'Implicit', 'Implicit', 'Implicit', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Immediate', 'Accumulator', 'Implicit', 'Indirect', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Absolute, X Indexed', 'Implicit',
    'Implicit', 'X Indexed, indirect', 'Implicit', 'Implicit', 'Zero Page', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Implicit', 'Implicit', 'Implicit', 'Absolute', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Zero Page, Y Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Implicit', 'Implicit',
    'Immediate', 'X Indexed, indirect', 'Immediate', 'Implicit', 'Zero Page', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Immediate', 'Implicit', 'Implicit', 'Absolute', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Zero Page, Y Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Absolute, X Indexed', 'Absolute, Y Indexed', 'Implicit',
    'Immediate', 'X Indexed, indirect', 'Implicit', 'Implicit', 'Zero Page', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Immediate', 'Implicit', 'Implicit', 'Absolute', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Absolute, X Indexed', 'Implicit',
    'Immediate', 'X Indexed, indirect', 'Implicit', 'Implicit', 'Zero Page', 'Zero Page', 'Zero Page', 'Implicit', 'Implicit', 'Immediate', 'Implicit', 'Implicit', 'Absolute', 'Absolute', 'Absolute', 'Implicit',
    'Relative', 'Indirect, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Zero Page, X Indexed', 'Zero Page, X Indexed', 'Implicit', 'Implicit', 'Absolute, Y Indexed', 'Implicit', 'Implicit', 'Implicit', 'Absolute, X Indexed', 'Absolute, X Indexed', 'Implicit' 
]

zyklen = [
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", 
    "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1" 
]
```

## The main program loop
The main loop of the program now reads the assembler file byte by byte. During processing, the program proceeds strictly according to the von Neumann principle:

- Fetch
- Decode
- Execute

In the fetch phase, the byte is read and the command behind it is read from the table. What the respective command does is the task of the decode phase. In the decode phase it is also examined which address mode the command is based on and how many bytes (operands or address) it requires for its processing. The execute phase becomes important only in the emulation and is neglected here. Instead, console output is generated in the fetch and decode phases and the output is written to a text file. This describes the basic task of the disassembler.

```bash
# Es können Dateien beliebiger Länge gelesen werden - 
# daher eine While-Schleife

while True:

    # Lies ein Byte aus dem Assemblertext ein
    bytecode = input_file.read(1)
    if not bytecode:
        break

    # Schreibe die Adresse
    address_str = hex(address)[2:].upper().zfill(4) + "\t"
    output_file.write(address_str)
    address += 1

    # Decodiere den Opcode 
    opcode = int.from_bytes(bytecode, byteorder='little', signed=False)
    # Byte in Hex umwandeln
    # 0x entfernen, entweder durch replace() oder [2:]
    # in Großbuchstaben umwandeln
    # mit führenden Nullen auffüllen, falls notwendig
    hexcode = hex(opcode)[2:].upper().zfill(2)
    # und in die Datei schreiben
    output_file.write(hexcode + " ")

    # Die Adressmodi Implizit und Akkumulator bestehen nur 
    # aus einem Byte und haben keine Operanden oder Adressen
    if adressmode[opcode] == "imp":
        output_file.write("\t\t" + mnemonics[opcode] + "\t")
        output_file.write("\t\t" + adressmode2[opcode] + "\t")
        output_file.write(zyklen[opcode] + "\t")
        output_file.write("\n")
        continue    # nächster Befehl

    if adressmode[opcode] == "acc":
        output_file.write("\t\t" + mnemonics[opcode] + "\t")
        output_file.write("\t\t" + adressmode2[opcode] + "\t")
        output_file.write(zyklen[opcode] + "\t")
        output_file.write("\n")
        continue    # nächster Befehl


    # nach dem Opcode den (ersten) Operanden lesen
    bytecode = input_file.read(1)
    if not bytecode:
        print("FEHLER: Datei unerwarterweise zu Ende")
        break

    operand = int.from_bytes(bytecode, byteorder='little', signed=False)
    hexcode = hex(operand)[2:].upper().zfill(2)
    # und in die Datei schreiben
    output_file.write(hexcode)
    address += 1

    # nun den Befehl auswerten
    # Immediate
    if adressmode[opcode] == "imm":
        output_file.write("\t\t" + mnemonics[opcode] + " #$" + hexcode + "\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # Relative
    if adressmode[opcode] == "rel":
        output_file.write("\t\t" + mnemonics[opcode] + " $" + hexcode + "  \t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # Zero Page
    if adressmode[opcode] == "zpg":
        output_file.write("\t\t" + mnemonics[opcode] + " $" + hexcode + "  \t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # Zero Page, X indexed
    if adressmode[opcode] == "zpx":
        output_file.write("\t\t" + mnemonics[opcode] + " $" + hexcode + ",X\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # Zero Page, Y indexed
    if adressmode[opcode] == "zpy":
        output_file.write("\t\t" + mnemonics[opcode] + " $" + hexcode + ",Y\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # X indexed, indirect
    if adressmode[opcode] == "inx":
        output_file.write("\t\t" + mnemonics[opcode] + " $(" + hexcode + ",X)\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # indirect, Y indexed
    if adressmode[opcode] == "iny":
        output_file.write("\t\t" + mnemonics[opcode] + " $(" + hexcode + "),Y\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # Nun sind noch alle Befehle übrig, die ein weiteres Byte
    # (also ingesamt 3 Bytes) für den Befehl beanspruchen

    # nach dem Opcode den (zweiten) Operanden lesen
    bytecode = input_file.read(1)
    if not bytecode:
        print("FEHLER: Datei unerwarterweise zu Ende")
        break

    operand2 = int.from_bytes(bytecode, byteorder='little', signed=False)
    hexcode2 = hex(operand2)[2:].upper().zfill(2)
    # und in die Datei schreiben
    output_file.write(" " + hexcode)
    hexcode = hexcode2 + hexcode
    address += 1

    # nun den Befehl auswerten
    # Indirect
    if adressmode[opcode] == "ind":
        output_file.write("\t" + mnemonics[opcode] + " $(" + hexcode + ")\t")
        output_file.write("\t\t" + adressmode2[opcode] + "\n")
        continue

    # Absolute
    if adressmode[opcode] == "abs":
        output_file.write("\t" + mnemonics[opcode] + " $" + hexcode + "\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue
    
    # Absolute, X indexed
    if adressmode[opcode] == "abx":
        output_file.write("\t" + mnemonics[opcode] + " $" + hexcode + ",X\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue

    # Absolute, Y indexed
    if adressmode[opcode] == "aby":
        output_file.write("\t" + mnemonics[opcode] + " $" + hexcode + ",Y\t")
        output_file.write("\t" + adressmode2[opcode] + "\n")
        continue    

    output_file.write("\n")

input_file.close()
output_file.close()
```
