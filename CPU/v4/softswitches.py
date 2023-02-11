class SoftSwitches:

    def __init__(self, speaker):
        self.speaker = speaker
        
    def read_byte(self, cycle, address):
        assert 0xC000 <= address <= 0xCFFF
        if address == 0xC030:
            if self.speaker:
                self.speaker.toggle(cycle)
        else:
            pass
        return 0x00
