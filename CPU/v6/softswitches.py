class SoftSwitches:

    def __init__(self, speaker, display, myApple):
        self.kbd = 0x00
        self.myApple = myApple
        self.speaker = speaker
        self.display = display

    def read_byte(self, cycle, address):
        assert 0xC000 <= address <= 0xCFFF
        if address == 0xC000:
            self.myApple.memory.write_byte(cycle, address, self.kbd)
            return self.kbd
        elif address == 0xC010:
            self.kbd = self.kbd & 0x7F
            self.myApple.memory.write_byte(cycle, 0xc000, self.kbd)
        elif address == 0xC030:
            if self.speaker:
                self.speaker.toggle(cycle)
        # elif address == 0xC050:
        #     self.display.txtclr()
        # elif address == 0xC051:
        #     self.display.txtset()
        # elif address == 0xC052:
        #     self.display.mixclr()
        # elif address == 0xC053:
        #     self.display.mixset()
        # elif address == 0xC054:
        #     self.display.lowscr()
        # elif address == 0xC055:
        #     self.display.hiscr()
        # elif address == 0xC056:
        #     self.display.lores()
        # elif address == 0xC057:
        #     self.display.hires()

        else:
            pass
        return 0x00
