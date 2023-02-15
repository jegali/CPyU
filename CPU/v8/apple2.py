from CPU import CPU
from memory import Memory
from floppydisk import FloppyDisk

class Apple2:

    def __init__(self, emulator) -> None:
        self.emulator = emulator
        self.memory = Memory()

        self.cpu = CPU(self.memory, emulator)
        
        if emulator is not None:
            emulator.updateRegisterFlags(self.cpu)
            emulator.updateMemoryView(self.memory)

        #self.slots = [None] * 8
        #self.slots[6] = FloppyDisk(self, 6)


    def run(self):
        #self.cpu.operation_cycle()
        pass

    #
    # Dies sind Wrapperfunktionen zum Auslesen 
    # der einzelnen Speicherbereiche
    # 
    
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

    def dump_mem(self):
        memdump = self.memory.dump_mem()
        return memdump


    def read_PC(self):
        return self.cpu.program_counter

    def read_AC(self):
        return self.cpu.accumulator

    def read_XR(self):
        return self.cpu.x_index

    def read_YR(self):
        return self.cpu.y_index
    
    def read_SP(self):
        return self.cpu.stack_pointer

    def read_Flags(self):
        return str(self.cpu.sign_flag) + str(self.cpu.overflow_flag) + "1" + str(self.cpu.break_flag) + str(self.cpu.decimal_mode_flag) + str(self.cpu.interrupt_disable_flag) + str(self.cpu.zero_flag) + str(self.cpu.carry_flag)
