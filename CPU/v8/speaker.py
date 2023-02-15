import numpy
import pygame

from pygame.locals import *


class Speaker:

    # ein bisschen testen mit der 23,
    # aber nun ist der beep genau 1kHz -
    # wie er sein soll
    CPU_CYCLES_PER_SAMPLE = 23
    CHECK_INTERVAL = 1000

    def __init__(self):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, allowedchanges=0)
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1, allowedchanges=0)
        self.reset()

    def toggle(self, cycle):
        if self.last_toggle is not None:
            # Aus dem Delta der vergangenen Taktzyklen seit dem letzten Mal
            # und der Anzahl der CPU-Cycles pro Sample
            # wird das Plateau der square-wave berechnet
            l = (cycle - self.last_toggle) // Speaker.CPU_CYCLES_PER_SAMPLE
            # Abfrage, in welcher Flanke wir uns befinden
            self.buffer.extend([0, 16384] if self.polarity else [0, -16384])
            # und die Flanke zusammenbauen
            self.buffer.extend((l - 2) * [16384] if self.polarity else (l-2)*[-16384])
            # dann die Polarität ändern
            self.polarity = not self.polarity
        self.last_toggle = cycle

    def reset(self):
        self.last_toggle = None
        self.buffer = []
        self.polarity = False

    def play(self):
        sample_array = numpy.int16(self.buffer)
        sound = pygame.sndarray.make_sound(sample_array)
        sound.play()
        self.reset()

    def update(self, cycle):
        if self.buffer and (cycle - self.last_toggle) > self.CHECK_INTERVAL:
            self.play()