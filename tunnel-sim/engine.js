var SIM = (function(){

  // Public members
  var engine = {
    activate: function(config){
      console.log('LED SIMULATOR ACTIVATING...');
      config = config || {};
      if (Detector.webgl) {
        init();
        console.log('LED SIMULATOR ACTIVATED!');
      } else {
        console.error('WebGL detection Failed!');
        console.log('LED SIMULATOR ACTIVATION FAILED!');
        var warning = Detector.getWebGLErrorMessage();
        document.getElementById('container').appendChild(warning);
      }
    }
  };

  // Private members
  function init() {
    socket.init();
    world.init();
    LEDs.init();
  };

  var socket = {
    init: function() {
      console.log('Connecting to fcserver...');
      // @TODO: connect to the fcserver
      // @TODO: when OPC message is received, call LEDs.update(...);
      console.log('Connected to fcserver!');
    }
  };

  var world = {
    init: function() {
      console.log('Initializing simulation world...');
      // @TODO: initialize the simulation environment
      console.log('Simulation world initialized!');
      this.animate();
    },
    animate: function() {
      // @TODO: nothing really, this is the main animation loop, but most (all?) of our updates come from the socket
    }
  };

  var LEDs = {
    init: function() {
      console.log('Initializing Virutal LEDs...');
      // @TODO: initialize LED meshes, each with an individual texture/material
      console.log('Virtual LEDs initialized!');
    },
    update: function(pixels) {
      // pixels should be a one-dimensional array of RGB values
      // @TODO: update the colours of the LEDs using the pixel array
    }
  };

  return engine;
})();
