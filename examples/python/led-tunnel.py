#!/usr/bin/env python3
"""This runs the various patterns for the LED Tunnel.

Example led-tunnel.json configuration:

{
  "default": {
    "time": 60
  },
  "patterns": [
    {"cmd": "./channel-runner.py pink-yellow"},
    {"cmd": "./wall-drops.py", "time": 30},
  ]
}
"""
__author__ = 'plong0 <plong00@gmail.com>'

import json
import subprocess
from pprint import pprint

with open('led-tunnel.json') as data_file:
    data = json.load(data_file)

while True:
    for pattern in data["patterns"]:
        if "cmd" in pattern:
            time = pattern["time"] if "time" in pattern else data['default']['time']
            print("RUNNING {} FOR {} seconds...".format(pattern['cmd'], time))
            try:
                proc = subprocess.Popen(pattern['cmd'].split())
                proc.communicate(timeout=int(time))
            except subprocess.TimeoutExpired as Timeout:
                proc.kill()
                print("COMPLETED {} AFTER {} seconds!".format(pattern['cmd'], Timeout.timeout))
                pass
