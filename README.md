# Powell River Makerspace LED Tunnel

The PR Makerspace LED Tunnel will use multiple [Fadecandy](https://learn.adafruit.com/led-art-with-fadecandy/intro) controller boards and a lot of addressable RGB LEDs to create a beautiful installation at the [Powell River Blackberry Festival 2017](http://www.powellriver.info/calendar/index.php?option=com_k2&view=item&id=300:blackberry-festival&Itemid=676).

**Sponsored by [Westview Agencies](http://www.westviewagencies.ca/) / [First Credit Union](https://www.firstcu.ca/) and Powell River Technology Co-op**

**Built by [Powell River Makerspace](http://prmakerspace.com)**

## Getting Started

### Setup

To install the dev environment, run the commands in terminal:

```
git clone https://github.com/prmakerspace/led-tunnel.git &&
cd led-tunnel &&
git clone https://github.com/plong0/fadecandy.git -b relay-server &&
cd fadecandy/server/ &&
make submodules &&
make &&
cd ../../tunnel-sim/ &&
bower install &&
cd ..
```

### Running

#### 1. Start the fadecandy server

From led-tunnel directory, run:

```
cd fadecandy/server/ &&
./fcserver config.json
```

#### 2. Run the web-based simular

To start a simple python webserver, open a terminal to the led-tunnel directory and run:

```
cd tunnel-sim &&
python -m SimpleHTTPServer 8000
```

In a browser, open: http://localhost:8000

The simulator connects to the *fcserver* and acts only as an output - it does not have any control over the lights!

You can use the browser's built-in developer tools / javascript console to see log messages from the simulator.

*You can use any webserver, the python one is really quick and simple.  Simply opening the index.html in the browser will not work because the javascript loads certain resources using ajax requests.*


#### 3. Code some cool effects!

Browse through the **[fadecandy/examples](https://github.com/plong0/fadecandy/tree/master/examples)** folder for examples in many different languages.  Choose whatever language you are interested in and start coding!

The tunnel uses a 48x64 matrix of LEDs.

Fadecandy (and this simulator!) use the [Open Pixel Control](http://openpixelcontrol.org/) protocol.  The fadecandy examples illustrate code that send packets in the OPC format.
