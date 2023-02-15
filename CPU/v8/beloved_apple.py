import pygame
import numpy
import time
import pyperclip

from pygame.locals import *

from apple2 import Apple2
from speaker import Speaker
from display import Display
from softswitches import SoftSwitches


import pygame
import numpy
import time

from pygame.locals import *


myApple = Apple2(None)
display = Display()
speaker = Speaker()
softswitches = SoftSwitches(speaker, display, myApple)
update_cycle = 0
update_cycle_bus = 0
update_cycle_clipboard = 0
quit = False

# used for clipboard functionality
paste = False
paste_count = 10
paste_string = ''


def main():
    global update_cycle
    global quit
    pygame.display.set_caption("CPyU - Jens' Apple Window")
    
    quit = False
    update_cycle = 0
    update_cycle_bus = 0
    while not quit:
        update_new()



def paste_it():
    global paste_count
    global paste
    global paste_string
    softswitches.kbd = 0x80 + (ord(paste_string[0]) & 0x7F)
    paste_string = paste_string[1:]
    paste_count -= 1
    if paste_count < 0 or len(paste_string) == 0:
        paste_string = ''
        pyperclip.copy('')
        paste = False



def update_new():
    global update_cycle
    global update_cycle_bus
    global update_cycle_clipboard
    global quit
    global paste
    global paste_count
    global paste_string

    # 75% CPU Zeit
    update_cycle_bus += 1
    if update_cycle_bus < 4:
        myApple.cpu.exec_command()
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
                softswitches.read_byte(bus_cycle, bus_address, bus_value)
            # oder geschrieben
            elif bus_rw == 1:
                # später kommt hier das display
                display.update(bus_address, bus_value)
                pass

            # alle 1024 Zyklen wird das Display
            # upgedatet und der Lautsprecher abgefragt
            update_cycle += 1
            if update_cycle >= 16:
                display.flash()
                pygame.display.flip()
                if speaker:
                    speaker.update(bus_cycle)
                update_cycle = 0

            update_cycle_clipboard += 1
            if update_cycle_clipboard > 100:
                if paste:
                    paste_it()
                update_cycle_clipboard = 0


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
                    # STRG + V: 
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




if __name__ == "__main__":
    main()