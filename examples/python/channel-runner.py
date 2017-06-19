#!/usr/bin/env python3

import opc, time

client = opc.Client('localhost:7890')

numChannels = 48
ledsPerChannel = 64
launchDelay = 1.125
trailLength = 32

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
        launched[channel] = 1
        timer = time.time()
        return True
    return False

def pixel_index(channel, index):
    global ledsPerChannel
    return (channel * ledsPerChannel + index)

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
            start = launched[i] - 1
            for j in range(start, max(0, start-trailLength), -1):
                if (j < ledsPerChannel):
                    index = pixel_index(i, j)
                    strength = (trailLength - start - j) / trailLength
                    pixels[index] = (127 - strength * 128, strength * 255, 191 + strength * 64)

            launched[i] += 1
            if (launched[i] > ledsPerChannel + trailLength):
                launched[i] = 1

    client.put_pixels(pixels)
    time.sleep(0.01)
