#!/usr/bin/env python3
"""Ringo Pulse sends nice rings along the tunnel

Try running with optional config name and phase
ex. ./ringo-pulse.py fire 10
"""
__author__ = 'plong0 <plong00@gmail.com>'

import sys
import time
import math
from pprint import pprint
from LED_Tunnel import Tunnel

# fun settings - try adding your own config and playing with the options
configs = {
    'deep-green': {
        'colour1': (0, 255, 192),  # turquoise
        'colour2': (0, 96, 0),   # dark green
        'phase': 3,
        'increment': 0.67
    },
    'fire': {
        'colour1': (255, 192, 0),  # golden orange
        'colour2': (192, 0, 0),   # red
        'phase': 7,
        'increment': 0.75
    },
    'blackberry': {
        'colour1': (192, 0, 255),   # purple
        'colour2': (255, 192, 255), # pale purple
        'phase': 5,
        'increment': 0.33
    }
}

config_name = next(iter(configs))
if len(sys.argv) > 1:
    config_name = sys.argv[1]

if (config_name not in configs):
    sys.exit('Invalid config name: "{}"'.format(config_name))

config = configs[config_name]

# allow further customization of selected config
if len(sys.argv) > 2:
    config['phase'] = int(sys.argv[2])

if len(sys.argv) > 3:
    config['increment'] = float(sys.argv[3])

print('RUNNING CONFIG: "{}"'.format(config_name))
pprint(config)

colour1 = config['colour1']
colour2 = config['colour2']
increment = config['increment'] if ('increment' in config) else 1
offset = config['offset'] if ('offset' in config) else 0
phase = config['phase'] if ('phase' in config) else 3

colourRange = (colour2[0]-colour1[0], colour2[1]-colour1[1], colour2[2]-colour1[2])

while True:
    pixels = [ (0,0,0) ] * Tunnel.LED_COUNT

    for i in range(Tunnel.LEDS_PER_CHANNEL):
        delta = i + offset
        if delta > Tunnel.LEDS_PER_CHANNEL:
            delta = delta - Tunnel.LEDS_PER_CHANNEL

        theta = delta / Tunnel.LEDS_PER_CHANNEL * (math.pi * phase)

        sinIndex = math.fabs(math.sin(theta))

        for j in range(Tunnel.CHANNEL_COUNT):
            index = Tunnel.get_pixel_index(j, i)
            pixels[index] = (
                colour1[0] + colourRange[0]*sinIndex,
                colour1[1] + colourRange[1]*sinIndex,
                colour1[2] + colourRange[2]*sinIndex
                )

    offset = offset + increment
    if (offset > Tunnel.LEDS_PER_CHANNEL):
        offset = 0

    Tunnel.Client.put_pixels(pixels)
    time.sleep(0.01)