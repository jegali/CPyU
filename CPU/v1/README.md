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
The RAM class inherits from the ROM class, which makes total sense. After all, the RAM has the same functions as the ROM, but in addition can also be written to the memory locations.

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
