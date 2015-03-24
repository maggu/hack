#!/usr/bin/env python

# Copyright (C) 2015  C C Magnus Gustavsson
# Released under the GNU General Public License

# Entertainment for small children.

# When a key or combination of keys is pressed one of 16 tones are
# played and the screen is filled with one of 16 million colors. The
# tones and colors associated with the keys change daily. Press "l",
# "i", "n" and "a" (with no active lock keys) simultaneously to quit.

from hashlib import md5
from numpy import sin, pi, array, int8
from sys import exit
from time import strftime, time
from pygame.constants import *
import pygame

# Initialize sound
sample_rate = 11025
pygame.mixer.init(sample_rate, -16, 1)  # 16-bit mono

# Assign values between 0.9 and 1.1
vibrato = []
for t in xrange(sample_rate):
    vibrato.append(1.0 + 0.1 * sin(2.0 * pi * t / sample_rate))

# Create tones
tones = []
vol = 16.0
for n in xrange(-12, 20, 2):
    freq = 440.0 * pow(2.0, (n / 12.0))
    amp = []
    for t in xrange(sample_rate):
        amp.append(vol * sin(2.0 * pi * t / sample_rate * freq * vibrato[t]))

    tones.append(pygame.sndarray.make_sound(array(amp, int8)))

# Initialize graphics
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

# Initialize pygame
pygame.init()

def get_hash(data):
    hash = []
    day_of_year = strftime("%j")
    for byte in md5(str(data) + day_of_year).digest():
        hash.append(ord(byte))
    return hash

def play_tone(tone):
    tones[tone % 16].play()

def set_color(color):
    screen.fill(color)
    pygame.display.flip()

# Event loop
keys_pressed = set()
last_time = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)

            # Limit to five updates per second
            now = int(time() * 5.0)
            if now != last_time:
                hash = get_hash(keys_pressed)
                play_tone(hash[-1])
                set_color(hash[:3])
                last_time = now

        if event.type == pygame.KEYUP:
            if event.key in keys_pressed:
                keys_pressed.remove(event.key)

    if keys_pressed == {K_l, K_i, K_n, K_a}:
        exit(0)
