#!/usr/bin/env python3
"""Wall Drops randomly drops some colours on left or right of tunnel

Try running with optional config name.
ex. ./wall-drops.py ocean
"""
__author__ = 'plong0 <plong00@gmail.com>'

import sys
import time
import random
from pprint import pprint
from LED_Tunnel import Tunnel

Maybe = 2

# fun settings - try adding your own config and playing with the options
configs = {
    'rainbow': {
        'colours': [
            (128, 0, 0), # dark red
            (255, 0, 0), # red
            (255, 165, 0), # orange
            (255, 192, 0), # orange
            (255, 255, 0), # yellow
            (0, 128, 0), # green
            (0, 255, 0), # green
            (0, 0, 128), # blue
            (0, 0, 255), # blue
            (192, 0, 192), # purple
            (192, 0, 255), # purple
            (255, 255, 255), # white
        ],
        'dropDelay': [0.25, 0.75],
        'dropWidth': 5,
        'mirror': True,
        'frameDelay': 0.07
    },
    'ocean': {
        'colours': [
            (0, 128, 192), # aqua
            (0, 192, 255), # aqua
            (0, 255, 255), # aqua
            (0, 0, 128), # blue,
            (0, 0, 192), # blue,
            (0, 0, 255), # blue,
            (0, 128, 0), # green
            (0, 192, 0), # green
            (0, 255, 0), # green
            (192, 0, 192), # purple
            (192, 192, 192), # white
            (255, 255, 255), # white
        ],
        'dropDelay': [0.125, 0.25],
        'dropWidth': 2,
        'mirror': False,
        'invert': True,
        'frameDelay': 0.05
    }
}
configs['rainbow-side'] = configs['rainbow'].copy()
configs['rainbow-side']['dropDelay'] = [0.25, 0.25]
configs['rainbow-side']['dropWidth'] = Tunnel.LEDS_PER_CHANNEL
configs['rainbow-side']['mirror'] = False
configs['rainbow-side']['frameDelay'] = 0.025

configs['rainbow-chunk'] = configs['rainbow-side'].copy()
configs['rainbow-chunk']['dropDelay'] = [0.25, 0.75]
configs['rainbow-chunk']['dropWidth'] = Tunnel.LEDS_PER_CHANNEL/5.0
configs['rainbow-chunk']['invert'] = Maybe


config_name = next(iter(configs))
if len(sys.argv) > 1:
    config_name = sys.argv[1]

if (config_name not in configs):
    sys.exit('Invalid config name: "{}"'.format(config_name))

config = configs[config_name]

# system settings
frameDelay = config['frameDelay'] if ('frameDelay' in config) else 0.05   # delay between frames - controls animation speed (increase to slow down)

# further customization
if len(sys.argv) > 2:
    config['trailLength'] = max(0, min(int(sys.argv[2]), TUNNEL.LEDS_PER_CHANNEL))

print('RUNNING CONFIG: "{}"'.format(config_name))
pprint(config)

# dropping stores the actively dropping channels
dropping = {}
dropping[Tunnel.LEFT_SIDE] = {}
dropping[Tunnel.RIGHT_SIDE] = {}

# dropDelay is how long until the next drop
dropDelay = 0

def should_drop():
    global timer
    global dropDelay
    return time.time() - timer >= dropDelay

def do_drop():
    global config
    global Maybe
    global dropDelay
    global pixels

    random.seed()

    # setup the drop
    drop = {
        'colourIndex': random.randint(0, len(config['colours'])-1),
        'progress': 0,
        'invert': config['invert'] if ('invert' in config) else False
    }

    if (drop['invert'] == Maybe):
        drop['invert'] = (random.randint(0, 1) == 1)

    # TODO: fix dropRadius for odd-numbered dropWidth
    dropRadius = int(config['dropWidth']/2)

    minDepth = dropRadius-1
    maxDepth = Tunnel.LEDS_PER_CHANNEL-1-dropRadius

    if (config['mirror']):
        # use a loop to prevent dropping at depths that are already dropping
        tried = []
        while True:
            dropDepth = random.randint(minDepth, maxDepth)
            if (dropDepth not in dropping[Tunnel.LEFT_SIDE] and dropDepth not in dropping[Tunnel.RIGHT_SIDE]):
                break;
            tried.append(dropDepth)
            if (len(tried) >= Tunnel.LEDS_PER_CHANNEL):
                break

        if (len(tried) < Tunnel.LEDS_PER_CHANNEL):
            # start the drop!
            for depth in range(max(0, dropDepth-dropRadius), min(Tunnel.LEDS_PER_CHANNEL-1, dropDepth+dropRadius)):
                dropping[Tunnel.LEFT_SIDE][depth] = drop.copy()
                dropping[Tunnel.RIGHT_SIDE][depth] = drop.copy()

    else:
        # randomly select which side to drop on
        dropSide = random.randint(Tunnel.LEFT_SIDE, Tunnel.RIGHT_SIDE)

        # use a loop to prevent dropping at depths that are already dropping
        tried = []
        while True:
            dropDepth = random.randint(minDepth, maxDepth)
            if (dropDepth not in dropping[dropSide]):
                break;
            tried.append(dropDepth)
            if (len(tried) >= Tunnel.LEDS_PER_CHANNEL):
                break

        if (len(tried) < Tunnel.LEDS_PER_CHANNEL):
            # start the drop!
            for depth in range(max(0, dropDepth-dropRadius), min(Tunnel.LEDS_PER_CHANNEL-1, dropDepth+dropRadius)):
                dropping[dropSide][depth] = drop.copy()

    # randomize delay until next drop
    dropDelay = random.uniform(config['dropDelay'][0], config['dropDelay'][1])

    # track time
    timer = time.time()

def update_drops():
    global config
    global dropping
    global pixels

    for side in dropping:
        finished = []
        for depth in dropping[side]:
            height = dropping[side][depth]['progress'] if (dropping[side][depth]['invert']) else Tunnel.SIDE_MATRIX_SIZE[1]-1-dropping[side][depth]['progress']
            index = Tunnel.get_pixel_index_by_side(side, depth, height)

            pixels[index] = config['colours'][dropping[side][depth]['colourIndex']]

            dropping[side][depth]['progress'] += 1

            if (dropping[side][depth]['progress'] >= Tunnel.SIDE_MATRIX_SIZE[1]):
                finished.append(depth)
        
        for finishedDepth in finished:
            del dropping[side][finishedDepth]



timer = time.time()
pixels = [ (0,0,0) ] * Tunnel.LED_COUNT

while True:
    if should_drop():
        do_drop();

    update_drops();

    Tunnel.Client.put_pixels(pixels)
    time.sleep(frameDelay)
