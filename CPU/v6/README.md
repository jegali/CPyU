# Keyboard
The keyboard was the easiest I/O component to implement. Unfortunately, it didn't make sense without a screen output - 
that's why I'm only going into the keyboard now.

## How does the keyboard work
Oh, actually quite simple. When the user presses a key, the byte value of that key is put on the address bus - 
at address 0xC000. There the value stays until it is deleted again. Usually this happens when you write something to 0xC001.

## Softswitches
When I started working with the keyboard, I came into contact with softswitches for the first time. So the implementation of the keyboard made sure that the memory area 0xC000 - 0xCFFF was implemented in the class memory. You remember:

```bash
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
```

You should also see the glitch in the read_byte method. Actually, a value should be returned, which doesn't happen when reading from the bus. I ironed out this error in the softswitches.py class. Here I write back the value, at least when handling the keyboard.

```bash
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
```

## Keyboard Emulation

Actually, a keyboard treatment is nothing mysterious. All I had to do was take every keystroke through pygame and convert it to the appropriate code that the Apple ][ understands. Something like ASCII (American standard code for information interchange) already existed in Apple's day, but Apple had its own bytecode. So I wrote a little keyboard handling routine:

```bash
       # Tastatur und Fenster-Funktionen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                print("quit")

            if event.type == pygame.KEYDOWN:
                key = ord(event.unicode) if event.unicode else 0
                if event.key == pygame.K_LEFT:
                    key = 0x08
                if event.key == pygame.K_RIGHT:
                    key = 0x15
                if key:
                    if key == 0x7F:
                        key = 0x08
                    softswitches.kbd = 0x80 + (key & 0x7F)
```

And that's it. The whole mystery of keyboard emulation. I didn't write my own routine or class for it, but left the few lines in the main loop...
