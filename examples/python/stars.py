#!/usr/bin/env python3
"""Stars lights up random LEDs

Try running with optional config name.
ex. ./stars.py blackberry
"""
__author__ = 'plong0 <plong00@gmail.com>'

import sys
import time
import random
from pprint import pprint
from LED_Tunnel import Tunnel

# fun settings - try adding your own config and playing with the options
configs = {
    'basic': {
        'launchDelay': 0.1,
        'maximum': int(Tunnel.LED_COUNT*2.0/3.0),
        'fadeIn': [0.2, 0.3],
        'lifespan': [1.0, 5.0],
        'fadeOut': [0.25, 0.5],
        'colours': [
            (255, 255, 0), # yellow
            (255, 192, 0), # orange
            (255, 255, 255) # white
        ]
    },
    'blackberry': {
        'launchDelay': 0.0,
        'maximum': int(Tunnel.LED_COUNT*0.75),
        'fadeIn': [0.2, 0.3],
        'lifespan': [1.0, 5.0],
        'fadeOut': [0.25, 0.5],
        'colours': [
            (192, 0, 255), # purple
            (255, 128, 255), # light purple
            (255, 192, 255) # white
        ]
    }
};

config_name = next(iter(configs))
if len(sys.argv) > 1:
    config_name = sys.argv[1]

if (config_name not in configs):
    sys.exit('Invalid config name: "{}"'.format(config_name))

config = configs[config_name]

# system settings
inverse = True      # if True, start at the back of the tunnel
frameDelay = 0.01   # delay between frames - controls animation speed (increase to slow down)

print('RUNNING CONFIG: "{}"'.format(config_name))
pprint(config)

activeStars = {}
lastLaunch = None

def should_launch():
    global activeStars, lastLaunch
    return len(activeStars) < config['maximum'] and (lastLaunch is None or time.time() - lastLaunch >= config['launchDelay'])

def do_launch():
    global activeStars, lastLaunch
    random.seed()
    index = random.randint(0, Tunnel.LED_COUNT-1)
    if index not in activeStars:
        activeStars[index] = {
            'state': 0,
            'stateStart': time.time(),
            'colourIndex': random.randint(0, len(config['colours'])-1),
            'fadeIn': random.uniform(config['fadeIn'][0], config['fadeIn'][1]),
            'lifespan': random.uniform(config['lifespan'][0], config['lifespan'][1]),
            'fadeOut': random.uniform(config['fadeOut'][0], config['fadeOut'][1])
        }

        lastLaunch = time.time()

while True:
    if should_launch():
        do_launch()

    pixels = [ (0,0,0) ] * Tunnel.LED_COUNT
    killStars = []
    for index in activeStars:
        activeStar = activeStars[index]

        stateTime = time.time() - activeStar['stateStart']

        if activeStar['state'] == 0:
            stateProg = stateTime / activeStar['fadeIn']
            colour1 = (0,0,0)
            colour2 = config['colours'][activeStar['colourIndex']]

        elif activeStar['state'] == 1:
            stateProg = stateTime / activeStar['lifespan']
            colour1 = config['colours'][activeStar['colourIndex']]
            colour2 = config['colours'][activeStar['colourIndex']]

        elif activeStar['state'] == 2:
            stateProg = stateTime / activeStar['lifespan']
            colour1 = config['colours'][activeStar['colourIndex']]
            colour2 = (0,0,0)
            if stateProg >= 1.0:
                killStars.append(index)


        if index not in killStars:
            if stateProg >= 1.0:
                activeStar['state'] += 1
                activeStar['stateStart'] = time.time()
                stateProg = 1.0

            pixels[index] = ( colour1[0]+(colour2[0]-colour1[0])*stateProg, colour1[1]+(colour2[1]-colour1[1])*stateProg, colour1[2]+(colour2[2]-colour1[2])*stateProg )

    # kill the expired stars
    for index in killStars:
        activeStars.pop(index, None)
            

    Tunnel.Client.put_pixels(pixels)
    time.sleep(frameDelay)
