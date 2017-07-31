#!/usr/bin/env python3
"""Audio Levels reads input from microphone and displays equalizer

Dependencies:
pyaudio
numpy

See platform-specific installation instructions at: http://people.csail.mit.edu/hubert/pyaudio/

If receiving error pyaudio is not found, try with:
pip3 install pyaudio

Audio signal processing examples:
http://www.swharden.com/wp/2013-05-09-realtime-fft-audio-visualization-with-python/
http://www.swharden.com/wp/2016-07-19-realtime-audio-visualization-in-python/
https://gist.github.com/hyperconcerto/950bbb9d9d4014d893e5

Multi-channel pyaudio processing:
https://stackoverflow.com/questions/22636499/convert-multi-channel-pyaudio-into-numpy-array

Try running with optional config name.
ex. ./audio-levels.py ocean
"""
__author__ = 'plong0 <plong00@gmail.com>'

import sys
import time
import signal
import pyaudio
import numpy as np
from pprint import pprint
from LED_Tunnel import Tunnel

MODE_WAVE = 0
MODE_FFT = 1

ACTIVE_MODE = MODE_FFT

LISTEN_FPS = 15
FORMAT = pyaudio.paInt16
CHANNELS = 1 # only 1 channel supported for microphone
RATE = 44100
#RATE = 16000
CHUNK = int(RATE / LISTEN_FPS)

FFT_START = 78
FFT_BANDS = 48
FFT_THRESHOLD = 0
FFT_NORM = "ortho"
FFT_NORM = None
FFT_LEDS_PER_BAND = 2
FFT_RENDER_BANDS = Tunnel.LEDS_PER_CHANNEL / FFT_LEDS_PER_BAND

WAVE_START = 0
WAVE_LENGTH = 64
WAVE_LEDS_PER_BAND = 1
WAVE_RENDER_BANDS = Tunnel.LEDS_PER_CHANNEL / WAVE_LEDS_PER_BAND

colours = [(0, 255, 255), (255, 255, 255), (64, 0, 128)]
frameDelay = 0.01

p = pyaudio.PyAudio()

def start_microphone():
    global p, inStream, FORMAT, CHANNELS, RATE, CHUNK
    print("Starting microphone input...")
    inStream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

def stop_microphone():
    global p, inStream
    print("Stopping microphone input...")
    inStream.stop_stream()
    inStream.close()
    p.terminate()

def read_microphone():
    global inStream, CHUNK
    data = inStream.read(CHUNK)
    data = np.fromstring(data, np.int16)
    return data

def condense(data, band_count):
    band_width = int(data.size / band_count)

    if data.size%band_width != 0:
        data = np.pad(data.astype(float), (0, band_width - data.size%band_width), mode='constant', constant_values=np.NaN)
    else:
        data = data.astype(float)

    data = np.nanmean(data.reshape(-1, band_width), axis=1)

    return data


def parse_wave(data):
    wave_x = range(WAVE_START, WAVE_START+WAVE_LENGTH)
    wave_y = data[WAVE_START : WAVE_START+WAVE_LENGTH]
    return (wave_x, wave_y)

def parse_fft(data):
    global FFT_START, FFT_BANDS
    spec_x = np.fft.fftfreq(FFT_BANDS, d = 1.0/RATE)
    y = np.fft.fft(data[FFT_START : FFT_START+FFT_BANDS], norm=FFT_NORM)
    #spec_y = y
    #spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
    spec_y = [np.sqrt(c.real ** 2) for c in y]
    return (spec_x, spec_y)

def render_levels_debug(levels, threshold=0):
    #peak = np.average(np.abs(levels[1]))*2
    peak = np.amax(np.abs(levels[1]))
    print("PEAK of {} @ {}".format(len(levels[1]), peak))
    for i in range(0, len(levels[1])):
        norm = np.abs(levels[1][i])/peak if peak > threshold else 0
        bars = "#"*int(50*norm)
        print("%02d %03f %s"%(i,norm,bars))
    print("")

def get_normals(levels, threshold=0, abs_normals=True):
    normals = []
    #peak = np.average(np.abs(levels[1]))*2
    peak = np.amax(np.abs(levels[1]))
    for i in range(0, len(levels[1])):
        value = np.abs(levels[1][i]) if abs_normals else levels[1][i]
        norm = value/peak if peak > threshold else 0
        normals.append(norm)

    return (normals, peak)

def run():
    global colours
    start_microphone()
    frameCount = 0
    while True:
        data = read_microphone()

        if ACTIVE_MODE == MODE_FFT:
            levels = parse_fft(data)
            render_threshold = FFT_THRESHOLD
            render_bands = FFT_RENDER_BANDS
            abs_normals = True
        else:
            levels = parse_wave(data)
            render_threshold = 0
            render_bands = WAVE_RENDER_BANDS
            abs_normals = False

        levels = (condense(np.array(levels[0]), render_bands), condense(np.array(levels[1]), render_bands))

        normals = get_normals(levels, render_threshold, abs_normals)

        #render_levels_debug(levels, render_threshold)

        pixels = [ (0,0,0) ] * Tunnel.LED_COUNT
        for side in range(0, 2):
            for depth in range(0, Tunnel.SIDE_MATRIX_SIZE[0]):
                channel = int(depth / FFT_LEDS_PER_BAND)
                if abs_normals:
                    channel_height = int(normals[0][channel] * Tunnel.SIDE_MATRIX_SIZE[1])
                else:
                    channel_height = int((Tunnel.SIDE_MATRIX_SIZE[1]/2.0) * (1. + normals[0][channel]))

                for height in range(0, Tunnel.SIDE_MATRIX_SIZE[1]):
                    index = Tunnel.get_pixel_index_by_side(side, depth, height)

                    if abs_normals:
                        if height < channel_height:
                            pixels[index] = colours[0]
                        elif height == channel_height:
                            pixels[index] = colours[1]
                        else:
                            pixels[index] = colours[2]
                    else:
                        if height >= channel_height-1 and height <= channel_height+1:
                            pixels[index] = colours[1]
                        else:
                            pixels[index] = colours[2]



        Tunnel.Client.put_pixels(pixels)
        frameCount += 1
        #time.sleep(frameDelay)


def terminate(signal, frame):
    stop_microphone()
    sys.exit(0)

signal.signal(signal.SIGINT, terminate)
run()
