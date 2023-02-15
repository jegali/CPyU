from floppydisk import FloppyDisk

class SoftSwitches:

    def __init__(self, speaker, display, myApple):
        self.kbd = 0x00
        self.myApple = myApple
        self.speaker = speaker
        self.display = display

    def read_byte(self, cycle, address, value):
        assert 0xC000 <= address <= 0xCFFF
        #if address >= 0xC100:
        #    print("Adresse:", hex(address))
        if address == 0xC000:
            self.myApple.memory.write_byte(cycle, address, self.kbd)
            return self.kbd
        elif address == 0xC010:
            self.kbd = self.kbd & 0x7F
            self.myApple.memory.write_byte(cycle, 0xc000, self.kbd)
        elif address == 0xC030:
            if self.speaker:
                self.speaker.toggle(cycle)
        elif address == 0xC050:
            self.display.txtclr()
        elif address == 0xC051:
            self.display.txtset()
        elif address == 0xC052:
            self.display.mixclr()
        elif address == 0xC053:
            self.display.mixset()
        elif address == 0xC054:
            self.display.lowscr()
        elif address == 0xC055:
            self.display.hiscr()
        elif address == 0xC056:
            self.display.lores()
        elif address == 0xC057:
            self.display.hires()
        # ein erster schüchterner Versuch, die Slots abzufragen
        elif ((address & 0xFF00) == 0xC000 and (address & 0xFF) >= 0x90):
            device = (address & 0x70) >> 4
            # Die Slots werden in der Klasse myApple gesetzt
            # in Slot 6 ist das Diskettenlaufwerk
            if self.myApple.slots[device] != None:
                return self.myApple.slots[device].softswitches(address, value)
                
            #return device ? device.update_soft_switch(addr, val) : 0;
  
        else:
            pass
        return 0x00
