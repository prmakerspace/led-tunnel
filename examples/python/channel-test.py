#!/usr/bin/env python3
"""This is for testing FadeCandy strips in a generic way.

While it does work with the LED Tunnel setup, it is designed to be independent of the tunnel.

It takes one command line argument for how many strips to test (default is 1):

Testing 1 strip:
./channel-test

Testing 4 strips:
./channel-test 4

Testing 48 strips (ie. the full tunnel):
./channel-test 48
"""
__author__ = 'plong0 <plong00@gmail.com>'

import sys
import time
from libs import opc

FADECANDY_SERVER_HOST = 'localhost'
FADECANDY_SERVER_PORT = 7890

LEDS_PER_CHANNEL = 64

CHANNEL_COUNT = 1   # default channel count

# read channel count from command-line argument
if len(sys.argv) > 1:
    CHANNEL_COUNT = int(sys.argv[1])

# effect timing
LAUNCH_DELAY    = 2.0   # how long to wait before launching next channel
FILL_TIME       = 4.0   # how long to fill one channel
RESET_DELAY     = 2.0   # how long to freeze on last colour before reset

# fades in between these colours
colours = [
    (255, 0, 0), # red
    (255, 192, 0), # orange
    (255, 255, 0), # yellow
    (0, 255, 0), # green
    (0, 192, 255), # cyan
    (192, 0, 255), # purple
    (255, 255, 255), # white
]

# calculated settings
FRAME_DELAY = FILL_TIME / LEDS_PER_CHANNEL
LED_COUNT = CHANNEL_COUNT * LEDS_PER_CHANNEL

# connect to fcserver
Client = opc.Client(FADECANDY_SERVER_HOST+":"+str(FADECANDY_SERVER_PORT))

# app state
currentChannel = 0
channelState = {}
channelHold = {}

# return a colour depending on state of channel
def get_colour(channel, index):
    global channelState, colours

    if channel in channelState:
        channelProgress = (channelState[channel] % LEDS_PER_CHANNEL)
        progress = channelProgress / LEDS_PER_CHANNEL

        ticks_per_colour = 1.0 / len(colours)
        colour_index = int(progress * len(colours))

        colour_start = ticks_per_colour * colour_index
        colour_percent = (progress - colour_start) / ticks_per_colour

        if index <= channelProgress:
            colour1 = colours[colour_index-1] if colour_index else (0, 0, 0)
            colour2 = colours[colour_index]

            colour = (colour1[0]+(colour2[0] - colour1[0])*colour_percent, colour1[1]+(colour2[1] - colour1[1])*colour_percent, colour1[2]+(colour2[2] - colour1[2])*colour_percent)

            return colour

    return (0, 0, 0)

# maps a local channel+index to global pixel index
def get_pixel_index(channel, index, invert=False, wrap=True):
    # validate index is within bounds or is wrappable
    if (not wrap and (index < 0 or index >= LEDS_PER_CHANNEL)):
        return -1

    # wrap the index
    # careful with index wrapping when translating to other languages
    # python's modulo works here, some languages calculate it differently
    # More info: https://stackoverflow.com/questions/3883004/negative-numbers-modulo-in-python
    index = index % LEDS_PER_CHANNEL

    # calculate channel bounds
    channelFirst = channel * LEDS_PER_CHANNEL
    channelLast = channelFirst + LEDS_PER_CHANNEL - 1

    # calculate the index in the full pixel list
    if (invert):
        result = channelLast - index
    else:
        result = channelFirst + index

    return result

timer = time.time()
while True:
    # do we launch the next channel?
    if (not channelState or time.time() - timer >= LAUNCH_DELAY) and currentChannel < CHANNEL_COUNT:
        channelState[currentChannel] = 0
        channelHold[currentChannel] = 0
        timer = time.time()
        currentChannel += 1

    # calculate all the pixel colours
    pixels = [ (0,0,0) ] * LED_COUNT
    for i in range(CHANNEL_COUNT):
        for j in range(LEDS_PER_CHANNEL):
            pixels[get_pixel_index(i, j)] = get_colour(i, j)

        if i in channelState:
            if channelState[i] == LEDS_PER_CHANNEL-1:
                if not channelHold[i]:
                    channelHold[i] = time.time()
                elif time.time() - channelHold[i] > RESET_DELAY:
                    channelState[i] = 0
                    channelHold[i] = 0
            else:
                channelState[i] += 1

    Client.put_pixels(pixels)
    time.sleep(FRAME_DELAY)
