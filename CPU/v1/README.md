# CPU
In contrast to the Disassember and Assembler modules, I paid more attention to modularization and object orientation when creating the CPU and its components.
So the CPU is not a monolith, but I have sorted the CPU into the context in which it should work later. 

## The class diagram
The object oriented view onto the app is best shown with a class diagram. We have a class Apple, which will realize the surrounding computer. Parts of the class Apple are the CPU, the RAM and the ROM. RAM and ROM as memory components inherit again from the class Memory. Class Apple itself is embedded inside the EmulatorWindow, which has aggregtation relationships to DisassemblerWindow and AssemblerWindow. The following class diagram clarifies these relations:<br/><br/>

![CPyU-Class-diagram](/images/class-diagram-cpyu-v1.png)

Let' discuss the classes in more depth now.

## Disassembler Window
This class already has been discussed. Find the details here: [Disassembler](https://github.com/jegali/CPyU/tree/main/Disassembler)

## Assembler Window
This class already has been discussed. Find the details here: [Assembler](https://github.com/jegali/CPyU/tree/main/Assembler)

## ROM
The ROM class is the base class of the memory. In the end it is only a collection of memory locations from which only reading is possible.
The current state of development is that the ROM consists of an array that is set to zero on initialization. Furthermore, the complete ROM can be dumped via the dump_mem() method. Individual memory locations of the ROM can be read out via the method read_byte(). 

For the further development it is still thought that for example the binary ROM file of the Apple can be loaded directly to a certain address. At the moment, however, these functions are still commented out.

```bash
#
# ROM - Read Only Memory
#
# This kind of memory can only be read,
# not written
#

class ROM:

    def __init__(self, start, size):
        self.start = start
        self.end = start + size - 1
        self._mem = [0x00] * size
        self.size = size

    # def load(self, address, data):
    #     for offset, datum in enumerate(data):
    #         self._mem[address - self.start + offset] = datum

    # def load_file(self, address, filename):
    #     with open(filename, "rb") as f:
    #         for offset, datum in enumerate(f.read()):
    #             self._mem[address - self.start + offset] = ord(datum)

    def read_byte(self, address):
        assert self.start <= address <= self.end
        return self._mem[address - self.start]

    def dump_mem(self):
        return self._mem[0:]
```

## RAM
The RAM class inherits from the ROM class, which makes total sense. After all, the RAM has the same functions as the ROM, but in addition can also be written to the memory locations. For now, that's all the enhancements the RAM can do. Surely more functions will be added later.

```bash
from rom import ROM


#
# RAM - Random Access Memory
#
# This is a more general memory that can be read
# and written, so it makes sense to inherit from ROM
#

class RAM(ROM):

    def write_byte(self, address, value):
        self._mem[address] = value
```

## Memory
The entirety of the computer memory consists of one part RAM and one part ROM. The management of the two parts is done by the class Memory in our example. There is - especially in the Apple ][ - also the concept of a zero page and the stack, but these are only special address areas of the RAM and are therefore not explicitly specified as own classes. For a correct emulation of the Apple ][ methods are still provided to write to and read from the computer's bus system. However, at the moment these methods are not needed and are therefore commented out.

```bash
from ram import RAM
from rom import ROM


#
# Memory 
#
# This class consists of RAM and ROM

class Memory:

    def __init__(self, options=None, use_bus=True):
        self.use_bus = use_bus
        self.rom = ROM(0xD000, 0x3000)

        if options:
            self.rom.load_file(0xD000, options.rom)

        self.ram = RAM(0x0000, 0xC000)

        if options and options.ram:
            self.ram.load_file(0x0000, options.ram)

        self.rom.dump_mem()
        self.ram.dump_mem()

    # def load(self, address, data):
    #     if address < 0xC000:
    #         self.ram.load(address, data)

    def read_byte(self, cycle, address):
        if address < 0xC000:
            return self.ram.read_byte(address)
        # elif address < 0xD000:
        #     return self.bus_read(cycle, address)
        else:
            return self.rom.read_byte(address)

    # def read_word(self, cycle, address):
    #     return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address + 1) << 8)

    # def read_word_bug(self, cycle, address):
    #     if address % 0x100 == 0xFF:
    #         return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address & 0xFF00) << 8)
    #     else:
    #         return self.read_word(cycle, address)

    def write_byte(self, cycle, address, value):
        if address < 0xC000:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 or 0x2000 <= address < 0x5FFF:
            self.bus_write(cycle, address, value)

    # def bus_read(self, cycle, address):
    #     if not self.use_bus:
    #         return 0
    #     op = struct.pack("<IBHB", cycle, 0, address, 0)
    #     try:
    #         bus.send(op)
    #         b = bus.recv(1)
    #         if len(b) == 0:
    #             sys.exit(0)
    #         return ord(b)
    #     except socket.error:
    #         sys.exit(0)

    # def bus_write(self, cycle, address, value):
    #     if not self.use_bus:
    #         return
    #     op = struct.pack("<IBHB", cycle, 1, address, value)
    #     try:
    #         bus.send(op)
    #     except IOError:
    #         sys.exit(0)
```

## CPU
The CPU is the actual core of the emulation program. Here all commands are decoded, executed and the results are stored in the respective registers and memory locations. The emulation is far from being executable and perfect at this point and is being extended a bit more every day. I will briefly explain the current status of the CPU class here.

First of all, the essential memory locations are initialized. In the case of the Apple ][ these are the zero page, the address of the stack and an address called reset vector. If a 6502 CPU is put into operation, the CPU reads the value of the memory location 0xFFFC and uses the read value as start address for the program.

```bash
from memory import Memory

class CPU(object):

    ZERO_PAGE = 0x0000
    STACK_PAGE = 0x0100
    RESET_VECTOR = 0xFFFC
```

The init() method then initializes and sets the other components of the CPU, such as the individual registers. Which registers are to be implemented depends on the concrete CPU. At this point we leave the general emulation level and dedicate ourselves concretely to the states of the 6502.

```bash
    def __init__(self, memory, emulator):

        self.program_counter = 0x0000
        
        self.accumulator = 0x00
        self.x_index = 0x00
        self.y_index = 0x00

        self.carry_flag = 0
        self.zero_flag = 0
        self.interrupt_disable_flag = 0
        self.decimal_mode_flag = 0
        self.break_flag = 1
        self.overflow_flag = 0
        self.sign_flag = 0

        self.stack_pointer = 0xFF

        self.cycles = 0

        self.memory = memory

        self.emulator = emulator

        self.setup_ops()
```

Besides the registers, the functions behind the opcodes/mnemonics are of course the core of the CPU and its emulation. The single functions are initialized in the method setup_ops(). For this I used the concept of lambda functions - this way the valid opcodes can be stored in a list or array and the method necessary for the processing can be stored comfortably.

```bash
    
    def setup_ops(self):
        self.ops = [None] * 0x100
        self.ops[0x00] = lambda: self.BRK()
        self.ops[0x01] = lambda: self.ORA(self.indirect_x_mode())
        self.ops[0x05] = lambda: self.ORA(self.zero_page_mode())
        self.ops[0x06] = lambda: self.ASL(self.zero_page_mode())
        self.ops[0x08] = lambda: self.PHP()
        self.ops[0x09] = lambda: self.ORA(self.immediate_mode())
        self.ops[0x0A] = lambda: self.ASL()
        self.ops[0x0D] = lambda: self.ORA(self.absolute_mode())
        self.ops[0x0E] = lambda: self.ASL(self.absolute_mode())
        self.ops[0x10] = lambda: self.BPL(self.relative_mode())
        self.ops[0x11] = lambda: self.ORA(self.indirect_y_mode())
        self.ops[0x15] = lambda: self.ORA(self.zero_page_x_mode())
        self.ops[0x16] = lambda: self.ASL(self.zero_page_x_mode())
        self.ops[0x18] = lambda: self.CLC()
        self.ops[0x19] = lambda: self.ORA(self.absolute_y_mode())
        self.ops[0x1D] = lambda: self.ORA(self.absolute_x_mode())
        self.ops[0x1E] = lambda: self.ASL(self.absolute_x_mode(rmw=True))
        self.ops[0x20] = lambda: self.JSR(self.absolute_mode())
        self.ops[0x21] = lambda: self.AND(self.indirect_x_mode())
        self.ops[0x24] = lambda: self.BIT(self.zero_page_mode())
        self.ops[0x25] = lambda: self.AND(self.zero_page_mode())
        self.ops[0x26] = lambda: self.ROL(self.zero_page_mode())
        self.ops[0x28] = lambda: self.PLP()
        self.ops[0x29] = lambda: self.AND(self.immediate_mode())
        self.ops[0x2A] = lambda: self.ROL()
        self.ops[0x2C] = lambda: self.BIT(self.absolute_mode())
        self.ops[0x2D] = lambda: self.AND(self.absolute_mode())
        self.ops[0x2E] = lambda: self.ROL(self.absolute_mode())
        self.ops[0x30] = lambda: self.BMI(self.relative_mode())
        self.ops[0x31] = lambda: self.AND(self.indirect_y_mode())
        self.ops[0x35] = lambda: self.AND(self.zero_page_x_mode())
        self.ops[0x36] = lambda: self.ROL(self.zero_page_x_mode())
        self.ops[0x38] = lambda: self.SEC()
        self.ops[0x39] = lambda: self.AND(self.absolute_y_mode())
        self.ops[0x3D] = lambda: self.AND(self.absolute_x_mode())
        self.ops[0x3E] = lambda: self.ROL(self.absolute_x_mode(rmw=True))
        self.ops[0x40] = lambda: self.RTI()
        self.ops[0x41] = lambda: self.EOR(self.indirect_x_mode())
        self.ops[0x45] = lambda: self.EOR(self.zero_page_mode())
        self.ops[0x46] = lambda: self.LSR(self.zero_page_mode())
        self.ops[0x48] = lambda: self.PHA()
        self.ops[0x49] = lambda: self.EOR(self.immediate_mode())
        self.ops[0x4A] = lambda: self.LSR()
        self.ops[0x4C] = lambda: self.JMP(self.absolute_mode())
        self.ops[0x4D] = lambda: self.EOR(self.absolute_mode())
        self.ops[0x4E] = lambda: self.LSR(self.absolute_mode())
        self.ops[0x50] = lambda: self.BVC(self.relative_mode())
        self.ops[0x51] = lambda: self.EOR(self.indirect_y_mode())
        self.ops[0x55] = lambda: self.EOR(self.zero_page_x_mode())
        self.ops[0x56] = lambda: self.LSR(self.zero_page_x_mode())
        self.ops[0x58] = lambda: self.CLI()
        self.ops[0x59] = lambda: self.EOR(self.absolute_y_mode())
        self.ops[0x5D] = lambda: self.EOR(self.absolute_x_mode())
        self.ops[0x5E] = lambda: self.LSR(self.absolute_x_mode(rmw=True))
        self.ops[0x60] = lambda: self.RTS()
        self.ops[0x61] = lambda: self.ADC(self.indirect_x_mode())
        self.ops[0x65] = lambda: self.ADC(self.zero_page_mode())
        self.ops[0x66] = lambda: self.ROR(self.zero_page_mode())
        self.ops[0x68] = lambda: self.PLA()
        self.ops[0x69] = lambda: self.ADC(self.immediate_mode())
        self.ops[0x6A] = lambda: self.ROR()
        self.ops[0x6C] = lambda: self.JMP(self.indirect_mode())
        self.ops[0x6D] = lambda: self.ADC(self.absolute_mode())
        self.ops[0x6E] = lambda: self.ROR(self.absolute_mode())
        self.ops[0x70] = lambda: self.BVS(self.relative_mode())
        self.ops[0x71] = lambda: self.ADC(self.indirect_y_mode())
        self.ops[0x75] = lambda: self.ADC(self.zero_page_x_mode())
        self.ops[0x76] = lambda: self.ROR(self.zero_page_x_mode())
        self.ops[0x78] = lambda: self.SEI()
        self.ops[0x79] = lambda: self.ADC(self.absolute_y_mode())
        self.ops[0x7D] = lambda: self.ADC(self.absolute_x_mode())
        self.ops[0x7E] = lambda: self.ROR(self.absolute_x_mode(rmw=True))
        self.ops[0x81] = lambda: self.STA(self.indirect_x_mode())
        self.ops[0x84] = lambda: self.STY(self.zero_page_mode())
        self.ops[0x85] = lambda: self.STA(self.zero_page_mode())
        self.ops[0x86] = lambda: self.STX(self.zero_page_mode())
        self.ops[0x88] = lambda: self.DEY()
        self.ops[0x8A] = lambda: self.TXA()
        self.ops[0x8C] = lambda: self.STY(self.absolute_mode())
        self.ops[0x8D] = lambda: self.STA(self.absolute_mode())
        self.ops[0x8E] = lambda: self.STX(self.absolute_mode())
        self.ops[0x90] = lambda: self.BCC(self.relative_mode())
        self.ops[0x91] = lambda: self.STA(self.indirect_y_mode(rmw=True))
        self.ops[0x94] = lambda: self.STY(self.zero_page_x_mode())
        self.ops[0x95] = lambda: self.STA(self.zero_page_x_mode())
        self.ops[0x96] = lambda: self.STX(self.zero_page_y_mode())
        self.ops[0x98] = lambda: self.TYA()
        self.ops[0x99] = lambda: self.STA(self.absolute_y_mode(rmw=True))
        self.ops[0x9A] = lambda: self.TXS()
        self.ops[0x9D] = lambda: self.STA(self.absolute_x_mode(rmw=True))
        self.ops[0xA0] = lambda: self.LDY(self.immediate_mode())
        self.ops[0xA1] = lambda: self.LDA(self.indirect_x_mode())
        self.ops[0xA2] = lambda: self.LDX(self.immediate_mode())
        self.ops[0xA4] = lambda: self.LDY(self.zero_page_mode())
        self.ops[0xA5] = lambda: self.LDA(self.zero_page_mode())
        self.ops[0xA6] = lambda: self.LDX(self.zero_page_mode())
        self.ops[0xA8] = lambda: self.TAY()
        self.ops[0xA9] = lambda: self.LDA(self.immediate_mode())
        self.ops[0xAA] = lambda: self.TAX()
        self.ops[0xAC] = lambda: self.LDY(self.absolute_mode())
        self.ops[0xAD] = lambda: self.LDA(self.absolute_mode())
        self.ops[0xAE] = lambda: self.LDX(self.absolute_mode())
        self.ops[0xB0] = lambda: self.BCS(self.relative_mode())
        self.ops[0xB1] = lambda: self.LDA(self.indirect_y_mode())
        self.ops[0xB4] = lambda: self.LDY(self.zero_page_x_mode())
        self.ops[0xB5] = lambda: self.LDA(self.zero_page_x_mode())
        self.ops[0xB6] = lambda: self.LDX(self.zero_page_y_mode())
        self.ops[0xB8] = lambda: self.CLV()
        self.ops[0xB9] = lambda: self.LDA(self.absolute_y_mode())
        self.ops[0xBA] = lambda: self.TSX()
        self.ops[0xBC] = lambda: self.LDY(self.absolute_x_mode())
        self.ops[0xBD] = lambda: self.LDA(self.absolute_x_mode())
        self.ops[0xBE] = lambda: self.LDX(self.absolute_y_mode())
        self.ops[0xC0] = lambda: self.CPY(self.immediate_mode())
        self.ops[0xC1] = lambda: self.CMP(self.indirect_x_mode())
        self.ops[0xC4] = lambda: self.CPY(self.zero_page_mode())
        self.ops[0xC5] = lambda: self.CMP(self.zero_page_mode())
        self.ops[0xC6] = lambda: self.DEC(self.zero_page_mode())
        self.ops[0xC8] = lambda: self.INY()
        self.ops[0xC9] = lambda: self.CMP(self.immediate_mode())
        self.ops[0xCA] = lambda: self.DEX()
        self.ops[0xCC] = lambda: self.CPY(self.absolute_mode())
        self.ops[0xCD] = lambda: self.CMP(self.absolute_mode())
        self.ops[0xCE] = lambda: self.DEC(self.absolute_mode())
        self.ops[0xD0] = lambda: self.BNE(self.relative_mode())
        self.ops[0xD1] = lambda: self.CMP(self.indirect_y_mode())
        self.ops[0xD5] = lambda: self.CMP(self.zero_page_x_mode())
        self.ops[0xD6] = lambda: self.DEC(self.zero_page_x_mode())
        self.ops[0xD8] = lambda: self.CLD()
        self.ops[0xD9] = lambda: self.CMP(self.absolute_y_mode())
        self.ops[0xDD] = lambda: self.CMP(self.absolute_x_mode())
        self.ops[0xDE] = lambda: self.DEC(self.absolute_x_mode(rmw=True))
        self.ops[0xE0] = lambda: self.CPX(self.immediate_mode())
        self.ops[0xE1] = lambda: self.SBC(self.indirect_x_mode())
        self.ops[0xE4] = lambda: self.CPX(self.zero_page_mode())
        self.ops[0xE5] = lambda: self.SBC(self.zero_page_mode())
        self.ops[0xE6] = lambda: self.INC(self.zero_page_mode())
        self.ops[0xE8] = lambda: self.INX()
        self.ops[0xE9] = lambda: self.SBC(self.immediate_mode())
        self.ops[0xEA] = lambda: self.NOP()
        self.ops[0xEC] = lambda: self.CPX(self.absolute_mode())
        self.ops[0xED] = lambda: self.SBC(self.absolute_mode())
        self.ops[0xEE] = lambda: self.INC(self.absolute_mode())
        self.ops[0xF0] = lambda: self.BEQ(self.relative_mode())
        self.ops[0xF1] = lambda: self.SBC(self.indirect_y_mode())
        self.ops[0xF5] = lambda: self.SBC(self.zero_page_x_mode())
        self.ops[0xF6] = lambda: self.INC(self.zero_page_x_mode())
        self.ops[0xF8] = lambda: self.SED()
        self.ops[0xF9] = lambda: self.SBC(self.absolute_y_mode())
        self.ops[0xFD] = lambda: self.SBC(self.absolute_x_mode())
        self.ops[0xFE] = lambda: self.INC(self.absolute_x_mode(rmw=True))

    #####

```

Even though the table is long and looks like a lot of work, the real work is still to come: the individual functions behind the initialization of the lambda functions still have to be implemented, of course. Here, too, I am still at the beginning and have implemented only one function so far.  The functions will be created bit by bit and then checked for their correct function via small assembler programs.

```bash

    # LOAD / STORE

    def LDA(self, operand_address):
        print("LDA")
        self.accumulator = self.update_nz(self.read_byte(operand_address))
        print("Akku: " + str(self.accumulator))
    #####

```

Besides the CPU functions, the address modes of the CPU must also be considered. This happens in the next block. At the moment only the method for the intermediate mode of the CPU exists, the other methods will follow.

```bash
    def immediate_mode(self):
        return self.get_PC()

    #####

```

Furthermore, methods are still needed to adjust the processor registers and bits:

```bash
    def update_nz(self, value):
        value = value % 0x100
        self.zero_flag = [0, 1][(value == 0)]
        self.sign_flag = [0, 1][((value & 0x80) != 0)]
        return value

    def update_nzc(self, value):
        self.carry_flag = [0, 1][(value > 0xFF)]
        return self.update_nz(value)

    #####

```

What I am not yet satisfied with is the method that reads, decodes and executes the respective assembly instruction according to the von Neumann principle. At the moment it can only process a single presence. Here I still have to think about something.

```bash

    def operation_cycle(self):
        # fetch
        opcode = self.read_pc_byte()
        #print("Opcode: " + str(opcode))
        # Anhand des Opcodes aus der Tabelle mit den Lambda-Funktionen die
        # entsprechende Funktion aussuchen
        # decode
        func_to_call = self.ops[opcode]
        if func_to_call is None:
            print ("UNKNOWN OPCODE")
            print (hex(self.program_counter - 1))
            print (hex(opcode))
            self.BRK()
        else:
            # execute
            #self.ops[opcode]()
            pass


    #
    # def get_PC(self, increment=1):
    #
    # Get the actual program counter value
    # increment the program counter by default one, 
    # if no value is submitted
    #

    def get_PC(self, increment=1):
        pc = self.program_counter
        self.program_counter += increment
        return pc

    def get_AC(self):
        return self.accumulator

    def get_XR(self):
        return self.x_index

    def get_YR(self):
        return self.y_index
    
    def get_SP(self):
        return self.stack_pointer

    def get_Flags(self):
        return str(self.sign_flag) + str(self.overflow_flag) + "1" + str(self.break_flag) + str(self.decimal_mode_flag) + str(self.interrupt_disable_flag) + str(self.zero_flag) + str(self.carry_flag)

    #
    # def read_PC(self):
    #
    # Just get the actual PC
    #

    def read_PC(self):
        return self.program_counter

    #
    # def read_pc_byte(self):
    #
    # Get the byte from the current PC position
    # and increment PC
    #
    
    def read_pc_byte(self):
        return self.read_byte(self.get_PC())


    # def read_byte(self, address):
    #     return self.memory.read_byte(self.cycles, address)

    def read_byte(self, address):
        return self.memory.read_byte(self.cycles, address)
```

## Class Apple
The Apple class holds together the CPU, memory, and other peripheral components yet to be implemented. At the moment, no use is made of peculiarities of the 6502 - this class writes only one instruction to memory and executes it. The auxiliary methods dump_xxx() read certain memory areas and can pass the information to the graphical user interface (the EmulationWindow).

```bash
from CPU import CPU
from memory import Memory

class Apple2:

    def __init__(self, emulator) -> None:
        self.emulator = emulator
        self.memory = Memory()
        for i in range(256):
            self.memory.write_byte(0,i,i)

        self.memory.write_byte(0, 0, 0xb9)
        self.memory.write_byte(0, 1, 0x03)
        self.cpu = CPU(self.memory, emulator)
        
        emulator.updateRegisterFlags(self.cpu)
        emulator.updateMemoryView(self.memory)


    def run(self):
        self.cpu.operation_cycle()


    def dump_ram(self):
        memdump = self.memory.ram.dump_mem()
        return memdump

    def dump_rom(self):
        memdump = self.memory.rom.dump_mem()
        return memdump

    def dump_zeropage(self):
        memdump = self.memory.ram.dump_mem()
        return memdump[0:256]

    def dump_stack(self):
        memdump = self.memory.ram.dump_mem()
        return memdump[256:512]
      
```

## Emulator Window
The emulator window was built according to the same principles as the disassembler and assembler window. This means that also this time there will be a class main.py which will be used to start the emulator window. What is new, however, is that the disassembler and also the assembler window can be called via a menu item in the emulator window. We will look at the source code for this functionality later. I also wrote a custom component that represents the hex editor and its functionality. This component is used instead of the PlainTextEdit component.


### The Hexedit component
Important elements in the component are:  

- Control only via the arrow keys
- Spaces between hex values must be skipped when navigating
- Input values may only be 0-9A-F 
- Editing is only allowed in the hex area

Basically, these properties are controlled by the event keyPressEvent and mouseEvent. Maybe there are extensions to be made to the components in the future, at the moment the state is unchanged and up to date.

```bash
#
# class myTextEdit(QtWidgets.QPlainTextEdit):
#
# Ich habe hier von der Klasse QPlainTextEdit
# eine Subklasse angelegt, um Tastendrücke abfangen zu können
# Editierbewegungen im hexeditor
# 

class myTextEdit(QtWidgets.QPlainTextEdit):  
    def __init__(self, parent=None):
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.setOverwriteMode(True)

    # Der Benutzer nutzt innerhalb des Editierfeldes
    # die Tasten A-F, 0-9 oder die Pfeiltasten

    def keyPressEvent(self, event):
        myCursor = QtGui.QTextCursor(self.document())

        # Hier wird der editierbare Bereich eingegrenzt. Das sind die Spalten 7-55 und
        # die Anzahl der Zeilen in dem Textedit
        if self.textCursor().columnNumber() >= 7 and self.textCursor().columnNumber() <= 55 and \
            self.textCursor().blockNumber() < self.document().lineCount():

            # Das Ende der Zeile ist erreicht, wir benötigen einen Zeilenvorschub (falls möglich)
            if self.textCursor().columnNumber() == 55 and \
                self.textCursor().blockNumber() < self.document().lineCount()-1:
                myCursor.setPosition(7 + (self.textCursor().blockNumber()+1)*75)
                self.setTextCursor(myCursor)
            # falls wir bereits in der letzten Zeile sind, brich die Eingabebehandlung ab
            elif self.textCursor().columnNumber() == 55 and \
                self.textCursor().blockNumber() == self.document().lineCount()-1:
                return

            # Es sind als Eingabe nur die hexadezimalen Zeichen a-fA-F0.9 erlaubt
            # a-f werden durch die Behandlung auf uppercase gesetzt 
            if event.key() in (QtCore.Qt.Key.Key_A.value, QtCore.Qt.Key.Key_B.value,
                            QtCore.Qt.Key.Key_C.value, QtCore.Qt.Key.Key_D.value,
                            QtCore.Qt.Key.Key_E.value, QtCore.Qt.Key.Key_F.value) or \
                event.key() >= QtCore.Qt.Key.Key_0 and event.key() <= QtCore.Qt.Key.Key_9:
                text = event.text()
                text = text.upper()
                # Der Cursor muss um zwei Positionen versetzt werden, wenn er auf einem Leerzeichen zwischen den Bytes steht
                # (eine Position automatisch nach Texteingabe, eine weitere für das Leerzeichen)
                newEvent = QKeyEvent(event.type(), QtCore.Qt.Key.Key_unknown, event.modifiers(), text)
                if self.textCursor().columnNumber() in (9, 12, 15, 18, 21, 24, 27, 31, 34, 37, 40, 43, 46, 49, 52):
                    myCursor.setPosition(self.textCursor().position() + 1)
                    self.setTextCursor(myCursor)
                # steht der Cursor zwischen den beiden 8-Byte-Blöcken, muss er um drei Positionen versetzt werden
                # (eine Position automatisch nach Texteingabe, zwei weitere für die Leerzeichen)
                elif self.textCursor().columnNumber() == 30:
                    myCursor.setPosition(self.textCursor().position() + 2)
                    self.setTextCursor(myCursor)

                super().keyPressEvent(newEvent)

            # Der Benutzer scrollt nach links
            if event.key() == QtCore.Qt.Key.Key_Left.value:
                # solange der Benutzer noch nicht am linken Rand angekommen ist...
                if (self.textCursor().columnNumber() > 7):  
                    myCursor.setPosition(self.textCursor().position() - 1) 
                    self.setTextCursor(myCursor)
                # ... falls er am linken Rand angekommen ist, wird überprüft,
                # ob er in der obersten Zeile ist. Falls nein, den Cursor nach rechts setzen
                # und eine Zeile hoch gehen
                elif self.textCursor().columnNumber() == 7 and \
                self.textCursor().blockNumber() > 0 :
                    myCursor.setPosition(54 + (self.textCursor().blockNumber()-1)*75)
                    self.setTextCursor(myCursor)

            # Der Benutzer scrollt nach rechts
            if event.key() == QtCore.Qt.Key.Key_Right.value:
                # solange der Benutzer noch nicht am rechten Rand angekommen ist...
                if (self.textCursor().columnNumber() < 54):  
                    myCursor.setPosition(self.textCursor().position() + 1) 
                    self.setTextCursor(myCursor)
                # ... falls er am rechten Rand angekommen ist, wird überprüft,
                # ob er in der untersten Zeile ist. Falls nein, den Cursor nach rechts setzen
                # und eine Zeile runter gehen
                elif self.textCursor().columnNumber() == 54 and \
                self.textCursor().blockNumber() < self.document().lineCount()-1:
                    myCursor.setPosition(7 + (self.textCursor().blockNumber()+1)*75)
                    self.setTextCursor(myCursor)

            # Die PFeiltasten hoch und runter bleiben, wie sie sind
            if event.key() == QtCore.Qt.Key.Key_Up.value:
                super().keyPressEvent(event)
            if event.key() == QtCore.Qt.Key.Key_Down.value:
                super().keyPressEvent(event)
                


    #
    # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    #
    # Der Benutzer klickt mit der Maus in das Editierfeld
    #

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        cursor = self.cursorForPosition(event.pos())

        # Klickt der Benutzer in den Adressbereich oder den Ascii-Bereich, 
        # wird er auf die Editierfläche beschränkt
        columnNumber = cursor.positionInBlock()
        if columnNumber < 7:
            columnNumber = 7
        if columnNumber > 54:
            columnNumber = 54

        # Fall er auf die Leerstellen zwischen den Bytes klickt (linke Spalte)
        # wird der Cursor auf das nächstgelegene Byte gesetzt
        if columnNumber >= 7 and columnNumber <= 30:
            columnNumber -= 7
            columnNumber = (columnNumber // 3) * 3
            columnNumber += 7

        # Fall er auf die Leerstellen zwischen den Bytes klickt (rechte Spalte)
        # wird der Cursor auf das nächstgelegene Byte gesetzt
        if columnNumber >= 32 and columnNumber <= 54:
            columnNumber -= 32
            columnNumber = (columnNumber // 3) * 3
            columnNumber += 32

        # und nun den Cursor "wirklich setzen"
        block = cursor.block()

        cursor.setPosition(block.position() + columnNumber)
        self.setTextCursor(cursor)

´´´

### Parts of the emulator window

```bash
# Form implementation generated from reading ui file '.\emulator.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

# xxx RAM View
# xxx Zero page View
# xxx Stack View
# xxx ROM View


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QKeyEvent
from apple2 import Apple2
from disassemblerWindow import Ui_DisassemblerWindow
from assemblerWindow import Ui_AssemblerWindow

class Ui_EmulatorWindow(object):

    program_counter = 0
    code = "A9 03"
    running = False
    Emulator = None
    window_asm = None
    window_dis = None

    def setupUi(self, Emulator):
        Emulator.setObjectName("Emulator")
        Emulator.resize(1440, 900)
        self.Emulator = Emulator
        # this sets the close event, if user clicks "X"
        self.Emulator.closeEvent = self.closeEvent
        self.centralwidget = QtWidgets.QWidget(Emulator)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(1040, 20, 341, 71))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.lblFlags = QtWidgets.QLabel(self.groupBox)
        self.lblFlags.setGeometry(QtCore.QRect(254, 20, 71, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblFlags.setFont(font)
        self.lblFlags.setObjectName("lblFlags")
        self.lblSP = QtWidgets.QLabel(self.groupBox)
        self.lblSP.setGeometry(QtCore.QRect(204, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblSP.setFont(font)
        self.lblSP.setObjectName("lblSP")
        self.lblSR = QtWidgets.QLabel(self.groupBox)
        self.lblSR.setGeometry(QtCore.QRect(174, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblSR.setFont(font)
        self.lblSR.setObjectName("lblSR")
        self.lblYR = QtWidgets.QLabel(self.groupBox)
        self.lblYR.setGeometry(QtCore.QRect(143, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblYR.setFont(font)
        self.lblYR.setObjectName("lblYR")
        self.lblXR = QtWidgets.QLabel(self.groupBox)
        self.lblXR.setGeometry(QtCore.QRect(113, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblXR.setFont(font)
        self.lblXR.setObjectName("lblXR")
        self.lblAc = QtWidgets.QLabel(self.groupBox)
        self.lblAc.setGeometry(QtCore.QRect(80, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblAc.setFont(font)
        self.lblAc.setObjectName("lblAc")
        self.lblPC = QtWidgets.QLabel(self.groupBox)
        self.lblPC.setGeometry(QtCore.QRect(30, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblPC.setFont(font)
        self.lblPC.setObjectName("lblPC")
        self.txtPC = QtWidgets.QLineEdit(self.groupBox)
        self.txtPC.setGeometry(QtCore.QRect(20, 40, 41, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtPC.setFont(font)
        self.txtPC.setObjectName("txtPC")
        self.txtAC = QtWidgets.QLineEdit(self.groupBox)
        self.txtAC.setGeometry(QtCore.QRect(76, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtAC.setFont(font)
        self.txtAC.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtAC.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtAC.setObjectName("txtAC")
        self.txtXR = QtWidgets.QLineEdit(self.groupBox)
        self.txtXR.setGeometry(QtCore.QRect(110, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtXR.setFont(font)
        self.txtXR.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtXR.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtXR.setObjectName("txtXR")
        self.txtYR = QtWidgets.QLineEdit(self.groupBox)
        self.txtYR.setGeometry(QtCore.QRect(140, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtYR.setFont(font)
        self.txtYR.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtYR.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtYR.setObjectName("txtYR")
        self.txtSR = QtWidgets.QLineEdit(self.groupBox)
        self.txtSR.setGeometry(QtCore.QRect(170, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtSR.setFont(font)
        self.txtSR.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtSR.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtSR.setObjectName("txtSR")
        self.txtSP = QtWidgets.QLineEdit(self.groupBox)
        self.txtSP.setGeometry(QtCore.QRect(200, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtSP.setFont(font)
        self.txtSP.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtSP.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtSP.setObjectName("txtSP")
        self.txtFlags = QtWidgets.QLineEdit(self.groupBox)
        self.txtFlags.setGeometry(QtCore.QRect(245, 40, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        self.txtFlags.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtFlags.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtFlags.setObjectName("txtFlags")

        # Die Gruppe für die Zeropage
        self.grpZP = QtWidgets.QGroupBox(self.centralwidget)
        self.grpZP.setGeometry(QtCore.QRect(780, 110, 641, 200))
        self.grpZP.setObjectName("grpZP")
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        #self.txtZP = QtWidgets.QPlainTextEdit(self.grpZP)
        self.txtZP = myTextEdit(self.grpZP)
        self.txtZP.setGeometry(QtCore.QRect(10, 30, 621, 150))
        self.txtZP.setObjectName("txtZP")
        self.txtZP.setFont(font)

        # Die Gruppe für den Stack
        self.grpStack = QtWidgets.QGroupBox(self.centralwidget)
        self.grpStack.setGeometry(QtCore.QRect(780, 320, 641, 200))
        self.grpStack.setObjectName("grpStack")
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        self.txtStack = QtWidgets.QPlainTextEdit(self.grpStack)
        self.txtStack.setGeometry(QtCore.QRect(10, 30, 621, 150))
        self.txtStack.setObjectName("txtStack")
        self.txtStack.setFont(font)


        # Die Gruppe für das RAM
        self.grpRAM = QtWidgets.QGroupBox(self.centralwidget)
        self.grpRAM.setGeometry(QtCore.QRect(780, 530, 641, 320))
        self.grpRAM.setObjectName("grpRAM")
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        self.txtRAM = QtWidgets.QPlainTextEdit(self.grpRAM)
        self.txtRAM.setGeometry(QtCore.QRect(10, 30, 621, 266))
        self.txtRAM.setObjectName("txtRAM")
        self.txtRAM.setFont(font)


        self.cmdStep = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.startApple2())
        self.cmdStep.setGeometry(QtCore.QRect(110, 30, 75, 23))
        self.cmdStep.setObjectName("cmdStep")

        self.cmdStep1 = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.stopApple2())
        self.cmdStep1.setGeometry(QtCore.QRect(110, 60, 75, 23))
        self.cmdStep1.setObjectName("cmdStep")

        self.cmdLoadRom = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.loadRom())
        self.cmdLoadRom.setGeometry(QtCore.QRect(110, 90, 85, 23))
        self.cmdLoadRom.setObjectName("cmdLoadRom")

        Emulator.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Emulator)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuWindow = QtWidgets.QMenu(self.menubar)
        self.menuWindow.setObjectName("menuWindow")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        Emulator.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Emulator)
        self.statusbar.setObjectName("statusbar")
        Emulator.setStatusBar(self.statusbar)
        
        self.actionDisassembler = QtGui.QAction(Emulator)
        self.actionDisassembler.setObjectName("actionDisassembler")
        self.actionDisassembler.triggered.connect(self.showDisassembler)
        
        self.actionAssembler = QtGui.QAction(Emulator)
        self.actionAssembler.setObjectName("actionAssembler")
        self.actionAssembler.triggered.connect(self.showAssembler)
        
        self.actionExit = QtGui.QAction(Emulator)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.triggered.connect(self.exitProgram)

        self.menuWindow.addAction(self.actionDisassembler)
        self.menuWindow.addAction(self.actionAssembler)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())

        self.retranslateUi(Emulator)
        QtCore.QMetaObject.connectSlotsByName(Emulator)

    def retranslateUi(self, Emulator):
        _translate = QtCore.QCoreApplication.translate
        Emulator.setWindowTitle(_translate("Emulator", "Emulator"))
        self.groupBox.setTitle(_translate("Emulator", "Registers / Flags"))
        self.lblFlags.setText(_translate("Emulator", "NV-BDIZC"))
        self.lblSP.setText(_translate("Emulator", "SP"))
        self.lblSR.setText(_translate("Emulator", "SR"))
        self.lblYR.setText(_translate("Emulator", "YR"))
        self.lblXR.setText(_translate("Emulator", "XR"))
        self.lblAc.setText(_translate("Emulator", "AC"))
        self.lblPC.setText(_translate("Emulator", "PC"))
        self.txtPC.setText(_translate("Emulator", "0000"))
        self.txtAC.setText(_translate("Emulator", "00"))
        self.txtXR.setText(_translate("Emulator", "00"))
        self.txtYR.setText(_translate("Emulator", "00"))
        self.txtSR.setText(_translate("Emulator", "00"))
        self.txtSP.setText(_translate("Emulator", "00"))
        self.txtFlags.setText(_translate("Emulator", "00-00000"))
        self.grpRAM.setTitle(_translate("Emulator", "RAM"))
        self.grpZP.setTitle(_translate("Emulator", "Zero Page"))
        self.grpStack.setTitle(_translate("Emulator", "Stack"))
        self.cmdStep.setText(_translate("Emulator", "Step"))
        self.cmdStep1.setText(_translate("Emulator", "Stop"))
        self.cmdLoadRom.setText(_translate("Emulator", "Load Rom"))
        self.menuWindow.setTitle(_translate("Emulator", "Window"))
        self.menuFile.setTitle(_translate("Emulator", "File"))
        self.actionDisassembler.setText(_translate("Emulator", "Disassembler"))
        self.actionAssembler.setText(_translate("Emulator", "Assembler"))
        self.actionExit.setText(_translate("Emulator", "Exit"))

    # def eventFilter(self, obj, event):
    #     if obj is self.plainTextEdit and event.type() == QtCore.QEvent.KeyPress:
    #         if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
    #             print("Enter pressed")
    #             return True
    #     return super(MainWindow, self).eventFilter(obj, event)

    def loadRom(self):
        # File Dialog liefert die angeklickte Datei zurück
        fname = QFileDialog.getOpenFileName(None, "Open File", ".\\", "Rom Files (*.rom)")
        if fname[0]:
            # decodieren der Datei
            #self.decode_file(fname[0])
            #self.read_file(fname[0])
            pass



    #####
    
    #  Menu Functions

    #
    # def exitProgram(self): 
    #
    # User clicked File | Exit
    # Program will be closed
    #

    def exitProgram(self):
        exit(0)

    #
    # def closeEvent(self, event): 
    #
    # User clicked "X" button
    # Program will be closed
    #

    def closeEvent(self, event):
        exit(0)

    #
    # def showDisassembler(self):
    #
    # User clicked Windows | Disassembler
    # Program will open a disassembler view
    # help from: https://www.youtube.com/watch?v=R5N8TA0KFxc
    #

    def showDisassembler(self):
        self.window_dis = QtWidgets.QMainWindow()
        self.disasm = Ui_DisassemblerWindow()
        self.disasm.setupUi(self.window_dis)
        self.window_dis.show()

    #
    # def showDisassembler(self):
    #
    # User clicked Windows | Assembler
    # Program will open a assembler view
    # help from: https://www.youtube.com/watch?v=R5N8TA0KFxc
    #

    def showAssembler(self):
        self.window_asm = QtWidgets.QMainWindow()
        self.asm = Ui_AssemblerWindow()
        self.asm.setupUi(self.window_asm)
        self.window_asm.show()


    def startApple2(self):
        self.running = True
        myApple = Apple2(self)
        myApple.run()
        while self.running:
            # Die While-Schleife muss für Eventbehandlung unterbrochen werden, 
            # sonst haben wir hier eine Endlosschleife
            # Über ProcessEvents kann auch das Event auf den Stop-Button abgefragt werden,
            # das die Variable running auf False setzt und damit die Schleife beendet
            QtWidgets.QApplication.processEvents()
        print("Done")


    def stopApple2(self):
        self.running = False


    def updateRegisterFlags(self, myCPU):
        self.txtPC.setText(self.int2hex(myCPU.read_PC(),4))
        self.txtAC.setText(self.int2hex(myCPU.get_AC(),2))
        self.txtXR.setText(self.int2hex(myCPU.get_XR(),2))
        self.txtYR.setText(self.int2hex(myCPU.get_YR(),2))
        self.txtSP.setText(self.int2hex(myCPU.get_SP(),2))
        self.txtFlags.setText(myCPU.get_Flags())


    def updateMemoryView(self, myMemory):
        # Zeropage
        self.updateRAMView(myMemory, 0)
        # Stackpage
        self.updateRAMView(myMemory, 1)
        # RAM
        self.updateRAMView(myMemory, 2)


    def updateRAMView(self, myMemory, myRAM):
        if myRAM == 0:
            control = self.txtZP
            code_array = myMemory.dump_zeropage()
            address = 0x0000
        if myRAM == 1:
            control = self.txtStack
            code_array = myMemory.dump_stack()
            address = 0x0100
        if myRAM == 2:
            control = self.txtRAM
            code_array = myMemory.dump_ram() + myMemory.dump_rom()
            address = 0x0000

        control.clear()
        
        blocksize = 16
        for chunk in range(0,len(code_array), blocksize):
            if address < 65536:
                address_str = hex(address)[2:].upper().zfill(4) + ": "
                first_8 =  '{}'.format(' '.join(self.int2hex(x,2) for x in code_array[chunk:chunk+blocksize//2]))
                second_8 =  '{}'.format(' '.join(self.int2hex(x,2) for x in code_array[chunk+blocksize//2:chunk+blocksize]))
                first_asc = self.convert2ascii(code_array[chunk:chunk+blocksize//2])
                second_asc = self.convert2ascii(code_array[chunk+blocksize//2:chunk+blocksize])
                control.appendPlainText(address_str + " " + first_8 + "  " + second_8 + "  " + first_asc + " " + second_asc)
            address += blocksize
        txtCursor = control.textCursor()
        txtCursor.setPosition(0)
        control.setTextCursor(txtCursor)


    #
    # def convert2ascii(self, memblock):
    #
    # This method converts a hex byte to ascii char
    # for display in the memory editor
    #

    def convert2ascii(self, memblock):
        ascii_str = ''
        for i in memblock:
            if 0x20 < ord(chr(i)) < 0x7F:
                ascii_str += chr(i)
            else:
                ascii_str += "."
        return ascii_str
    #
    # def int2hex(x,y):
    #
    # Diese Methode wandelt einen int-Wert (x)
    # in einen hex-Wert der Länge (y) um
    #

    def int2hex(self,x,y):
        return hex(x)[2:].zfill(y).upper() 

```
