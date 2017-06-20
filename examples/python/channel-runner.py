#!/usr/bin/env python3

import opc, time

client = opc.Client('localhost:7890')

# fun settings
launchDelay = 0.25  # value in seconds between channel start
trailLength = 32    # maximum 64

#color1 = (255, 0, 255) # magenta
#color2 = (255, 255, 0) # yellow
color1 = (0, 255, 255) # cyan
color2 = (255, 153, 0) # orange

# system settings
numChannels = 48
ledsPerChannel = 64

inverse = True      # if True, start at the back of the tunnel
frameDelay = 0.01   # delay between frames - controls animation speed (increase to slow down)

# setup
colorShift = (color2[0]-color1[0], color2[1]-color1[1], color2[2]-color1[2])
currentChannel = 0
launched = {}

def should_launch():
    global launched
    global timer
    return not launched or time.time() - timer >= launchDelay

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
            for j in range(start, (start-trailLength), -1):
                index = pixel_index(i, j, inverse, launched[i]['wrap'])
                if (index >= 0 and index < len(pixels)):
                    #strength = j / ledsPerChannel
                    strength = (start - j) / (trailLength - 1)
                    pixels[index] = (color1[0]+colorShift[0]*strength, color1[1]+colorShift[1]*strength, color1[2]+colorShift[2]*strength)

            launched[i]['start'] += 1
            if (launched[i]['start'] > ledsPerChannel):
                launched[i]['start'] = 1
                launched[i]['wrap'] = True

    client.put_pixels(pixels)
    time.sleep(frameDelay)
