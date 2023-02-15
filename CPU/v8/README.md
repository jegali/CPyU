# Clipboard and copy/paste
Typing in the same program over and over again is quite exhausting. Especially if you do no have a possibility of saving your sources at hand - without cassette or Floppy Disk. So I decided to implement a copy/paste functionality to be able to copy source code from a Windows/Max/Linux editor to the Applesoft BASIC prompt.

## How does the Paste-function work
It is very convenient that the Apple polls the softswitch 0xC000 constantly. I found this out when I implemented an output in the method read_byte / read_bus when and how often the bus is polled. 0xC000 is actually constantly in operation. That was reason enough to think about using this polling actively by flooding the keyboard strobe with information. So I implemented a small routine that puts a letter on the line ten times in the main loop when CTRL is pressed. And, what can I say: this worked wonderfully.

So I looked on the internet how (and if) it is possible to read the clipboard of my computer and process it in Python. Result: you can. The library pyperclip provides exactly this functionality. Drawback: pyperclip can only process strings. For my purposes this is sufficient to edit Applesoftprogamme on the PC and then copy/paste them to the Apple. 

## Implementation
Pyperclip has be imported in clas beloved_apple.py:

```bash
import pygame
import numpy
import time
import pyperclip
```

If it is not found, it has to be installed beforehand. I used pip:

```bash
pip install pyperclip
```

The basis functionality of pyperclip ist pyperclip.copy("whatever you want to copy to clipboard") and pyperclip.paste(), which returns a string. I wanted to set up the clipboard function as I am used to from my Windows PC - when typing CTRL+V the clipboard should be pasted. The Apple and its keyboard input understand this key combination, it is signal 22 (or 0x16). For this signal I have extended the keyboard input routine (also class beloved_apple.py): 

```bash
       for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                print("quit")

            if event.type == VIDEORESIZE:
                pass

            if event.type == pygame.KEYDOWN:
                key = ord(event.unicode) if event.unicode else 0
                if event.key == pygame.K_LEFT:
                    key = 0x08
                if event.key == pygame.K_RIGHT:
                    key = 0x15
                if key:
                    if key == 0x7F:
                        key = 0x08
# --> NEW           # STRG + V: 
                    # über diese kombination wird gepasted
                    if key == 0x16:
                        paste_string = pyperclip.paste().replace('\n','')
                        if len(paste_string) > 0:
                            paste_count = len(paste_string)
                            paste = True
                    # jeden anderen Tastaturstroke entgegennehmen
                    # nur das paste nicht weiter bearbeiten, weil es 
                    # ansonsten die Eingabe zerstört
                    if key != 0x16:
                        softswitches.kbd = 0x80 + (key & 0x7F)
```

Of course, it must be taken into account that not all the text can be pasted at once. Within the emulation first again a bus access must have taken place, so that the I/O "process" knows that it has to do something. Therefore I have on the one hand set the variable paste to True in the keyboard query, on the other hand it is checked every 1024 cycles whether paste is set to True and then another character is put on the bus. This is done until the last character is pasted. So that the same thing is not pasted twice, the clipboard is cleared after successful pasting.

```bash
    # 75% CPU Zeit
    update_cycle_bus += 1
    if update_cycle_bus < 4:
        stepApple2()
    # 25% I/O Zeit
    else:    
        update_cycle_bus = 0
        # I/O Kanäle laufen über den Speicherbereich 0xc000-0xcfff
        # die Methode write_byte / read_byte überprüft die Adresse und erzeugt ein
        # Datenpaket mit Adresse, Wert und aktuellem Taktzyklus und speichert das
        # in einer queue
        # Hier wird die queue abgearbeitet
        if myApple.memory.bus_queue.qsize() > 0:
            bus_packet = myApple.memory.bus_queue.get()
            bus_cycle = bus_packet.cycle
            bus_address = bus_packet.address
            bus_value = bus_packet.value
            bus_rw = bus_packet.rw

            # wurde vom bus gelesen?
            if bus_rw == 0:
                softswitches.read_byte(bus_cycle, bus_address)
            # oder geschrieben
            elif bus_rw == 1:
                display.update(bus_address, bus_value)
                pass


            # alle 1024 Zyklen wird das Display
            # upgedatet und der Lautsprecher abgefragt
            update_cycle += 1
            if update_cycle >= 1024:

                # Der Benutzer hat etwas üner Copy+Paste
                # in den Emulator gegeben
                if paste:
                    paste_it()

```

The last part is the paste_it() method, which is called periodically from the I/O part of the main loop. The method still works with global variables in the test environment, this will be adjusted. Here the next character is read from the input buffer, placed on the keyboard line and then removed from the buffer. If the complete buffer is processed, the boolean variable paste is set to False again and the paste process is finished.

```bash
def paste_it():
    global paste_count
    global paste
    global paste_string
    softswitches.kbd = 0x80 + (ord(paste_string[0]) & 0x7F)
    paste_string = paste_string[1:]
    paste_count -= 1
    if paste_count <= 0 or len(paste_string) == 0:
        paste_string = ''
        pyperclip.copy('')
        paste = False
```

## Usage
Start the emulation by typing in:

```bash
python beloved_apple.py
```
