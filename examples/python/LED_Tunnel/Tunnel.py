"""PRMS LED Tunnel core functions"""
from libs import opc

# FadeCandy Server Settings
FADECANDY_SERVER_HOST = 'localhost'
FADECANDY_SERVER_PORT = 7890

# Tunnel Definition
CHANNEL_COUNT = 48
LEDS_PER_CHANNEL = 64
LED_COUNT = CHANNEL_COUNT * LEDS_PER_CHANNEL

# Settings when working with sides (aka "walls")
LEFT_SIDE = 0
RIGHT_SIDE = 1

SIDE_MATRIX_SIZE = (int(LEDS_PER_CHANNEL), int(CHANNEL_COUNT/2))

# initialize the OPC Client
Client = opc.Client(FADECANDY_SERVER_HOST+":"+str(FADECANDY_SERVER_PORT))

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

def get_pixel_index_by_side(side, depth, height, invert=False):    
    if side == LEFT_SIDE:
        #left side
        base = height
    elif side == RIGHT_SIDE:
        #right side
        base = (2 * SIDE_MATRIX_SIZE[1] - height - 1)

    if base != None:
        if invert:
            return (base + 1) * SIDE_MATRIX_SIZE[0] - 1 - depth
        return base * SIDE_MATRIX_SIZE[0] + depth

    return -1