# CPU and emulation
In this readme I report about the changes and enhancements to the CPU and emulation since v1.

## ROM
Temporarily, a method for writing had to be added to the ROM class - if only to be able to bend the reset vector, which is located in ROM with the Apple ][.
Furthermore there are new methods to read not only bytes but also words. 

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


    #
    # def load_file(self, address, filename)
    #
    # This methode reads a ROM file byte by byte and writes 
    # it into the specified address.
    # Optimization: can a file read and copied at once ?
    #

    def load_file(self, address, filename):
        with open(filename, "rb") as f:
            byte = f.read(1)
            offset = 0
            while byte:
                self._mem[address - self.start + offset] = ord(byte)
                byte = f.read(1)
                offset += 1
    


    #
    # def read_byte(self, address):
    #
    # This method reads a single byte from the specified address
    #

    def read_byte(self, address):
        assert self.start <= address <= self.end
        return self._mem[address - self.start]



    #
    # def read_word(self, address):
    #
    # This method reads a word from the specified address
    # To do this, it uses the read_byte method twice and reads
    # two adjacent memory cells
    #

    def read_word(self, address):
        return self.read_byte(address) + (self.read_byte(address + 1) << 8)



    #
    # def write_byte(self, address, value):
    #
    # just for testing - a ROM cannot be read
    #

    def write_byte(self, address, value):
        assert self.start <= address <= self.end
        self._mem[address - self.start] = value



    #
    # def dump_mem(self):
    #
    # This method returns the whole memory block
    #

    def dump_mem(self):
        return self._mem[0:]

```

## RAM
No changes

## Memory
The class memory was extended by the possibilities of the memory dump. Furthermore, methods for reading and writing words were added. 

When initializing the memory, the ROM image of the Apple ][ is loaded directly. 

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
        # Das ROM initialiseren
        self.rom = ROM(0xD000, 0x3000)
        # Das Apple-Rom laden 
        self.rom.load_file(0xD000, "apple2.rom")
        
        #if options:
        #    self.rom.load_file(0xD000, options.rom)

        # Das RAM initialiseren
        self.ram = RAM(0x0000, 0xC000)
        # Der Bereich von # 0xC000 bis 0xCFFF ist reserviert
        # für IO und Ports / Slots
        # Ich setze den RAM auf 0xD000, bis ich eine Lösung gefunden habe
        self.ram = RAM(0x0000, 0xD000)

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


    def read_word(self, cycle, address):
        return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address + 1) << 8)


    def read_word_bug(self, cycle, address):
        if address % 0x100 == 0xFF:
            return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address & 0xFF00) << 8)
        else:
            return self.read_word(cycle, address)


    def write_byte(self, cycle, address, value):
        if address < 0xC000:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 or 0x2000 <= address < 0x5FFF:
            self.bus_write(cycle, address, value)
        # just for testing! ROM cannot be written
        if address >= 0xD000:
            self.rom.write_byte(address, value)


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



    #
    # def dump_ram(self):
    #
    # Lese das RAM aus [0x0000 - 0xCFFF]
    #

    def dump_ram(self):
        memdump = self.ram.dump_mem()
        return memdump



    #
    # def dump_rom(self):
    #
    # Lese das ROM aus [0xD000 - 0xFFFF]
    #

    def dump_rom(self):
        memdump = self.rom.dump_mem()
        return memdump



    #
    # def dump_zeropage(self):
    #
    # Lese die Zeropage aus [0x0000 - 0x00FF]
    #

    def dump_zeropage(self):
        memdump = self.ram.dump_mem()
        return memdump[0:256]



    #
    # def dump_stack(self):
    #
    # Lese die Stackpage aus [0x0100 - 0x01FF]
    #

    def dump_stack(self):
        memdump = self.ram.dump_mem()
        return memdump[256:512]



    #
    # def dump_ram(self):
    #
    # Lese den kompletten Speicherbereich aus [0x0000 - 0xFFFF]
    #

    def dump_mem(self):
        memdump = self.ram.dump_mem() + self.rom.dump_mem()
        return memdump
```    

## CPU
Most of the changes were made to the CPU class. First, a reset() function was added to the CPU. The 6502 has the peculiarity that at startup and reset the CPU reads the content of the memory location 0xFFFC and applies this value as start address of the program. Therefore the method reset() is now called when the CPU is initialized.

```bash
    def __init__(self, memory, emulator):

        self.program_counter = 0x0000
        
        self.accumulator = 0x00
        self.x_index = 0x00
        self.y_index = 0x00

        ...
        
        self.setup_ops()
        self.reset()
        
        ...
        
    #
    # def reset(self):
    #
    # A peculiarity of the 6502 is that the address 0xfffc of the 
    # memory is read when the CPU is switched on. The memory value 
    # found here is interpreted as the start address of the program. 
    #

    def reset(self):
        self.program_counter = self.read_word(self.RESET_VECTOR)
```

### Microcodes and address modes
The actual emulation consists of the implementation of the microcodes and their effect on the processor registers, flags and the program counter. In principle there are 0xFF possible instructions and thus 255 potential methods that have to be written - in addition there are the different address modes of the respective instructions.

I went to the internet for the emulation methods and use parts of the source code from https://github.com/jtauber/applepy/blob/master/cpu6502.py.

I never got this project up and running, which was one of the reasons why I wanted to write my own emulator. By taking over the functions I learned a lot about the processing methods of the CPU. Together with the book of Rodnay Zaks "Programming the 6502" (you can find it at https://ia800703.us.archive.org/30/items/Programming_the_6502_OCR/Programming_the_6502_OCR.pdf) I got a deeper knowledge of the emulation of a CPU.

What is very interesting about James' implementation is that he uses lambda functions. This concept is so time-saving that I rewrote my own disassembler and converted it to lambda function (I reported about it). The following is an excerpt of the CPU operations. I have - simply because it is boring to read 255 times the same - shortened the table and limited myself to the address modes and the command LDA, to which I have a very special relationship.

In the past, when there were no trainers and cheat modules for games, we had to cheat ourselves. There was also only a fixed memory without paging and/or swapping, no multitasking, and so you could assume that a program was always loaded into RAM and executed at the same place. Furthermore, the 6502 CPU had only three registers - the Accumulator, the X and the Y registers on which comparative operations (CMP) could be performed. The games in our childhood often started with three lives. When all lives were used up, the game was over. What can I say? There were two efficient ways for us to cheat.

- Possibility one: Find in the binary code the places where the accumulator was loaded with three: LDA #$03 (yes, most of the time it was the accumulator that initialized the lives) and set the value to #$80, start the game and have a look if it worked. 
- Possibility tow: Find the place where a CMP #$00 followed by a BNE / BEQ was in memory (here all lives were used up and a jump to the game over routine was pending), and reqrite the jmp to game over with a jump to continue the game.

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
```


### Command execution
The command execution of a single command is handled by the exec_command() method. Here the next byte is read from memory, the associated command is decoded and executed. 

```bash
   def exec_command(self):
        # read the current byte and increment pc
        opcode = self.read_pc_byte()
        func_to_call = self.ops[opcode]
        if func_to_call is None:
            print ("UNKNOWN OPCODE")
            print (hex(self.program_counter - 1))
            print (hex(opcode))
            self.BRK()
        else:
            # execute
            self.ops[opcode]()
```

This method can be called via a button on the GUI of the emulator. This allows a step-by-step emulation.

## Class Apple
There were no changes in this class. 

## Emulator Window
The emulator class has a new area in which the current instruction to be processed is displayed: 

![Emulator-v2](/images/emulator-v2.png)

The other changes were small but time consuming. I contemplated how to make a connection between emulator and disassembler so that already existing Disassmbler functions can be used within the emulator window. I also asked myself whether a reference to the memory area can be passed so that the copy of the memory block in the disassembler is automatically changed when there is a write command. unfortunately that was not the case...

```bash
   def __init__(self) -> None:
        self.myApple = None
        self.disasm_preview = Ui_DisassemblerWindow()
    
    ...
    
    def setupUi(self, Emulator):
    Emulator.setObjectName("Emulator")
    Emulator.resize(1440, 900)
    self.Emulator = Emulator
    ...
    self.myApple = Apple2(self)


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
        self.disasm.setupParent(self)
        self.disasm.setupUi(self.window_dis)
        if self.myApple:
            self.disasm.transfer_memory(self.myApple.dump_mem())
            self.disasm.fill_code_view(bytearray(self.myApple.dump_mem()))
            self.disasm.disassemble()
        self.window_dis.show()
        
    ...

    def startApple2(self):
        self.running = True
        #self.myApple = Apple2(self)
        self.updateRegisterFlags(self.myApple.cpu)
        self.disasm_preview.transfer_memory(self.myApple.dump_mem())
        self.lblCmd.setText(self.disasm_preview.disassemble_command(self.myApple.read_PC(),self.myApple.dump_mem()))
        #self.myApple.run()
        while self.running:
            # Die While-Schleife muss für Eventbehandlung unterbrochen werden, 
            # sonst haben wir hier eine Endlosschleife
            # Über ProcessEvents kann auch das Event auf den Stop-Button abgefragt werden,
            # das die Variable running auf False setzt und damit die Schleife beendet
            QtWidgets.QApplication.processEvents()
        print("Done")

    def stepApple2(self):
        self.myApple.memory.write_byte(0, 2, 0xa9)
        self.myApple.cpu.exec_command()
        self.updateRegisterFlags(self.myApple.cpu)
        self.lblCmd.setText(self.disasm_preview.disassemble_command(self.myApple.read_PC(),self.myApple.dump_mem()))

    def stopApple2(self):
        self.running = False

```
