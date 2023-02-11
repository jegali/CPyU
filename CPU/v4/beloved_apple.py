import pygame
import numpy
import time

from pygame.locals import *

from apple2 import Apple2
from speaker import Speaker
from softswitches import SoftSwitches





myApple = Apple2(None)
speaker = Speaker()

softswitches = SoftSwitches(speaker)
update_cycle = 0
update_cycle_bus = 0
quit = False
display_screen = pygame.display.set_mode((560*2, 384*2))


def stepApple2():
    myApple.cpu.exec_command()


def main():
    global update_cycle
    global quit
    pygame.display.set_caption("CPyU - Jens' Apple Window")
    
    quit = False
    update_cycle = 0
    update_cycle_bus = 0
    while not quit:
        update_new()



def update_new():
    global update_cycle
    global update_cycle_bus
    global quit

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
                # später kommt hier das display
                pass

            # alle 1024 Zyklen wird das Display
            # upgedatet und der Lautsprecher abgefragt
            update_cycle += 1
            if update_cycle >= 1024:
                if speaker:
                    speaker.update(bus_cycle)
                update_cycle = 0

        # Tastatur und Fenster-Funktionen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                print("quit")


def update():
    global update_cycle
    global quit

    stepApple2()
    if myApple.memory.is_bus_read == 1:
        softswitches.read_byte(myApple.memory.is_bus_cycle, myApple.memory.is_bus_address )
    elif myApple.memory.is_bus_write == 1:
        display.update(myApple.memory.is_bus_address, myApple.memory.is_bus_value)

    update_cycle += 1
    if update_cycle >= 1024:
        display.flash()
        pygame.display.flip()
        if speaker:
            speaker.update(myApple.memory.is_bus_cycle)
        update_cycle = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True

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




if __name__ == "__main__":
    main()