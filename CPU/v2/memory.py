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
        # xxx todo
        # bus read ist noch nicht implementiert
        # auch der speicherbereich zwischen c000 und d000 
        # ist noch nicht initialisiert
        elif address < 0xD000:
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
    
