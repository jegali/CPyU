import random

firmware = [0xA2,0x20,0xA0,0x00,0xA2,0x03,0x86,0x3C,0x8A,0x0A,0x24,0x3C,0xF0,0x10,0x05,0x3C,
            0x49,0xFF,0x29,0x7E,0xB0,0x08,0x4A,0xD0,0xFB,0x98,0x9D,0x56,0x03,0xC8,0xE8,0x10,
            0xE5,0x20,0x58,0xFF,0xBA,0xBD,0x00,0x01,0x0A,0x0A,0x0A,0x0A,0x85,0x2B,0xAA,0xBD,
            0x8E,0xC0,0xBD,0x8C,0xC0,0xBD,0x8A,0xC0,0xBD,0x89,0xC0,0xA0,0x50,0xBD,0x80,0xC0,
            0x98,0x29,0x03,0x0A,0x05,0x2B,0xAA,0xBD,0x81,0xC0,0xA9,0x56,0xa9,0x00,0xea,0x88,
            0x10,0xEB,0x85,0x26,0x85,0x3D,0x85,0x41,0xA9,0x08,0x85,0x27,0x18,0x08,0xBD,0x8C,
            0xC0,0x10,0xFB,0x49,0xD5,0xD0,0xF7,0xBD,0x8C,0xC0,0x10,0xFB,0xC9,0xAA,0xD0,0xF3,
            0xEA,0xBD,0x8C,0xC0,0x10,0xFB,0xC9,0x96,0xF0,0x09,0x28,0x90,0xDF,0x49,0xAD,0xF0,
            0x25,0xD0,0xD9,0xA0,0x03,0x85,0x40,0xBD,0x8C,0xC0,0x10,0xFB,0x2A,0x85,0x3C,0xBD,
            0x8C,0xC0,0x10,0xFB,0x25,0x3C,0x88,0xD0,0xEC,0x28,0xC5,0x3D,0xD0,0xBE,0xA5,0x40,
            0xC5,0x41,0xD0,0xB8,0xB0,0xB7,0xA0,0x56,0x84,0x3C,0xBC,0x8C,0xC0,0x10,0xFB,0x59,
            0xD6,0x02,0xA4,0x3C,0x88,0x99,0x00,0x03,0xD0,0xEE,0x84,0x3C,0xBC,0x8C,0xC0,0x10,
            0xFB,0x59,0xD6,0x02,0xA4,0x3C,0x91,0x26,0xC8,0xD0,0xEF,0xBC,0x8C,0xC0,0x10,0xFB,
            0x59,0xD6,0x02,0xD0,0x87,0xA0,0x00,0xA2,0x56,0xCA,0x30,0xFB,0xB1,0x26,0x5E,0x00,
            0x03,0x2A,0x5E,0x00,0x03,0x2A,0x91,0x26,0xC8,0xD0,0xEE,0xE6,0x27,0xE6,0x3D,0xA5,
            0x3D,0xCD,0x00,0x08,0xA6,0x2B,0x90,0xDB,0x4C,0x01,0x08,0x00,0x00,0x00,0x00,0x00]

DEFAULT_VOLUME = 254
NUM_DRIVES = 2
DOS_NUM_SECTORS = 16
DOS_NUM_TRACKS = 35
DOS_TRACK_BYTES = 256 * DOS_NUM_SECTORS
RAW_TRACK_BYTES = 0x1A00
STANDARD_2IMG_HEADER_SIZE = 64
STANDARD_PRODOS_BLOCKS = 280


class FloppyDisk:

    def __init__(self, myApple, slot) -> None:
        self.drive = 0
        self.is_motor_on = False
        self.is_write_protected = [0,1]
        self.disk_data = [[0 for i in range(2*DOS_NUM_TRACKS)], [0 for i in range(2*DOS_NUM_TRACKS)]]
        self.curr_phys_track = 0
        self.curr_nibble = 0
        
        self.drive_curr_phys_track = [0,0]
        self.real_track = [0 for i in range(RAW_TRACK_BYTES+1)]

        self.latch_data = 0
        self.write_mode = False
        self.load_mode = False
        self.drive_spin = False

        self.gcr_nibble_pos = 0
        self.gcr_nibbles = []

        self.setup_firmware(myApple, slot)



    def setup_firmware(self, myApple, slot):
        for i in range(0x100):
            myApple.memory.ram.write_byte(0xC000 + (slot << 8) + i, firmware[i])



    def io_read(self, address):
        switch = address & 0xf
        if switch == 0x0 or switch == 0x1 or switch == 0x2 or switch == 0x3 or \
           switch == 0x4 or switch == 0x5 or switch == 0x6 or switch == 0x7:
            self. set_phase(address)
        elif switch == 0x8:
            self.is_motor_on = False
        elif switch == 0x9:
            self.is_motor_on = True
        elif switch == 0xa:
            self.set_drive(0)
        elif switch == 0xb:
            self.set_drive(1)
        elif switch == 0xc:
            self.io_latch_c()
        elif switch == 0xd:
            self.load_mode = True
            if self.is_motor_on and not self.write_mode:
                self.latch_data &= 0x7F
                # TODO: check phase - write protect is forced if phase 1 is on [F9.7]
                if self.is_write_protected[self.drive]:
                    self.latch_data |= 0x80
        elif switch == 0xe:
            self.write_mode = False
        elif switch == 0xf:
            self.write_mode = True

        if (address & 1) == 0:
            if self.is_motor_on:
                return self.latch_data
            
            self.drive_spin = not self.drive_spin
            return 0x7e if self.drive_spin else 0x7f

        return random() * 256



    def io_write(self, address, value):
        switch = address & 0xf
        if switch == 0x0 or switch == 0x1 or switch == 0x2 or switch == 0x3 or \
           switch == 0x4 or switch == 0x5 or switch == 0x6 or switch == 0x7:
            self. set_phase(address)
        elif switch == 0x8:
            self.is_motor_on = False
        elif switch == 0x9:
            self.is_motor_on = True
        elif switch == 0xa:
            self.set_drive(0)
        elif switch == 0xb:
            self.set_drive(1)
        elif switch == 0xc:
            self.io_latch_c()
        elif switch == 0xd:
            self.load_mode = True
        elif switch == 0xe:
            self.write_mode = False
        elif switch == 0xf:
            self.write_mode = True

        if self.is_motor_on and self.write_mode and self.load_mode:
            self.latch_data = value


    # self.real_track müsste hier ein array zugewiesen werden.
    # ist aber nur ein "int", und damit kracht es in ioLatch, 
    # denn dort wird self_track indiziert 
    def set_phase(self, address):
        switch = address & 0xf
        phase = 0
        print("switch:", switch)
        if switch == 0x0 or switch == 0x2 or \
            switch == 0x4 or switch == 0x6:
            pass
        elif switch == 0x1:
            phase = self.curr_phys_track & 3
            if phase == 1:
                if self.curr_phys_track > 0:
                    self.curr_phys_track -= 1
            elif phase == 3:
                if self.curr_phys_track < (2 * DOS_NUM_TRACKS) -1:
                    self.curr_phys_track += 1
            self.real_track = self.disk_data[self.drive][self.curr_phys_track >> 1]
        elif switch == 0x03:
            phase = self.curr_phys_track & 3
            if phase == 2:
                if self.curr_phys_track > 0:
                    self.curr_phys_track -=1
            elif phase == 0:
                if self.curr_phys_track < (2 * DOS_NUM_TRACKS) - 1:
                    self.curr_phys_track += 1
            self.real_track = self.disk_data[self.drive][self.curr_phys_track >> 1]
        elif switch == 0x5:
            phase = self.curr_phys_track & 3
            if phase == 3:
                if self.curr_phys_track > 0:
                    self.curr_phys_track -=1
            elif phase == 1:
                if self.curr_phys_track < (2 * DOS_NUM_TRACKS) - 1:
                    self.curr_phys_track += 1
            self.real_track = self.disk_data[self.drive][self.curr_phys_track >> 1]
        elif switch == 0x7:
            phase = self.curr_phys_track & 3
            if phase == 0:
                if self.curr_phys_track > 0:
                    self.curr_phys_track -=1
            elif phase == 2:
                if self.curr_phys_track < (2 * DOS_NUM_TRACKS) - 1:
                    self.curr_phys_track += 1
            self.real_track = self.disk_data[self.drive][self.curr_phys_track >> 1]

        print("set_phase", self.real_track)



    def reset(self):
        self.io_read(0x8)


    def write_sync(self, length):
        self.write_nibbles(0xff, length)


    def write_nibbles(self, nibble, length):
        while length > 0:
            length -= 1
            self.gcr_write_nibble(nibble)


    def gcr_write_nibble(self, value):
        self.gcr_nibbles[self.gcr_nibble_pos] = value
        self.gcr_nibble_pos += 1


    def encode44(self, value):
        self.gcr_write_nibble((value >>1) | 0xaa)
        self.gcr_write_nibble(value | 0xaa)

    

    def set_drive(self, drive_num):
        self.drive_curr_phys_track[self.drive] = self.curr_phys_track
        self.drive = drive_num
        self.curr_phys_track = self.drive_curr_phys_track[self.drive]
        self.real_track = self.disk_data[self.drive][self.curr_phys_track >> 1]
        print("Drive selected: ", drive_num)



    def io_latch_c(self):
        self.load_mode = False
        if not self.write_mode:
            print("io latch nibble:",self.curr_nibble)
            print("real track", self.real_track)
            self.latch_data = self.real_track[self.curr_nibble] & 0xff
            print("io latch no write")
        else:
            print("io latch write 0xC0XD, 0xC0XC")
            self.real_track[self.curr_nibble] = self.latch_data
        
        self.curr_nibble += 1
        if self.curr_nibble >= RAW_TRACK_BYTES:
            self.curr_nibble = 0
        print("io Latch C")



    def softswitches(self, address, value):
        switch = address & 0xf
        if switch == 0x0 or switch == 0x1 or switch == 0x2 or switch == 0x3 or \
           switch == 0x4 or switch == 0x5 or switch == 0x6 or switch == 0x7:
            self.set_phase(address) 
        elif switch == 0x8:
            self.is_motor_on = False
        elif switch == 0x9:
            self.is_motor_on = True
        elif switch == 0xa:
            self.set_drive(0)
        elif switch == 0xb:
            self.set_drive(1)
        elif switch == 0xc:
            self.io_latch_c()
        elif 0xd:
            self.load_mode = True  
            # if (value === undefined && this.isMotorOn && !this.writeMode)
            # wa ist undefined in pythonv???
            if self.is_motor_on and not self.write_mode:
                self.latch_data &= 0x7f
                print("Hier in undefined load mode")
                # abfrage auf schreibschutz
                #// TODO: check phase - write protect is forced if phase 1 is on [F9.7]
                #if (this.isWriteProtected[this.drive]) {
                #this.latchData |= 0x80;
        elif 0xe:
            self.write_mode = False
        elif 0xf:
            self.write_mode = True

        # if value !=== undefined fehlt noch in der Abfrage
        if self.is_motor_on and self.write_mode and self.load_mode:
            self.latch_data = value

        # if value === undefined fehlt noch
        #         if (value === undefined && (address & 1) == 0) {
        #     // only even addresses return the latch
        #     if (this.isMotorOn) {
        #       return this.latchData;
        #     }

        #     // simple hack to fool DOS SAMESLOT drive spin check (usually at $BD34)
        #     this.driveSpin = !this.driveSpin;
        #     return this.driveSpin ? 0x7E : 0x7F;
        #   }

        return 0

    
