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

