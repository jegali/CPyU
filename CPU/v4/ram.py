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
