# The enhanced commandline version
The first version of the disassembler consisted of several conversion tables. In this version I consolidated the tables and made the project a bit clearer. I report about the changes in the next section.

## Starting the disassembler
Nothing has changed in the call of the disassembler and its function and the possible command line parameters. It has an integrated help function which you can see in the next screenshot.

![Disassembler_CMD](/images/6502-cmd-disasm.png)

## The translation table
This is where the main and most important change has taken place. The conversion tables have been consolidated and are now in one list. The individual indices of the list correspond thereby to the valid mnemonics and contain the valid clock cycles, the name of the processor instruction, the address mode in short form and long form as well as a plain text description of the instruction for better understanding of the disassemblat.

```bash
# Taktzyklen, Befehlsname, Adressmodus, Adressmodus ausführlich, Beschreibung
operations = [(1,"???", "imp", " ", " ")] * 0x100
operations[0x00] = (7, "BRK", "imp", "Implicit", "Break (force interrupt)")
operations[0x01] = (6, "ORA", "inx", "X Indexed, indirect", "OR to A")
operations[0x05] = (3, "ORA", "zpg", "Zero Page", "OR to A")
operations[0x06] = (5, "ASL", "zpg", "Zero Page", "Arithmetic shift left")
operations[0x08] = (3, "PHP", "imp", "Implicit", "Push P onto stack")
operations[0x09] = (2, "ORA", "imm", "Immediate", "OR to A")
operations[0x0A] = (3, "ASL", "acc", "Accumulator", "Airthmetic shift left")
operations[0x0D] = (4, "ORA", "abs", "Absolute", "OR to A")
operations[0x0E] = (6, "ASL", "abs", "Absolute", "Arithmetics shift left")
operations[0x10] = (2, "BPL", "rel", "Relative", "Branch if plus (N=0)")
operations[0x11] = (5, "ORA", "iny", "Indirect, Y Indexed", "OR to A")
operations[0x15] = (4, "ORA", "zpx", "Zero Page, X Indexed", "OR to A")
operations[0x16] = (6, "ASL", "zpx", "Zero Page, X Indexed", "Arithmetic shift left")
operations[0x18] = (2, "CLC", "imp", "Implicit", "Clear carry")
operations[0x19] = (4, "ORA", "aby", "Absolute, Y Indexed", "OR to A")
operations[0x1D] = (4, "ORA", "abx", "Absolute, X Indexed", "OR to A")
operations[0x1E] = (7, "ASL", "abx", "Absolute, X Indexed", "Arithmetic shift left")
operations[0x20] = (6, "JSR", "abs", "Absolute", "Jump to subroutine")
operations[0x21] = (6, "AND", "inx", "X Indexed, Indirect", "AND to A")
operations[0x24] = (3, "BIT", "zpg", "Zero Page", "AND with A (A unchanged)")
operations[0x25] = (3, "AND", "zpg", "Zero Page", "AND to A")
operations[0x26] = (5, "ROL", "zpg", "Zero Page", "Rotate left through carry")
operations[0x28] = (4, "PLP", "imp", "Implicit", "Pop P from Stack")
operations[0x29] = (2, "AND", "imm", "Immediate", "And to A")
operations[0x2A] = (3, "ROL", "acc", "Accumulator", "Rotate left")
operations[0x2C] = (4, "BIT", "abs", "Absolute", "AND with A (A unchanged)")
operations[0x2D] = (4, "AND", "abs", "Absolute", "AND to A")
operations[0x2E] = (6, "ROL", "abs", "Absolute", "Rotate left")
operations[0x30] = (2, "BMI", "rel", "Relative", "Branch if minus (N=1)")
operations[0x31] = (5, "AND", "iny", "Indirect, Y Indexed", "AND to A")
operations[0x35] = (4, "AND", "zpx", "Zero Page, X Indexed", "AND to A")
operations[0x36] = (6, "ROL", "zpx", "Zero Page, X Indexed", "Rotate left")
operations[0x38] = (2, "SEC", "imp", "Implicit", "Set carry")
operations[0x39] = (4, "AND", "aby", "Absolute, Y Indexed", "AND to A")
operations[0x3D] = (4, "AND", "abx", "Absolute, X Indexed", "AND to A")
operations[0x3E] = (7, "ROL", "abx", "Absolute, X Indexed", "Rotate left")
operations[0x40] = (6, "RTI", "imp", "Implicit", "Return from interrupt")
operations[0x41] = (6, "EOR", "inx", "X Indexed, Indirect", "XOR to A")
operations[0x45] = (3, "EOR", "zpg", "Zero Page", "XOR to A")
operations[0x46] = (5, "LSR", "zpg", "Zero Page", "Logical shift right")
operations[0x48] = (3, "PHA", "imp", "Implicit", "Push A onto Stack")
operations[0x49] = (2, "EOR", "imm", "Immediate", "XOR to A")
operations[0x4A] = (3, "LSR", "acc", "Accumulator", "Logical shift right")
operations[0x4C] = (3, "JMP", "abs", "Absolute", "Jump to new location")
operations[0x4D] = (4, "EOR", "abs", "Absolute", "XOR To A")
operations[0x4E] = (6, "LSR", "abs", "Absolute", "Logical shift right")
operations[0x50] = (2, "BVC", "rel", "Relative", "Branch if ovfl clear (V=0)")
operations[0x51] = (5, "EOR", "iny", "Indirect, Y Indexed", "XOR to A")
operations[0x55] = (4, "EOR", "zpx", "Zero Page, X Indexed", "XOR to A")
operations[0x56] = (6, "LSR", "zpx", "Zero Page, X Indexed", "Logical shift right")
operations[0x58] = (2, "CLI", "imp", "Implicit", "Clear IRQ disable")
operations[0x59] = (4, "EOR", "aby", "Absolute, Y Indexed", "XOR to A")
operations[0x5D] = (4, "EOR", "abx", "Absolute, X Indexed", "XOR to A")
operations[0x5E] = (7, "LSR", "abx", "Absolute, X Indexed", "Logical shift right")
operations[0x60] = (6, "RTS", "imp", "Implicit", "Return from subroutine")
operations[0x61] = (6, "ADC", "inx", "X Indexed, Indirect", "Add with carry to A")
operations[0x65] = (3, "ADC", "zpg", "Zero Page", "Add with carry to A")
operations[0x66] = (5, "ROR", "zpg", "Zero Page", "Rotate right")
operations[0x68] = (4, "PLA", "imp", "Implicit", "Pop A from stack")
operations[0x69] = (2, "ADC", "imm", "Immediate", "Add with carry to A")
operations[0x6A] = (2, "ROR", "acc", "Accumulator", "Rotate right")
operations[0x6C] = (5, "JMP", "ind", "Indirect", "Jump to new location")
operations[0x6D] = (4, "ADC", "abs", "Absolute", "Add with carry to A")
operations[0x6E] = (6, "ROR", "abs", "Absolute", "Rotate right")
operations[0x70] = (2, "BVS", "rel", "Relative", "Branch if ovfl set (V=1)")
operations[0x71] = (5, "ADC", "iny", "Indirect, Y Indexed", "Add with carry to A")
operations[0x75] = (4, "ADC", "zpx", "Zero Page, X Indexed", "Add with carry to A")
operations[0x76] = (6, "ROR", "zpx", "Zero Page, X Indexed", "Rotate right")
operations[0x78] = (2, "SEI", "imp", "Implicit", "Set IRQ disable")
operations[0x79] = (4, "ADC", "aby", "Absolute, Y Indexed", "Add with carry to A")
operations[0x7D] = (4, "ADC", "abx", "Absolute, X Indexed", "Add with carry to A")
operations[0x7E] = (7, "ROR", "abx", "Absolute, X Indexed", "Rotate right")
operations[0x81] = (6, "STA", "inx", "X Indexed, Indirect", "Store A")
operations[0x84] = (3, "STY", "zpg", "Zero Page", "Store Y")
operations[0x85] = (3, "STA", "zpg", "Zero Page", "Store A")
operations[0x86] = (3, "STX", "zpg", "Zero Page", "Store X")
operations[0x88] = (2, "DEY", "imp", "Implicit", "Decrement Y")
operations[0x8A] = (2, "TXA", "imp", "Implicit", "Transfer X to A")
operations[0x8C] = (4, "STY", "abs", "Absolute", "Store Y")
operations[0x8D] = (4, "STA", "abs", "Absolute", "Store A")
operations[0x8E] = (4, "STX", "abs", "Absolute", "Store X")
operations[0x90] = (2, "BCC", "rel", "Relative", "Branch if carry clear (C=0)")
operations[0x91] = (6, "STA", "iny", "Indirect, Y Indexed", "Store A")
operations[0x94] = (4, "STY", "zpx", "Zero Page, X Indexed", "Store Y")
operations[0x95] = (4, "STA", "zpx", "Zero Page, X Indexed", "Store A")
operations[0x96] = (4, "STX", "zpy", "Zero Page, Y Indexed", "Store X")
operations[0x98] = (3, "TYA", "imp", "Implicit", "Transfer Y to A")
operations[0x99] = (5, "STA", "aby", "Absolute, Y Indexed", "Store A")
operations[0x9A] = (2, "TXS", "imp", "Implicit", "Transfer X to S")
operations[0x9D] = (5, "STA", "abx", "Absolute, X Indexed", "Store A")
operations[0xA0] = (2, "LDY", "imm", "Immediate", "Load Y")
operations[0xA1] = (6, "LDA", "inx", "X Indexed, Indirect", "Load A")
operations[0xA2] = (2, "LDX", "imm", "Immediate", "Load X")
operations[0xA4] = (3, "LDY", "zpg", "Zero Page", "Load Y")
operations[0xA5] = (3, "LDA", "zpg", "Zero Page", "Load A")
operations[0xA6] = (3, "LDX", "zpg", "Zero Page", "Load X")
operations[0xA8] = (2, "TAY", "imp", "Implicit", "Transer A to Y")
operations[0xA9] = (2, "LDA", "imm", "Immediate", "Load A")
operations[0xAA] = (2, "TAX", "imp", "Implicit", "Transfer A to X")
operations[0xAC] = (4, "LDY", "abs", "Absolute", "Load Y")
operations[0xAD] = (4, "LDA", "abs", "Absolute", "Load A")
operations[0xAE] = (4, "LDX", "abs", "Absolute", "Load X")
operations[0xB0] = (2, "BCS", "rel", "Relative", "Branch if carry set (C=1)")
operations[0xB1] = (5, "LDA", "iny", "Indirect, Y Indexed", "Load A")
operations[0xB4] = (4, "LDY", "zpx", "Zero Page, X Indexed", "Load Y")
operations[0xB5] = (4, "LDA", "zpx", "Zero Page, X Indexed", "Load A")
operations[0xB6] = (4, "LDX", "zpy", "Zero Page, Y Indexed", "Load X")
operations[0xB8] = (3, "CLV", "imp", "Implicit", "Clear overflow")
operations[0xB9] = (4, "LDA", "aby", "Absolute, Y Indexed", "Load A")
operations[0xBA] = (3, "TSX", "imp", "Implicit", "Transfer S to X")
operations[0xBC] = (4, "LDY", "abx", "Absolute, X Indexed", "Load Y")
operations[0xBD] = (4, "LDA", "abx", "Absolute, X Indexed", "Load A")
operations[0xBE] = (4, "LDX", "aby", "Absolute, Y Indexed", "Load X")
operations[0xC0] = (2, "CPY", "imm", "Immediate", "Compare with Y")
operations[0xC1] = (6, "CMP", "inx", "X Indexed, Indirect", "Compare with A")
operations[0xC4] = (3, "CPY", "zpg", "Zero Page", "Compare with Y")
operations[0xC5] = (3, "CMP", "zpg", "Zero Page", "Compare with A")
operations[0xC6] = (5, "DEC", "zpg", "Zero Page", "Decrement by one")
operations[0xC8] = (2, "INY", "imp", "Implicit", "Increment Y by one")
operations[0xC9] = (2, "CMP", "imm", "Immediate", "Compare with A")
operations[0xCA] = (2, "DEX", "imp", "Implicit", "Decrement X by one")
operations[0xCC] = (4, "CPY", "abs", "Absolute", "Compare with Y")
operations[0xCD] = (4, "CMP", "abs", "Absolute", "Compare with A")
operations[0xCE] = (6, "DEC", "abs", "Absolute", "Decrement by one")
operations[0xD0] = (2, "BNE", "rel", "Relative", "Branch if not equal (Z=0)")
operations[0xD1] = (5, "CMP", "iny", "Indirect, Y Indexed", "Compare with A")
operations[0xD5] = (4, "CMP", "zpx", "Zero Page, X Indexed", "Compare with A")
operations[0xD6] = (6, "DEC", "zpx", "Zero Page, X Indexed", "Decrement by one")
operations[0xD8] = (3, "CLD", "imp", "Implicit", "Clear decimal mode")
operations[0xD9] = (4, "CMP", "aby", "Absolute, Y Indexed", "Compare with A")
operations[0xDD] = (4, "CMP", "abx", "Absolute, X Indexed", "Compare with A")
operations[0xDE] = (7, "DEC", "abx", "Absolute, X Indexed", "Decrement by one")
operations[0xE0] = (2, "CPX", "imm", "Immediate", "Compare with X")
operations[0xE1] = (6, "SBC", "inx", "X Indexed, Indirect", "Subtract with borrow from A")
operations[0xE4] = (3, "CPX", "zpg", "Zero Page", "Compare with X")
operations[0xE5] = (3, "SBC", "zpg", "Zero Page", "Subtract with borrow from A")
operations[0xE6] = (5, "INC", "zpg", "Zero Page", "Increment by one")
operations[0xE8] = (2, "INX", "imp", "Implicit", "Increment X by one")
operations[0xE9] = (2, "SBC", "imm", "Immediate", "Subtract with borrow from A")
operations[0xEA] = (2, "NOP", "imp", "Implicit", "No operation")
operations[0xEC] = (4, "CPX", "abs", "Absolute", "Compare with X")
operations[0xED] = (4, "SBC", "abs", "Absolute", "Subtract with borrow from A")
operations[0xEE] = (6, "INC", "abs", "Absolute", "Increment by one")
operations[0xF0] = (2, "BEQ", "rel", "Relative", "Branch if equal (Z=1)")
operations[0xF1] = (5, "SBC", "iny", "Indirect, Y Indexed", "Subtract with borrow from A")
operations[0xF5] = (4, "SBC", "zpx", "Zero Page, X Indexed", "Subtract with borrow from A")
operations[0xF6] = (6, "INC", "zpx", "Zero Page, X Indexed", "Increment by one")
operations[0xF8] = (2, "SED", "imp", "Implicit", "Set decimal mode")
operations[0xF9] = (4, "SBC", "aby", "Absolute, Y Indexed", "Subtract with borrow from A")
operations[0xFD] = (4, "SBC", "abx", "Absolute, X Indexed", "Subtract with borrow from A")
operations[0xFE] = (7, "INC", "abx", "Absolute, X Indexed", "Increment by one")
```

First, an empty table with 256 entries is created, whose values are all set to invalid (???). Then the individual elements of the table are filled in the places for which the consecutive (bytecode) number represents a valid command.



```bash
PS C:\Users\jens\OneDrive\Desktop\CPyU\Disassembler\v3> python .\6502_disasssembler.py -h
usage: 6502_disasssembler.py [-h] -i I [-o O] [-a A]

options:
  -h, --help  show this help message and exit
  -i I        Die Eingabedatei zum Disassemblieren. apple2.rom ist default
  -o O        stdout, falls kein Dateiname angegeben wird
  -a A        Adresse als Hexadezimalzahl (D000 als Beispiel für Apple II)
PS C:\Users\jens\OneDrive\Desktop\CPyU\Disassembler\v3> python .\6502_disasssembler.py -i .\apple2.rom -a d000
D000    A9 20           LDA #$20                ;2      Immediate
D002    8D 26 03        STA $0326               ;4      Absolute
D005    AD 57 C0        LDA $C057               ;4      Absolute
D008    AD 53 C0        LDA $C053               ;4      Absolute
D00B    AD 50 C0        LDA $C050               ;4      Absolute
D00E    A9 00           LDA #$00                ;2      Immediate
D010    85 1C           STA $1C         ;3      Zero Page
D012    AD 26 03        LDA $0326               ;4      Absolute
D015    85 1B           STA $1B         ;3      Zero Page
D017    A0 00           LDY #$00                ;2      Immediate
D019    84 1A           STY $1A         ;3      Zero Page
D01B    A5 1C           LDA $1C         ;3      Zero Page
D01D    91 1A           STA $(1A),Y             ;6      Indirect, Y Indexed
D01F    20 A2 D0        JSR $D0A2               ;6      Absolute
D022    C8              INY                     ;2      Implicit
D023    D0 F6           BNE $F6         ;2      Relative
D025    E6 1B           INC $1B         ;5      Zero Page
D027    A5 1B           LDA $1B         ;3      Zero Page
D029    29 1F           AND #$1F                ;2      Immediate
D02B    D0 EE           BNE $EE         ;2      Relative
D02D    60              RTS                     ;6      Implicit
D02E    8D 22 03        STA $0322               ;4      Absolute
D031    8E 20 03        STX $0320               ;4      Absolute
D034    8C 21 03        STY $0321               ;4      Absolute
D037    48              PHA                     ;3      Implicit
D038    29 C0           AND #$C0                ;2      Immediate
D03A    85 26           STA $26         ;3      Zero Page
D03C    4A              LSR                     ;3      Accumulator
D03D    4A              LSR                     ;3      Accumulator
D03E    05 26           ORA $26         ;3      Zero Page
D040    85 26           STA $26         ;3      Zero Page
D042    68              PLA                     ;4      Implicit
D043    85 27           STA $27         ;3      Zero Page
D045    0A              ASL                     ;3      Accumulator
D046    0A              ASL                     ;3      Accumulator
```


