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
