# Generate a 440 Hz square waveform in Pygame by building an array of samples and play
# it for 5 seconds.  Change the hard-coded 440 to another value to generate a different
# pitch.
#
# Run with the following command:
#   python pygame-play-tone.py

from array import array
from time import sleep

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


t = 100
freqs = [400, 440, 605]


def play(i):
    Note(freqs[i]).play(t)
    sleep(0.3)


def dice(n):
    if n == 1:
        play(0)
    if n == 2:
        play(2)
        play(0)
    if n == 3:
        play(0)
        play(2)
        play(0)
    if n == 4:
        play(0)
        play(1)
        play(2)
        play(0)
    if n >= 5:
        play(0)
        play(0)
        for i in range((n - 4) // 2):
            play((2 * i + 1) % 2)
            play((2 * i) % 2)
        if n % 2 == 1:
            play((i + 1) % 2)
        play(2)
        play(0)


if __name__ == "__main__":
    pre_init(44100, -16, 1, 1024)
    pygame.init()
    dice(4)
    #Note(610).play(t)
    sleep(2)
