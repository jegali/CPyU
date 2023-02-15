from ram import RAM
from rom import ROM

import queue
from dataclasses import dataclass

#
# Memory 
#
# This class consists of RAM and ROM


@dataclass
class Bus_IO:
    cycle: int
    rw: int
    address: int
    value: int


class Memory:

    def __init__(self, options=None, use_bus=True):
        self.use_bus = use_bus
        # Das ROM initialiseren
        self.rom = ROM(0xD000, 0x3000)
        # Das Apple-Rom laden 
        self.rom.load_file(0xD000, "apple2p.rom")
        
        self.is_bus_read = 0
        self.is_bus_write = 0
        self.is_bus_cycle = 0
        self.is_bus_address = 0
        self.is_bus_value = 0    

        self.bus_queue =  queue.Queue()   

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



    def read_byte(self, cycle, address):
        if address < 0xC000:
            return self.ram.read_byte(address)
        # auf dem Bus liegen die Adressen für die I/O
        # auch Keyboard, Tape und Speaker
        # für die korrekte Ausgabe des Speakers müssen die Taktzyklen mitgegeben
        # werden, da sich die Frequenz halt auch über die Anzahl der benötigten
        # cycles definiert
        elif address < 0xD000:
            value = self.ram.read_byte(address)
            #value = self.rom.read_byte(address)
            self.bus_read(cycle, address, value)
            return value
        else:
            return self.rom.read_byte(address)


    def read_word(self, cycle, address):
        return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address + 1) << 8)



    # der 6502 hat einen Hardwarebug - wie der Pentium
    # wenn im indirekten Modus die Adresse 0x00ff einer bestimmten Speicherseite gelesen wird,
    # dann liegt das zweite Byte der Adresse bei 00 und damit eigentlich auf einer neuen Seite
    # Der Bug der 6502 sorgt dafür, dass die Speicherstelle 00 der selben Seite genutzt wird - 
    # sizusagen ein "wraparound"
    def read_word_bug(self, cycle, address):
        if address % 0x100 == 0xFF:
            return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address & 0xFF00) << 8)
        else:
            return self.read_word(cycle, address)



    def write_byte(self, cycle, address, value):
        #if address < 0xC000:
        if address < 0xD000:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 or 0x2000 <= address < 0x5FFF:
            self.bus_write(cycle, address, value)
        # just for testing! ROM cannot be written
        if address >= 0xD000:
            self.rom.write_byte(address, value)



    def bus_read(self, cycle, address, value):
        buspacket = Bus_IO(cycle, 0, address, value)
        self.bus_queue.put(buspacket)



    def bus_write(self, cycle, address, value):
        buspacket = Bus_IO(cycle, 1, address, value)  
        self.bus_queue.put(buspacket)




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
    
