# Generate a 440 Hz square waveform in Pygame by building an array of samples and play
# it for 5 seconds.  Change the hard-coded 440 to another value to generate a different
# pitch.
#
# Run with the following command:
#   python pygame-play-tone.py

from array import array
from time import sleep
import random

import pygame
from pygame.mixer import Sound, get_init, pre_init


class Note(Sound):

    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples


t = 10
dt = 0.2
freqs = [100, 200, 600]


def play(i):
    if i>=0:
        Note(freqs[i]).play(t)
    sleep(dt)


def beat(pattern):
    k = 0
    while True:
        play(0)
        for p in pattern:
            if p:
                play(2)
            else:
                play(-1)
        k += 1


if __name__ == "__main__":
    pre_init(44100, -16, 1, 1024)
    pygame.init()
    n_bits = 4
    pattern = random.choices([0, 1], k=2 ** n_bits-1)
    print(pattern)
    beat(pattern)
    sleep(2)
