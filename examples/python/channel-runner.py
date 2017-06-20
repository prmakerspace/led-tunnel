#!/usr/bin/env python3

import opc, time

client = opc.Client('localhost:7890')

numChannels = 48
ledsPerChannel = 64
launchDelay = 0.5
trailLength = 64

#color1 = (255, 0, 255) # magenta
#color2 = (255, 255, 0) # yellow
color1 = (255, 153, 0) # orange
color2 = (0, 255, 255) # cyan
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
            for j in range(start, max(-1, start-trailLength), -1):
                if (j < ledsPerChannel):
                    index = pixel_index(i, j)
                    #strength = j / ledsPerChannel
                    strength = (start - j) / trailLength
                    pixels[index] = (color1[0]+colorShift[0]*strength, color1[1]+colorShift[1]*strength, color1[2]+colorShift[2]*strength)

            launched[i] += 1
            if (launched[i] > ledsPerChannel + trailLength):
                launched[i] = 1

    client.put_pixels(pixels)
    time.sleep(0.01)
