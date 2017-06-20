#!/usr/bin/env python3

import opc, time, sys
from pprint import pprint

client = opc.Client('localhost:7890')

# fun settings
configs = {
    'cyan-orange': {
        'launchDelay': 0.25,
        'trailLength': 32,
        'color1': (0, 255, 255),  # cyan
        'color2': (255, 153, 0)   # orange
    },
    'pink-yellow': {
        'launchDelay': 0.125,
        'trailLength': 64,
        'color1': (255, 0, 255),  # magenta
        'color2': (255, 255, 0)   # yellow
    }
}

config_name = next(iter(configs))
if len(sys.argv) > 1:
    config_name = sys.argv[1]

if (config_name not in configs):
    sys.exit('Invalid config name: "{}"'.format(config_name))

config = configs[config_name]

# system settings
numChannels = 48
ledsPerChannel = 64

inverse = True      # if True, start at the back of the tunnel
frameDelay = 0.01   # delay between frames - controls animation speed (increase to slow down)

if len(sys.argv) > 2:
    config['trailLength'] = max(0, min(int(sys.argv[2]), ledsPerChannel))

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

def pixel_index(channel, index, invert=False, wrap=True):
    global ledsPerChannel
    # validate index is within bounds or is wrappable
    if (not wrap and (index < 0 or index >= ledsPerChannel)):
        return -1

    # wrap the index
    # careful with index wrapping when translating to other languages
    # python's modulo works here, some languages calculate it differently
    # More info: https://stackoverflow.com/questions/3883004/negative-numbers-modulo-in-python
    index = index % ledsPerChannel

    # calculate channel bounds
    channelFirst = channel * ledsPerChannel
    channelLast = channelFirst + ledsPerChannel - 1

    # calculate the index in the full pixel list
    if (invert):
        result = channelLast - index
    else:
        result = channelFirst + index

    return result

def color_in_range(color1, color2, position):
    return (color1[0]+(color2[0]-color1[0])*position, color1[1]+(color2[1]-color1[1])*position, color1[2]+(color2[2]-color1[2])*position)

timer = time.time()
while True:
    if should_launch():
        if do_launch(currentChannel):
            currentChannel += 1
            if (currentChannel > numChannels):
                currentChannel = 0

    pixels = [ (0,0,0) ] * numChannels * ledsPerChannel
    for i in range(numChannels):
        if (i in launched):
            start = launched[i]['start'] - 1
            for j in range(start, (start - config['trailLength']), -1):
                index = pixel_index(i, j, inverse, launched[i]['wrap'])
                if (index >= 0 and index < len(pixels)):
                    #strength = j / ledsPerChannel
                    strength = (start - j) / (config['trailLength'] - 1)
                    pixels[index] = color_in_range(config['color1'], config['color2'], strength)

            launched[i]['start'] += 1
            if (launched[i]['start'] > ledsPerChannel):
                launched[i]['start'] = 1
                launched[i]['wrap'] = True

    client.put_pixels(pixels)
    time.sleep(frameDelay)
