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
