#!/usr/bin/env python3

# Run with optional integer phase argument (default is 3)
# ex. ./ringo-pulse.py 5

import opc, time, math, sys

client = opc.Client('localhost:7890')

numChannels = 48
ledsPerChannel = 64

colour1 = (0, 255, 192)
colour2 = (0, 96, 0)
colourRange = (colour2[0]-colour1[0], colour2[1]-colour1[1], colour2[2]-colour1[2])
increment = 1
offset = 0
phase = 3

if len(sys.argv) > 1:
    phase = int(sys.argv[1])

def pixel_index(channel, index):
    global ledsPerChannel
    return (channel * ledsPerChannel + index)

while True:
    pixels = [ (0,0,0) ] * numChannels * ledsPerChannel

    for i in range(ledsPerChannel):
        delta = i + offset
        if delta > ledsPerChannel:
            delta = delta - ledsPerChannel

        theta = delta / ledsPerChannel * (math.pi * phase)

        sinIndex = math.fabs(math.sin(theta))

        for j in range(numChannels):
            index = pixel_index(j, i)
            pixels[index] = (
                colour1[0] + colourRange[0]*sinIndex,
                colour1[1] + colourRange[1]*sinIndex,
                colour1[2] + colourRange[2]*sinIndex
                )

    offset = offset + increment
    if (offset > ledsPerChannel):
        offset = 0

    client.put_pixels(pixels)
    time.sleep(0.01)
