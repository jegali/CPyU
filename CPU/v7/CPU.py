from memory import Memory


class CPU(object):

    ZERO_PAGE = 0x0000
    STACK_PAGE = 0x0100
    RESET_VECTOR = 0xFFFC

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
        self.reset()


    
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


    #
    # def reset(self):
    #
    # A peculiarity of the 6502 is that the address 0xfffc of the 
    # memory is read when the CPU is switched on. The memory value 
    # found here is interpreted as the start address of the program. 
    #

    def reset(self):
        self.program_counter = self.read_word(self.RESET_VECTOR)
        

    #####

    # LOAD / STORE

    def LDA(self, operand_address):
        self.accumulator = self.update_nz(self.read_byte(operand_address))
    
    def LDX(self, operand_address):
        self.x_index = self.update_nz(self.read_byte(operand_address))

    def LDY(self, operand_address):
        self.y_index = self.update_nz(self.read_byte(operand_address))

    def STA(self, operand_address):
        self.write_byte(operand_address, self.accumulator)

    def STX(self, operand_address):
        self.write_byte(operand_address, self.x_index)

    def STY(self, operand_address):
        self.write_byte(operand_address, self.y_index)

    # TRANSFER

    def TAX(self):
        self.x_index = self.update_nz(self.accumulator)

    def TXA(self):
        self.accumulator = self.update_nz(self.x_index)

    def TAY(self):
        self.y_index = self.update_nz(self.accumulator)

    def TYA(self):
        self.accumulator = self.update_nz(self.y_index)

    def TSX(self):
        self.x_index = self.update_nz(self.stack_pointer)

    def TXS(self):
        self.stack_pointer = self.x_index

    # SHIFTS / ROTATES

    def ASL(self, operand_address=None):
        if operand_address is None:
            self.accumulator = self.update_nzc(self.accumulator << 1)
        else:
            self.cycles += 2
            self.write_byte(operand_address, self.update_nzc(self.read_byte(operand_address) << 1))

    def ROL(self, operand_address=None):
        if operand_address is None:
            a = self.accumulator << 1
            if self.carry_flag:
                a = a | 0x01
            self.accumulator = self.update_nzc(a)
        else:
            self.cycles += 2
            m = self.read_byte(operand_address) << 1
            if self.carry_flag:
                m = m | 0x01
            self.write_byte(operand_address, self.update_nzc(m))

    def ROR(self, operand_address=None):
        if operand_address is None:
            if self.carry_flag:
                self.accumulator = self.accumulator | 0x100
            self.carry_flag = self.accumulator % 2
            self.accumulator = self.update_nz(self.accumulator >> 1)
        else:
            self.cycles += 2
            m = self.read_byte(operand_address)
            if self.carry_flag:
                m = m | 0x100
            self.carry_flag = m % 2
            self.write_byte(operand_address, self.update_nz(m >> 1))

    def LSR(self, operand_address=None):
        if operand_address is None:
            self.carry_flag = self.accumulator % 2
            self.accumulator = self.update_nz(self.accumulator >> 1)
        else:
            self.cycles += 2
            self.carry_flag = self.read_byte(operand_address) % 2
            self.write_byte(operand_address, self.update_nz(self.read_byte(operand_address) >> 1))

    # JUMPS / RETURNS

    def JMP(self, operand_address):
        self.cycles -= 1
        self.program_counter = operand_address

    def JSR(self, operand_address):
        self.cycles += 2
        self.push_word(self.program_counter - 1)
        self.program_counter = operand_address

    def RTS(self):
        self.cycles += 4
        self.program_counter = self.pull_word() + 1

    # BRANCHES

    def BCC(self, operand_address):
        if not self.carry_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BCS(self, operand_address):
        if self.carry_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BEQ(self, operand_address):
        if self.zero_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BNE(self, operand_address):
        if not self.zero_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BMI(self, operand_address):
        if self.sign_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BPL(self, operand_address):
        if not self.sign_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BVC(self, operand_address):
        if not self.overflow_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BVS(self, operand_address):
        if self.overflow_flag:
            self.cycles += 1
            self.program_counter = operand_address

    # SET / CLEAR FLAGS

    def CLC(self):
        self.carry_flag = 0

    def CLD(self):
        self.decimal_mode_flag = 0

    def CLI(self):
        self.interrupt_disable_flag = 0

    def CLV(self):
        self.overflow_flag = 0

    def SEC(self):
        self.carry_flag = 1

    def SED(self):
        self.decimal_mode_flag = 1

    def SEI(self):
        self.interrupt_disable_flag = 1

    # INCREMENT / DECREMENT

    def DEC(self, operand_address):
        self.cycles += 2
        self.write_byte(operand_address, self.update_nz(self.read_byte(operand_address) - 1))

    def DEX(self):
        self.x_index = self.update_nz(self.x_index - 1)

    def DEY(self):
        self.y_index = self.update_nz(self.y_index - 1)

    def INC(self, operand_address):
        self.cycles += 2
        self.write_byte(operand_address, self.update_nz(self.read_byte(operand_address) + 1))

    def INX(self):
        self.x_index = self.update_nz(self.x_index + 1)

    def INY(self):
        self.y_index = self.update_nz(self.y_index + 1)

    # PUSH / PULL

    def PHA(self):
        self.cycles += 1
        self.push_byte(self.accumulator)

    def PHP(self):
        self.cycles += 1
        self.push_byte(self.status_as_byte())

    def PLA(self):
        self.cycles += 2
        self.accumulator = self.update_nz(self.pull_byte())

    def PLP(self):
        self.cycles += 2
        self.status_from_byte(self.pull_byte())

    # LOGIC

    def ORA(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator | self.read_byte(operand_address))

    def AND(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator & self.read_byte(operand_address))

    def EOR(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator ^ self.read_byte(operand_address))

    # ARITHMETIC

    def ADC(self, operand_address):
        # @@@ doesn't handle BCD yet
        assert not self.decimal_mode_flag

        a2 = self.accumulator
        a1 = self.signed(a2)
        m2 = self.read_byte(operand_address)
        m1 = self.signed(m2)

        # twos complement addition
        result1 = a1 + m1 + self.carry_flag

        # unsigned addition
        result2 = a2 + m2 + self.carry_flag

        self.accumulator = self.update_nzc(result2)

        # perhaps this could be calculated from result2 but result1 is more intuitive
        self.overflow_flag = [0, 1][(result1 > 127) | (result1 < -128)]

    def SBC(self, operand_address):
        # @@@ doesn't handle BCD yet
        assert not self.decimal_mode_flag

        a2 = self.accumulator
        a1 = self.signed(a2)
        m2 = self.read_byte(operand_address)
        m1 = self.signed(m2)

        # twos complement subtraction
        result1 = a1 - m1 - [1, 0][self.carry_flag]

        # unsigned subtraction
        result2 = a2 - m2 - [1, 0][self.carry_flag]

        self.accumulator = self.update_nz(result2)
        self.carry_flag = [0, 1][(result2 >= 0)]

        # perhaps this could be calculated from result2 but result1 is more intuitive
        self.overflow_flag = [0, 1][(result1 > 127) | (result1 < -128)]

    # BIT

    def BIT(self, operand_address):
        value = self.read_byte(operand_address)
        self.sign_flag = ((value >> 7) % 2)  # bit 7
        self.overflow_flag = ((value >> 6) % 2)  # bit 6
        self.zero_flag = [0, 1][((self.accumulator & value) == 0)]

    # COMPARISON

    def CMP(self, operand_address):
        result = self.accumulator - self.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)

    def CPX(self, operand_address):
        result = self.x_index - self.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)

    def CPY(self, operand_address):
        result = self.y_index - self.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)

    # SYSTEM

    def NOP(self):
        pass

    def BRK(self):
        self.cycles += 5
        self.push_word(self.program_counter + 1)
        self.push_byte(self.status_as_byte())
        self.program_counter = self.read_word(0xFFFE)
        self.break_flag = 1

    def RTI(self):
        self.cycles += 4
        self.status_from_byte(self.pull_byte())
        self.program_counter = self.pull_word()


    #
    # Different Address modes
    # Borrowed from:
    # https://github.com/jtauber/applepy
    #

    def immediate_mode(self):
        return self.get_PC()

    def absolute_mode(self):
        self.cycles += 2
        return self.read_pc_word()

    def absolute_x_mode(self, rmw=False):
        if rmw:
            self.cycles += 1
        return self.absolute_mode() + self.x_index

    def absolute_y_mode(self, rmw=False):
        if rmw:
            self.cycles += 1
        return self.absolute_mode() + self.y_index

    def zero_page_mode(self):
        self.cycles += 1
        return self.read_pc_byte()

    def zero_page_x_mode(self):
        self.cycles += 1
        return (self.zero_page_mode() + self.x_index) % 0x100

    def zero_page_y_mode(self):
        self.cycles += 1
        return (self.zero_page_mode() + self.y_index) % 0x100

    def indirect_mode(self):
        self.cycles += 2
        return self.read_word_bug(self.absolute_mode())

    def indirect_x_mode(self):
        self.cycles += 4
        return self.read_word_bug((self.read_pc_byte() + self.x_index) % 0x100)

    def indirect_y_mode(self, rmw=False):
        if rmw:
            self.cycles += 4
        else:
            self.cycles += 3
        return self.read_word_bug(self.read_pc_byte()) + self.y_index

    def relative_mode(self):
        pc = self.get_PC()
        return pc + 1 + self.signed(self.read_byte(pc))
 
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
            # self.ops[opcode]()
            pass



    def exec_command(self):
        # Jeder Befehl ben??tigt mindesten zwei Taktzyklen
        self.cycles += 2
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


    #
    # def read_PC(self):
    #
    # Just get the actual PC
    #

    def read_PC(self):
        return self.program_counter

    def read_AC(self):
        return self.accumulator

    def read_XR(self):
        return self.x_index

    def read_YR(self):
        return self.y_index
    
    def read_SP(self):
        return self.stack_pointer

    def read_Flags(self):
        return str(self.sign_flag) + str(self.overflow_flag) + "1" + str(self.break_flag) + str(self.decimal_mode_flag) + str(self.interrupt_disable_flag) + str(self.zero_flag) + str(self.carry_flag)


    #
    # def read_pc_byte(self):
    #
    # Get the byte from the current PC position
    # and increment PC
    #
    
    def read_pc_byte(self):
        return self.read_byte(self.get_PC())

    def read_byte(self, address):
        return self.memory.read_byte(self.cycles, address)
    
    def read_word(self, address):
        return self.memory.read_word(self.cycles, address)
    
    def read_pc_word(self):
        return self.read_word(self.get_PC(2))

    def read_word_bug(self, address):
        return self.memory.read_word_bug(self.cycles, address)

    def write_byte(self, address, value):
        self.memory.write_byte(self.cycles, address, value)

####

    def push_byte(self, byte):
        self.write_byte(self.STACK_PAGE + self.stack_pointer, byte)
        self.stack_pointer = (self.stack_pointer - 1) % 0x100

    def pull_byte(self):
        self.stack_pointer = (self.stack_pointer + 1) % 0x100
        return self.read_byte(self.STACK_PAGE + self.stack_pointer)

    def push_word(self, word):
        hi, lo = divmod(word, 0x100)
        self.push_byte(hi)
        self.push_byte(lo)

    def pull_word(self):
        s = self.STACK_PAGE + self.stack_pointer + 1
        self.stack_pointer += 2
        return self.read_word(s)

####

    def status_from_byte(self, status):
        self.carry_flag = [0, 1][0 != status & 1]
        self.zero_flag = [0, 1][0 != status & 2]
        self.interrupt_disable_flag = [0, 1][0 != status & 4]
        self.decimal_mode_flag = [0, 1][0 != status & 8]
        self.break_flag = [0, 1][0 != status & 16]
        self.overflow_flag = [0, 1][0 != status & 64]
        self.sign_flag = [0, 1][0 != status & 128]

    def status_as_byte(self):
        return self.carry_flag | self.zero_flag << 1 | self.interrupt_disable_flag << 2 | self.decimal_mode_flag << 3 | self.break_flag << 4 | 1 << 5 | self.overflow_flag << 6 | self.sign_flag << 7


    def signed(self, x):
        if x > 0x7F:
            x = x - 0x100
        return x