#!/usr/bin/env python3
"""Channel Runner sends some gradient bars down each channel

Try running with optional config name.
ex. ./channel-runner.py pink-yellow
"""
__author__ = 'plong0 <plong00@gmail.com>'

import sys
import time
from pprint import pprint
from LED_Tunnel import Tunnel

# fun settings - try adding your own config and playing with the options
configs = {
    'cyan-orange': {
        'launchDelay': 0.25,
        'trailLength': 32,
        'colour1': (0, 255, 255),  # cyan
        'colour2': (255, 153, 0)   # orange
    },
    'pink-yellow': {
        'launchDelay': 0.125,
        'trailLength': 64,
        'colour1': (255, 0, 255),  # magenta
        'colour2': (255, 255, 0)   # yellow
    },
    'blackberry': {
        'launchDelay': 0.25,
        'trailLength': 48,
        'colour2': (192, 0, 255),  # purple
        'colour1': (255, 192, 255) # pale purple
    }
}

config_name = next(iter(configs))
if len(sys.argv) > 1:
    config_name = sys.argv[1]

if (config_name not in configs):
    sys.exit('Invalid config name: "{}"'.format(config_name))

config = configs[config_name]

# system settings
inverse = True      # if True, start at the back of the tunnel
frameDelay = 0.01   # delay between frames - controls animation speed (increase to slow down)

# further customization
if len(sys.argv) > 2:
    config['trailLength'] = max(0, min(int(sys.argv[2]), TUNNEL.LEDS_PER_CHANNEL))

print('RUNNING CONFIG: "{}"'.format(config_name))
pprint(config)

# setup
currentChannel = 0
launched = {}

def should_launch():
    global config
    global launched
    global timer
    return not launched or time.time() - timer >= config['launchDelay']

def do_launch(channel):
    global launched
    global timer
    if (channel not in launched):
        launched[channel] = {'start': 1, 'wrap': False}
        timer = time.time()
        return True
    return False

def colour_in_range(colour1, colour2, position):
    return (colour1[0]+(colour2[0]-colour1[0])*position, colour1[1]+(colour2[1]-colour1[1])*position, colour1[2]+(colour2[2]-colour1[2])*position)

timer = time.time()
while True:
    if should_launch():
        if do_launch(currentChannel):
            currentChannel += 1
            if (currentChannel > Tunnel.CHANNEL_COUNT):
                currentChannel = 0

    pixels = [ (0,0,0) ] * Tunnel.LED_COUNT
    for i in range(Tunnel.CHANNEL_COUNT):
        if (i in launched):
            start = launched[i]['start'] - 1
            for j in range(start, (start - config['trailLength']), -1):
                index = Tunnel.get_pixel_index(i, j, inverse, launched[i]['wrap'])
                if (index >= 0 and index < len(pixels)):
                    #strength = j / ledsPerChannel
                    strength = (start - j) / (config['trailLength'] - 1)
                    pixels[index] = colour_in_range(config['colour1'], config['colour2'], strength)

            launched[i]['start'] += 1
            if (launched[i]['start'] > Tunnel.LEDS_PER_CHANNEL):
                launched[i]['start'] = 1
                launched[i]['wrap'] = True

    Tunnel.Client.put_pixels(pixels)
    time.sleep(frameDelay)
