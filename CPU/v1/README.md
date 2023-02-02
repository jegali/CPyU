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

    # LOAD / STORE

    def LDA(self, operand_address):
        print("LDA")
        self.accumulator = self.update_nz(self.read_byte(operand_address))
        print("Akku: " + str(self.accumulator))
    #####

    def immediate_mode(self):
        return self.get_PC()

    #####

    def update_nz(self, value):
        value = value % 0x100
        self.zero_flag = [0, 1][(value == 0)]
        self.sign_flag = [0, 1][((value & 0x80) != 0)]
        return value

    def update_nzc(self, value):
        self.carry_flag = [0, 1][(value > 0xFF)]
        return self.update_nz(value)

    #####

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
