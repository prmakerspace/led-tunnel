var SIM = (function(){

  // Public members
  var engine = {
    activate: function(config){
      console.log('LED SIMULATOR ACTIVATING...');
      config = config || {};
      if (Detector.webgl) {
        init(config);
        console.log('LED SIMULATOR ACTIVATED!');
      } else {
        console.error('WebGL detection Failed!');
        console.log('LED SIMULATOR ACTIVATION FAILED!');
        var warning = Detector.getWebGLErrorMessage();
        $(config.WebGL.selector).append(warning);
      }
    }
  };

  // Private members
  function init(config) {
    config = config || {};
    UI.init(config.UI);
    Socket.init(config.Socket);
    World.init(config.World);
    LEDs.init(config.LEDs);
  };

  var Socket = {
    init: function(config) {
      config = config || {};
      this.isConnected = false;
      console.log('Connecting to fcserver...');
      // Connect to a Fadecandy server running on the same computer, on a port configured to relay
      this.connection = new WebSocket('ws://'+config.host+':'+config.port);

      // Options needed for relaying
      // setting binaryType is required to properly receive the OPC messages
      this.connection.binaryType = 'arraybuffer';

      // Socket event handlers
      this.connection.onopen = this.connected;
      this.connection.onclose = this.disconnected;
      this.connection.onmessage = this.packetReceived;
    },
    connected: function(event) {
      this.isConnected = true;
      UI.setConnectionStatus('Connected');
      console.log('Connected to fcserver!');
    },
    disconnected: function(event) {
      this.isConnected = false;
      UI.setConnectionStatus('Disconnected');
      console.log('Disconnected from fcserver!');
    },
    packetReceived: function(event) {
      // @TODO: parse event and call LEDs.update(...);
      console.log('Packet received =>', event);
    }
  };

  var UI = {
    init: function(config) {
      config = config || {};
      this.HUD = $(config.selector || '#HUD');
    },
    setConnectionStatus(status) {
      if (!this.connectionStatus && this.HUD) {
        this.connectionStatus = $('<div class="connection-status"></div>');
        this.HUD.append(this.connectionStatus);
      }
      if (this.connectionStatus) {
        var oldStatus = this.connectionStatus.data('status');
        if (status != oldStatus) {
          this.connectionStatus.html(status);
          if (oldStatus) {
            this.connectionStatus.removeClass('status-'+oldStatus.toLowerCase());
          }
          if(status) {
            this.connectionStatus.addClass('status-'+status.toLowerCase());
          }
          this.connectionStatus.data('status', status || null);
        }
      }
    }
  };

  var World = {
    init: function(config) {
      config = config || {};
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
    init: function(config) {
      config = config || {};
      console.log('Initializing Virtual LEDs...');
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
