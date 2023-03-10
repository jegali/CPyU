# Lambda functions
For this version, I updated the disassembly unit to make use of lambda functions. For this purpose, I have added the clock cycles and functions for the address modes to the table. This has changed the table from 

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
```

into this structure:

```bash
def init_operations(self):
    # Taktzyklen, Befehlsname, Adressmodus, Adressmodus ausführlich, Beschreibung, Funktion, AnzahlBytes
    self.operations = [(1,"???", "imp", "Implicit", " ", self.illegal_opcode, 1)] * 0x100
    self.operations[0x00] = (7, "BRK", "imp", "Implicit", "Break (force interrupt)", self.implicit_mode, 1)
    self.operations[0x01] = (6, "ORA", "inx", "X Indexed, indirect", "OR to A", self.indirect_mode_x, 2)
    self.operations[0x05] = (3, "ORA", "zpg", "Zero Page", "OR to A", self.zero_page_mode, 2)
    self.operations[0x06] = (5, "ASL", "zpg", "Zero Page", "Arithmetic shift left", self.zero_page_mode, 2)
    self.operations[0x08] = (3, "PHP", "imp", "Implicit", "Push P onto stack", self.implicit_mode, 1)
    self.operations[0x09] = (2, "ORA", "imm", "Immediate", "OR to A", self.immediate_mode, 2)
    self.operations[0x0A] = (3, "ASL", "acc", "Accumulator", "Airthmetic shift left", self.accumulator_mode, 1)
    self.operations[0x0D] = (4, "ORA", "abs", "Absolute", "OR to A", self.absolute_mode, 3)
    self.operations[0x0E] = (6, "ASL", "abs", "Absolute", "Arithmetics shift left", self.absolute_mode, 3)
    self.operations[0x10] = (2, "BPL", "rel", "Relative", "Branch if plus (N=0)", self.relative_mode, 2)
    self.operations[0x11] = (5, "ORA", "iny", "Indirect, Y Indexed", "OR to A", self.indirect_mode_y, 2)
    self.operations[0x15] = (4, "ORA", "zpx", "Zero Page, X Indexed", "OR to A", self.zero_page_mode_x, 2)
    self.operations[0x16] = (6, "ASL", "zpx", "Zero Page, X Indexed", "Arithmetic shift left", self.zero_page_mode_x, 2)
    self.operations[0x18] = (2, "CLC", "imp", "Implicit", "Clear carry", self.implicit_mode, 1)
    self.operations[0x19] = (4, "ORA", "aby", "Absolute, Y Indexed", "OR to A", self.absolute_mode_y, 3)
    self.operations[0x1D] = (4, "ORA", "abx", "Absolute, X Indexed", "OR to A", self.absolute_mode_x, 3)
    self.operations[0x1E] = (7, "ASL", "abx", "Absolute, X Indexed", "Arithmetic shift left", self.absolute_mode_x, 3)
    self.operations[0x20] = (6, "JSR", "abs", "Absolute", "Jump to subroutine", self.absolute_mode, 3)
    self.operations[0x21] = (6, "AND", "inx", "X Indexed, Indirect", "AND to A", self.indirect_mode_x, 2)
    self.operations[0x24] = (3, "BIT", "zpg", "Zero Page", "AND with A (A unchanged)", self.zero_page_mode, 2)
    self.operations[0x25] = (3, "AND", "zpg", "Zero Page", "AND to A", self.zero_page_mode, 2)
    self.operations[0x26] = (5, "ROL", "zpg", "Zero Page", "Rotate left through carry", self.zero_page_mode, 2)
    self.operations[0x28] = (4, "PLP", "imp", "Implicit", "Pop P from Stack", self.implicit_mode, 1)
    self.operations[0x29] = (2, "AND", "imm", "Immediate", "And to A", self.immediate_mode, 2)
    self.operations[0x2A] = (3, "ROL", "acc", "Accumulator", "Rotate left", self.accumulator_mode, 1)
    self.operations[0x2C] = (4, "BIT", "abs", "Absolute", "AND with A (A unchanged)", self.absolute_mode, 3)
    self.operations[0x2D] = (4, "AND", "abs", "Absolute", "AND to A", self.absolute_mode, 3)
    self.operations[0x2E] = (6, "ROL", "abs", "Absolute", "Rotate left", self.absolute_mode, 3)
    self.operations[0x30] = (2, "BMI", "rel", "Relative", "Branch if minus (N=1)", self.relative_mode, 2)
    self.operations[0x31] = (5, "AND", "iny", "Indirect, Y Indexed", "AND to A", self.indirect_mode_y, 2)
    self.operations[0x35] = (4, "AND", "zpx", "Zero Page, X Indexed", "AND to A", self.zero_page_mode_x, 2)
    self.operations[0x36] = (6, "ROL", "zpx", "Zero Page, X Indexed", "Rotate left", self.zero_page_mode_x, 2)
    self.operations[0x38] = (2, "SEC", "imp", "Implicit", "Set carry", self.implicit_mode, 1)
    self.operations[0x39] = (4, "AND", "aby", "Absolute, Y Indexed", "AND to A", self.absolute_mode_y, 3)
    self.operations[0x3D] = (4, "AND", "abx", "Absolute, X Indexed", "AND to A", self.absolute_mode_x, 3)
    self.operations[0x3E] = (7, "ROL", "abx", "Absolute, X Indexed", "Rotate left", self.absolute_mode_x, 3)
    self.operations[0x40] = (6, "RTI", "imp", "Implicit", "Return from interrupt", self.implicit_mode, 1)
    self.operations[0x41] = (6, "EOR", "inx", "X Indexed, Indirect", "XOR to A", self.indirect_mode_x, 2)
    self.operations[0x45] = (3, "EOR", "zpg", "Zero Page", "XOR to A", self.zero_page_mode, 2)
    self.operations[0x46] = (5, "LSR", "zpg", "Zero Page", "Logical shift right", self.zero_page_mode, 2)
    self.operations[0x48] = (3, "PHA", "imp", "Implicit", "Push A onto Stack", self.implicit_mode, 1)
    self.operations[0x49] = (2, "EOR", "imm", "Immediate", "XOR to A", self.immediate_mode, 2)
    self.operations[0x4A] = (3, "LSR", "acc", "Accumulator", "Logical shift right", self.accumulator_mode, 1)
    self.operations[0x4C] = (3, "JMP", "abs", "Absolute", "Jump to new location", self.absolute_mode, 3)
    self.operations[0x4D] = (4, "EOR", "abs", "Absolute", "XOR To A", self.absolute_mode, 3)
    self.operations[0x4E] = (6, "LSR", "abs", "Absolute", "Logical shift right", self.absolute_mode,3)
    self.operations[0x50] = (2, "BVC", "rel", "Relative", "Branch if ovfl clear (V=0)", self.relative_mode,2)
    self.operations[0x51] = (5, "EOR", "iny", "Indirect, Y Indexed", "XOR to A", self.indirect_mode_y,2)
    self.operations[0x55] = (4, "EOR", "zpx", "Zero Page, X Indexed", "XOR to A", self.zero_page_mode_x,2)
    self.operations[0x56] = (6, "LSR", "zpx", "Zero Page, X Indexed", "Logical shift right", self.zero_page_mode_x,2)
    self.operations[0x58] = (2, "CLI", "imp", "Implicit", "Clear IRQ disable", self.implicit_mode,1)
    self.operations[0x59] = (4, "EOR", "aby", "Absolute, Y Indexed", "XOR to A", self.absolute_mode_y,3)
    self.operations[0x5D] = (4, "EOR", "abx", "Absolute, X Indexed", "XOR to A", self.absolute_mode_x,3)
    self.operations[0x5E] = (7, "LSR", "abx", "Absolute, X Indexed", "Logical shift right", self.absolute_mode_x,3)
    self.operations[0x60] = (6, "RTS", "imp", "Implicit", "Return from subroutine", self.implicit_mode,1)
    self.operations[0x61] = (6, "ADC", "inx", "X Indexed, Indirect", "Add with carry to A", self.indirect_mode_x,2)
    self.operations[0x65] = (3, "ADC", "zpg", "Zero Page", "Add with carry to A", self.zero_page_mode,2)
    self.operations[0x66] = (5, "ROR", "zpg", "Zero Page", "Rotate right", self.zero_page_mode,2)
    self.operations[0x68] = (4, "PLA", "imp", "Implicit", "Pop A from stack", self.implicit_mode,1)
    self.operations[0x69] = (2, "ADC", "imm", "Immediate", "Add with carry to A", self.immediate_mode,2)
    self.operations[0x6A] = (2, "ROR", "acc", "Accumulator", "Rotate right", self.accumulator_mode,1)
    self.operations[0x6C] = (5, "JMP", "ind", "Indirect", "Jump to new location",self.indirect_mode,3)
    self.operations[0x6D] = (4, "ADC", "abs", "Absolute", "Add with carry to A", self.absolute_mode,3)
    self.operations[0x6E] = (6, "ROR", "abs", "Absolute", "Rotate right", self.absolute_mode,3)
    self.operations[0x70] = (2, "BVS", "rel", "Relative", "Branch if ovfl set (V=1)", self.relative_mode,2)
    self.operations[0x71] = (5, "ADC", "iny", "Indirect, Y Indexed", "Add with carry to A", self.indirect_mode_y,2)
    self.operations[0x75] = (4, "ADC", "zpx", "Zero Page, X Indexed", "Add with carry to A", self.zero_page_mode_x,2)
    self.operations[0x76] = (6, "ROR", "zpx", "Zero Page, X Indexed", "Rotate right", self.zero_page_mode_x,2)
    self.operations[0x78] = (2, "SEI", "imp", "Implicit", "Set IRQ disable", self.implicit_mode,1)
    self.operations[0x79] = (4, "ADC", "aby", "Absolute, Y Indexed", "Add with carry to A", self.absolute_mode_y,3)
    self.operations[0x7D] = (4, "ADC", "abx", "Absolute, X Indexed", "Add with carry to A", self.absolute_mode_x,3)
    self.operations[0x7E] = (7, "ROR", "abx", "Absolute, X Indexed", "Rotate right", self.absolute_mode_x,3)
    self.operations[0x81] = (6, "STA", "inx", "X Indexed, Indirect", "Store A", self.indirect_mode_x,2)
    self.operations[0x84] = (3, "STY", "zpg", "Zero Page", "Store Y", self.zero_page_mode,2)
    self.operations[0x85] = (3, "STA", "zpg", "Zero Page", "Store A", self.zero_page_mode,2)
    self.operations[0x86] = (3, "STX", "zpg", "Zero Page", "Store X", self.zero_page_mode,2)
    self.operations[0x88] = (2, "DEY", "imp", "Implicit", "Decrement Y", self.implicit_mode,1)
    self.operations[0x8A] = (2, "TXA", "imp", "Implicit", "Transfer X to A", self.implicit_mode,1)
    self.operations[0x8C] = (4, "STY", "abs", "Absolute", "Store Y", self.absolute_mode,3)
    self.operations[0x8D] = (4, "STA", "abs", "Absolute", "Store A", self.absolute_mode,3)
    self.operations[0x8E] = (4, "STX", "abs", "Absolute", "Store X", self.absolute_mode,3)
    self.operations[0x90] = (2, "BCC", "rel", "Relative", "Branch if carry clear (C=0)", self.relative_mode,2)
    self.operations[0x91] = (6, "STA", "iny", "Indirect, Y Indexed", "Store A", self.indirect_mode_y,2)
    self.operations[0x94] = (4, "STY", "zpx", "Zero Page, X Indexed", "Store Y", self.zero_page_mode_x,2)
    self.operations[0x95] = (4, "STA", "zpx", "Zero Page, X Indexed", "Store A", self.zero_page_mode_x,2)
    self.operations[0x96] = (4, "STX", "zpy", "Zero Page, Y Indexed", "Store X", self.zero_page_mode_y,2)
    self.operations[0x98] = (3, "TYA", "imp", "Implicit", "Transfer Y to A", self.implicit_mode,1)
    self.operations[0x99] = (5, "STA", "aby", "Absolute, Y Indexed", "Store A", self.absolute_mode_y,3)
    self.operations[0x9A] = (2, "TXS", "imp", "Implicit", "Transfer X to S", self.implicit_mode,1)
    self.operations[0x9D] = (5, "STA", "abx", "Absolute, X Indexed", "Store A", self.absolute_mode_x,3)
    self.operations[0xA0] = (2, "LDY", "imm", "Immediate", "Load Y", self.immediate_mode,2)
    self.operations[0xA1] = (6, "LDA", "inx", "X Indexed, Indirect", "Load A", self.indirect_mode_x,2)
    self.operations[0xA2] = (2, "LDX", "imm", "Immediate", "Load X", self.immediate_mode,2)
    self.operations[0xA4] = (3, "LDY", "zpg", "Zero Page", "Load Y", self.zero_page_mode,2)
    self.operations[0xA5] = (3, "LDA", "zpg", "Zero Page", "Load A", self.zero_page_mode,2)
    self.operations[0xA6] = (3, "LDX", "zpg", "Zero Page", "Load X", self.zero_page_mode,2)
    self.operations[0xA8] = (2, "TAY", "imp", "Implicit", "Transer A to Y", self.implicit_mode,1)
    self.operations[0xA9] = (2, "LDA", "imm", "Immediate", "Load A", self.immediate_mode,2)
    self.operations[0xAA] = (2, "TAX", "imp", "Implicit", "Transfer A to X", self.implicit_mode,1)
    self.operations[0xAC] = (4, "LDY", "abs", "Absolute", "Load Y", self.absolute_mode,3)
    self.operations[0xAD] = (4, "LDA", "abs", "Absolute", "Load A", self.absolute_mode,3)
    self.operations[0xAE] = (4, "LDX", "abs", "Absolute", "Load X", self.absolute_mode,3)
    self.operations[0xB0] = (2, "BCS", "rel", "Relative", "Branch if carry set (C=1)", self.relative_mode,2)
    self.operations[0xB1] = (5, "LDA", "iny", "Indirect, Y Indexed", "Load A", self.indirect_mode_y,2)
    self.operations[0xB4] = (4, "LDY", "zpx", "Zero Page, X Indexed", "Load Y", self.zero_page_mode_x,2)
    self.operations[0xB5] = (4, "LDA", "zpx", "Zero Page, X Indexed", "Load A", self.zero_page_mode_x,2)
    self.operations[0xB6] = (4, "LDX", "zpy", "Zero Page, Y Indexed", "Load X", self.zero_page_mode_y,2)
    self.operations[0xB8] = (3, "CLV", "imp", "Implicit", "Clear overflow", self.implicit_mode,1)
    self.operations[0xB9] = (4, "LDA", "aby", "Absolute, Y Indexed", "Load A", self.absolute_mode_y,3)
    self.operations[0xBA] = (3, "TSX", "imp", "Implicit", "Transfer S to X", self.implicit_mode,1)
    self.operations[0xBC] = (4, "LDY", "abx", "Absolute, X Indexed", "Load Y", self.absolute_mode_x,3)
    self.operations[0xBD] = (4, "LDA", "abx", "Absolute, X Indexed", "Load A", self.absolute_mode_x,3)
    self.operations[0xBE] = (4, "LDX", "aby", "Absolute, Y Indexed", "Load X", self.absolute_mode_y,3)
    self.operations[0xC0] = (2, "CPY", "imm", "Immediate", "Compare with Y", self.immediate_mode,2)
    self.operations[0xC1] = (6, "CMP", "inx", "X Indexed, Indirect", "Compare with A", self.indirect_mode_x,2)
    self.operations[0xC4] = (3, "CPY", "zpg", "Zero Page", "Compare with Y", self.zero_page_mode,2)
    self.operations[0xC5] = (3, "CMP", "zpg", "Zero Page", "Compare with A", self.zero_page_mode,2)
    self.operations[0xC6] = (5, "DEC", "zpg", "Zero Page", "Decrement by one", self.zero_page_mode,2)
    self.operations[0xC8] = (2, "INY", "imp", "Implicit", "Increment Y by one", self.implicit_mode,1)
    self.operations[0xC9] = (2, "CMP", "imm", "Immediate", "Compare with A", self.immediate_mode,2)
    self.operations[0xCA] = (2, "DEX", "imp", "Implicit", "Decrement X by one", self.implicit_mode,1)
    self.operations[0xCC] = (4, "CPY", "abs", "Absolute", "Compare with Y", self.absolute_mode,3)
    self.operations[0xCD] = (4, "CMP", "abs", "Absolute", "Compare with A", self.absolute_mode,3)
    self.operations[0xCE] = (6, "DEC", "abs", "Absolute", "Decrement by one", self.absolute_mode,3)
    self.operations[0xD0] = (2, "BNE", "rel", "Relative", "Branch if not equal (Z=0)", self.relative_mode,2)
    self.operations[0xD1] = (5, "CMP", "iny", "Indirect, Y Indexed", "Compare with A", self.indirect_mode_y,2)
    self.operations[0xD5] = (4, "CMP", "zpx", "Zero Page, X Indexed", "Compare with A", self.zero_page_mode_x,2)
    self.operations[0xD6] = (6, "DEC", "zpx", "Zero Page, X Indexed", "Decrement by one", self.zero_page_mode_x,2)
    self.operations[0xD8] = (3, "CLD", "imp", "Implicit", "Clear decimal mode", self.implicit_mode,1)
    self.operations[0xD9] = (4, "CMP", "aby", "Absolute, Y Indexed", "Compare with A", self.absolute_mode_y,3)
    self.operations[0xDD] = (4, "CMP", "abx", "Absolute, X Indexed", "Compare with A", self.absolute_mode_x,3)
    self.operations[0xDE] = (7, "DEC", "abx", "Absolute, X Indexed", "Decrement by one", self.absolute_mode_x,3)
    self.operations[0xE0] = (2, "CPX", "imm", "Immediate", "Compare with X", self.immediate_mode,2)
    self.operations[0xE1] = (6, "SBC", "inx", "X Indexed, Indirect", "Subtract with borrow from A", self.indirect_mode_x,2)
    self.operations[0xE4] = (3, "CPX", "zpg", "Zero Page", "Compare with X", self.zero_page_mode,2)
    self.operations[0xE5] = (3, "SBC", "zpg", "Zero Page", "Subtract with borrow from A", self.zero_page_mode,2)
    self.operations[0xE6] = (5, "INC", "zpg", "Zero Page", "Increment by one", self.zero_page_mode,2)
    self.operations[0xE8] = (2, "INX", "imp", "Implicit", "Increment X by one", self.implicit_mode,1)
    self.operations[0xE9] = (2, "SBC", "imm", "Immediate", "Subtract with borrow from A", self.immediate_mode,2)
    self.operations[0xEA] = (2, "NOP", "imp", "Implicit", "No operation", self.implicit_mode,1)
    self.operations[0xEC] = (4, "CPX", "abs", "Absolute", "Compare with X", self.absolute_mode,3)
    self.operations[0xED] = (4, "SBC", "abs", "Absolute", "Subtract with borrow from A", self.absolute_mode,3)
    self.operations[0xEE] = (6, "INC", "abs", "Absolute", "Increment by one", self.absolute_mode,3)
    self.operations[0xF0] = (2, "BEQ", "rel", "Relative", "Branch if equal (Z=1)", self.relative_mode,2)
    self.operations[0xF1] = (5, "SBC", "iny", "Indirect, Y Indexed", "Subtract with borrow from A", self.indirect_mode_y,2)
    self.operations[0xF5] = (4, "SBC", "zpx", "Zero Page, X Indexed", "Subtract with borrow from A", self.zero_page_mode_x,2)
    self.operations[0xF6] = (6, "INC", "zpx", "Zero Page, X Indexed", "Increment by one", self.zero_page_mode_x,2)
    self.operations[0xF8] = (2, "SED", "imp", "Implicit", "Set decimal mode", self.implicit_mode,1)
    self.operations[0xF9] = (4, "SBC", "aby", "Absolute, Y Indexed", "Subtract with borrow from A", self.absolute_mode_y,3)
    self.operations[0xFD] = (4, "SBC", "abx", "Absolute, X Indexed", "Subtract with borrow from A", self.absolute_mode_x,3)
    self.operations[0xFE] = (7, "INC", "abx", "Absolute, X Indexed", "Increment by one", self.absolute_mode_x,3)
```

The global table was converted into a method. The initialization of the table is done within the method setupUI():

```bash
def setupUi(self, DisassemblerWindow):

    self.init_operations()
```

The disassemble() method could thus be streamlined and shortened. As before, a complete file or memory area is disassembled. This is one step closer to my goal, but the functionality to disassemble a single memory address for stepwise emulation is still missing. I will work on this in the next version. 

```bash
def disassemble(self):
    # nur, wenn etwas im Buffer steht, wird decodiert
    if self.code_array:
        # Startadresse aus dem Textfeld
        address = int(self.txtStartAddress.text(),0)
        self.plainTextEdit_3.clear()
        # Schleifenzähler
        byte_to_decode = 0
        last_byte = len(self.code_array)

        while byte_to_decode < last_byte:
            # Zeile zusammenbauen
            # Schreibe die Adresse
            line_to_write = hex(address)[2:].upper().zfill(4) + "- \t"

            opcode = int(self.code_array[byte_to_decode])
            operation = self.operations[opcode]
            info = operation[5](byte_to_decode)
            cycles = operation[6]

            hexcode = ' '.join([hex(i)[2:].upper().zfill(2) for i in self.code_array[byte_to_decode:(byte_to_decode + cycles)]]) 
            line_to_write = line_to_write + "{:<15}".format(hexcode)

            command = operation[1]
            line_to_write = line_to_write + command                
            line_to_write = line_to_write + " " + "{:<15}".format(info["operand"])                
            line_to_write = line_to_write + self.writeOptions(opcode)

            address += operation[6]
            byte_to_decode += operation[6]

            self.plainTextEdit_3.appendPlainText(line_to_write)

    txtCursor = self.plainTextEdit_3.textCursor()
    txtCursor.setPosition(0)
    self.plainTextEdit_3.setTextCursor(txtCursor)
```

Here are still the single methods for the address modes of the CPU. I have found that this approach will also be the viable way in the emulation.

```bash
#
# Zwei kleine Helferlein zum Auslesen von Speicherstellen
#

def read_byte(self, pc):
    return self.code_array[pc]

def read_word(self, pc):
    return ((self.code_array[pc+1]<<8) + (self.code_array[pc]))

def signed(self, x):
    if x > 0x7F:
        x = x - 0x100
    return x


#
# Methoden für die Adressmodi
# byte_to_decode is the actual position to be decoded
# so I will it name PC (=Program Counter)
#

def indirect_mode(self, pc):
    operand = "($%04X)" % (self.read_word(pc + 1))
    return {
        "operand": operand,        
    }

def indirect_mode_x(self, pc):
    operand = "($%02X,X)" % (self.read_byte(pc + 1))
    return {
        "operand": operand,        
    }

def indirect_mode_y(self, pc):
    operand = "($%02X),Y" % (self.read_byte(pc + 1))
    return {
        "operand": operand,        
    }

def zero_page_mode(self, pc):
    operand = "$%02X" % (self.read_byte(pc + 1))
    return {
        "operand": operand,        
    }

def zero_page_mode_x(self, pc):
    operand = "$%02X,X" % (self.read_byte(pc + 1))
    return {
        "operand": operand,        
    }

def zero_page_mode_y(self, pc):
    operand = "$%02X,Y" % (self.read_byte(pc + 1))
    return {
        "operand": operand,        
    }

def absolute_mode(self, pc):
    operand = "$%04X" % (self.read_word(pc + 1))
    return {
        "operand": operand,        
    }

def absolute_mode_x(self, pc):
    operand = "$%04X,X" % (self.read_word(pc + 1))
    return {
        "operand": operand,        
    }

def absolute_mode_y(self, pc):
    operand = "$%04X,Y" % (self.read_word(pc + 1))
    return {
        "operand": operand,        
    }

def immediate_mode(self, pc):
    operand = "#$%02X" % (self.read_byte(pc + 1))
    return {
        "operand": operand,
    }

def implicit_mode(self, pc):
    operand = "#$%02X" % (self.read_byte(pc + 1))
    return {
        "operand": operand,        
    }

def accumulator_mode(self, pc):
    operand = ""
    return {
        "operand": operand,        
    }

def relative_mode(self, pc):
    operand = "$%04X" % (pc + self.signed(self.read_byte(pc + 1) + 2))
    return {
        "operand": operand,        
    }

def illegal_opcode(self, pc):
    operand = ""
    return {
        "operand": operand,       
    }

```
