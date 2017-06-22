#!/usr/bin/env python3
"""Wall Sines just pumps some sine waves on each side of the tunnel"""
__author__ = 'plong0 <plong00@gmail.com>'

import sys
import time
import math
from LED_Tunnel import Tunnel

colour1 = (102, 0, 255)      # purple
colour2 = (0, 255, 255)      # cyan
colour3 = (255, 255, 255)    # white

# system settings
inverse = True      # if True, start at the back of the tunnel
frameDelay = 0.01   # delay between frames - controls animation speed (increase to slow down)

left = [ 0 ] * Tunnel.SIDE_MATRIX_SIZE[0]
right = [ 0 ] * Tunnel.SIDE_MATRIX_SIZE[0]

offset = 0
increment = 0
phases = 8*math.pi/Tunnel.LEDS_PER_CHANNEL

flux = 1.0
fluxMax = 2.0
fluxMin = 0.0
fluxIncrement = 1/16.0

frames = 0
while True:
    pixels = [ (0,0,0) ] * Tunnel.LED_COUNT
    for i in range(Tunnel.SIDE_MATRIX_SIZE[0]):
        heightL = int(Tunnel.SIDE_MATRIX_SIZE[1]/2.0 * ((1 + flux * math.cos(phases * i + offset)) / 2.0 + 0.0))
        heightR = int(Tunnel.SIDE_MATRIX_SIZE[1]/2.0 * ((1 + flux * math.sin(phases * i + offset)) / 2.0 + 0.0))
        for j in range(Tunnel.SIDE_MATRIX_SIZE[1]):
            indexL = Tunnel.get_pixel_index_by_side(Tunnel.LEFT_SIDE, i, j)
            indexR = Tunnel.get_pixel_index_by_side(Tunnel.RIGHT_SIDE, i, j)

            debug = (frames == 0 and (i == 0 or i == Tunnel.SIDE_MATRIX_SIZE[0]-1))

            if (indexL >= 0 and indexL < Tunnel.LED_COUNT):
                if (j < heightL):
                    pixels[indexL] = colour2
                elif (j == heightL):
                    pixels[indexL] = colour3
                else:
                    pixels[indexL] = colour1
            elif debug:
                print(" LEFT: [{},{}] @ {}".format(i, j, indexL))
            
            if (indexR >= 0 and indexR < Tunnel.LED_COUNT):
                if (j < heightR):
                    pixels[indexR] = colour2
                elif (j == heightR):
                    pixels[indexR] = colour3
                else:
                    pixels[indexR] = colour1
            elif debug:
                print("RIGHT: [{},{}] @ {}".format(i, j, indexR))


    offset += increment
    if (offset >= Tunnel.SIDE_MATRIX_SIZE[1]):
        offset = 0

    flux += fluxIncrement
    if (flux > fluxMax or flux < fluxMin):
        fluxIncrement *= -1.0

    frames += 1
    Tunnel.Client.put_pixels(pixels)
    time.sleep(frameDelay)