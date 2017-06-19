var SIM = (function(){

  // Public members
  var engine = {
    activate: function(config){
      console.log('LED SIMULATOR ACTIVATING...');
      this.config = config || {};
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
    this.config = config || {};
    UI.init(config.UI);
    Socket.init(config.Socket);
    World.init(config.World);
    LEDs.init(config.LEDs);
  };

  var Socket = {
    init: function(config) {
      this.config = config || {};
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
      if (event && event.data) {
        var data = new Uint8Array(event.data);
        if (data.length > 4) {
          var channel = data[0];
          var command = data[1]
          var pixels = data.slice(4);
          LEDs.update(pixels);
        }
      }
    }
  };

  var UI = {
    init: function(config) {
      this.config = config || {};
      this.HUD = $(config.selector || '#HUD');
    },
    setConnectionStatus(status) {
      if (!this.connectionStatus && this.HUD) {
        this.connectionStatus = $('<div class="connection-status"></div>');
        this.connectionStatus.append($('<label>Server:</label>'));
        this.connectionStatus.append($('<span class="value"></span>'));
        this.HUD.append(this.connectionStatus);
      }
      if (this.connectionStatus) {
        var oldStatus = this.connectionStatus.data('status');
        if (status != oldStatus) {
          this.connectionStatus.children('.value').first().html(status);
          if (oldStatus) {
            this.connectionStatus.removeClass('status-'+oldStatus.toLowerCase());
          }
          if(status) {
            this.connectionStatus.addClass('status-'+status.toLowerCase());
          }
          this.connectionStatus.data('status', status || null);
        }
      }
    },
    setLEDCount(ledCount){
      if (!this.ledCount && this.HUD) {
        this.ledCount = $('<div class="led-count"></div>');
        this.ledCount.append($('<label>LED Count:</label>'));
        this.ledCount.append($('<span class="value"></span>'));
        this.HUD.append(this.ledCount);
      }
      if (this.ledCount) {
        this.ledCount.children('.value').first().html(ledCount);
      }
    }
  };

  var World = {
    init: function(config) {
      this.config = config || {};
      console.log('Initializing simulation world...');
      // initialize the simulation environment
      this.scene = new THREE.Scene();
      this.renderer = new THREE.WebGLRenderer();
      this.renderer.setSize(this.config.viewport.width, this.config.viewport.height);
      $(config.selector).append(this.renderer.domElement);
      this.initMeshes(config.meshes);
      this.initCameras(config.cameras);
      this.initLights(config.lights);
      console.log('Simulation world initialized!');
      this.animate();
    },
    initMeshes: function(config) {
      config = config || {};
      this.meshes = {};
      this.textures = {};

      var ground = new THREE.CubeGeometry(config.ground.width, config.ground.height, config.ground.depth);
      this.textures.ground = new THREE.MeshBasicMaterial( { color: 0x009900 } );
      this.meshes.ground = new THREE.Mesh(ground, this.textures.ground);
      this.scene.add(this.meshes.ground);

      var post = new THREE.CubeGeometry(4, config.tent.height, 4);
      this.textures.post = new THREE.MeshBasicMaterial( { color: 0x333333 } );
      this.meshes.posts = [];
      for (var i=0; i < 4; i++) {
        this.meshes.posts.push(new THREE.Mesh(post, this.textures.post));
        this.scene.add(this.meshes.posts[i]);
        this.meshes.posts[i].position.y = config.tent.height/2.0;
      }
      // front-left
      this.meshes.posts[0].position.x = -config.tent.width/2.0;
      this.meshes.posts[0].position.z = -config.tent.depth/2.0;
      // back-left
      this.meshes.posts[1].position.x = -config.tent.width/2.0;
      this.meshes.posts[1].position.z = config.tent.depth/2.0;
      // back-right
      this.meshes.posts[2].position.x = config.tent.width/2.0;
      this.meshes.posts[2].position.z = config.tent.depth/2.0;
      // front-right
      this.meshes.posts[3].position.x = config.tent.width/2.0;
      this.meshes.posts[3].position.z = -config.tent.depth/2.0;
    },
    initCameras: function(config) {
      config = config || {};
      this.cameras = {};
      this.activeCamera = '';
      if (config.perspective) {
        this.initPerspectiveCamera(config.perspective);
        this.activeCamera = 'perspective';
      }
      if (!this.activeCamera) {
        throw 'No camera selected!';
      }
    },
    initPerspectiveCamera: function(config) {
      config = config || {};
      config.aspect = config.aspect || (this.config.viewport.width/this.config.viewport.height);

      var perspCamera = new THREE.PerspectiveCamera(config.FOV, config.aspect, config.near, config.far); 
      perspCamera.position.x = config.position.x;
      perspCamera.position.y = config.position.y;
      perspCamera.position.z = config.position.z;
      if (config.focus) {
        perspCamera.lookAt(new THREE.Vector3(config.focus.x, config.focus.y, config.focus.z));
      }
      this.cameras.perspective = perspCamera;
    },
    initLights: function(config) {
      config = config || {};

      this.lights = {};

      var hemLight = new THREE.HemisphereLight(0xFFFFFF, 0xFFFFFF, 1.0);
      this.lights.hemisphere = hemLight;
      this.scene.add(this.lights.hemisphere);
    },
    animate: function() {
      requestAnimationFrame(World.animate);
      World.render();
    },
    render: function() {
      if (this.scene && this.activeCamera && this.cameras[this.activeCamera]) {
        this.renderer.render(this.scene, this.cameras[this.activeCamera]);
      }
    }
  };

  var LEDs = {
    init: function(config) {
      this.config = config || {};
      console.log('Loading LED layout...');
      var self = this;
      this.ledGeometry = new THREE.CubeGeometry( config.mesh.width, config.mesh.height, config.mesh.depth);
      this.ledTexture = new THREE.MeshPhongMaterial( { color: 0xFFFFFF, specular: 0xFFFFFF, shininess: 20 } );

      if (typeof config.layout == 'string') {
        if (config.layout.substr(config.layout.length - 5) == '.json') {
          // load the layout as a json array
          $.getJSON(config.layout)
          .done(function(data) {
            console.log('LED Layout loaded!');
            self.setLayout(data);
          })
          .fail(function(error) {
            console.error('LED Layout could not be loaded:', error.statusText);
          });
        }
        else if (config.layout.substr(config.layout.length - 3) == '.js') {
          // use $.ajax instead of $.getScript so it doesn't affect global scope
          $.ajax(config.layout, { dataType: 'text' })
          .done(function(data) {
            // stash the console.log function
            var consoleLog = console.log;
            // override it with a do-nothing function (silence!)
            console.log = function(){};
            // evaluate the script
            eval(data)
            // restore the console.log
            console.log = consoleLog;

            console.log('LED Layout loaded!');
            // setLayout with whatever variable script set it into
            self.setLayout(eval(config.layoutVar || 'model'));
          })
          .fail(function(error) {
            console.error('LED Layout could not be loaded:', error.statusText);
          });
        }
      }
      else if (Array.isArray(config.layout)) {
        self.setLayout(config.layout);
      }
    },
    setLayout: function(pixels) {
      console.log('Initializing Virtual LEDs...');
      this.pixels = [];
      if (pixels) {
        // pixelOrder defines the order the layout defines array points in
        var pixelOrder = this.config.order || ['x', 'y', 'z'];
        for (var i=0; i < pixels.length; i++) {
          var rawPixel = pixels[i];
          var pixel = {
            point: {
              x: 0,
              y: 0,
              z: 0
            },
            color: {
              r: 0.0,
              g: 0.0,
              b: 0.0
            },
            mesh: null,
            texture: null,
            setColor: function(r, g, b) {
              this.color.r = r;
              this.color.g = g;
              this.color.b = b;
              if (this.texture) {
                this.texture.color.r = this.color.r;
                this.texture.color.g = this.color.g;
                this.texture.color.b = this.color.b;
              }
            }
          };
          if (typeof rawPixel == 'object' && Array.isArray(rawPixel.point)) {
            for (var j=0; j < pixelOrder.length && j < rawPixel.point.length; j++) {
              // pixelOrder[j] is the axis that rawPixel.point[j] represents
              pixel.point[pixelOrder[j]] = rawPixel.point[j];
            }
          }
          this.drawPixel(pixel, i);
          this.pixels.push(pixel);
        }
      }
      UI.setLEDCount(this.pixels.length);
      console.log('Virtual LEDs initialized!');
    },
    drawPixel: function(pixel, index) {
      pixel.texture = this.ledTexture.clone();
      pixel.mesh = new THREE.Mesh(this.ledGeometry, pixel.texture);

      pixel.texture.color.r = pixel.color.r;
      pixel.texture.color.g = pixel.color.g;
      pixel.texture.color.b = pixel.color.b;

      pixel.mesh.position.x = this.config.anchor.x + (pixel.point.x * this.config.scale.x);
      pixel.mesh.position.y = this.config.anchor.y + (pixel.point.y * this.config.scale.y);
      pixel.mesh.position.z = this.config.anchor.z + (pixel.point.z * this.config.scale.z);

      World.scene.add(pixel.mesh);
    },
    update: function(pixels) {
      // pixels should be a one-dimensional array of RGB values
      if (pixels && this.pixels && pixels.length && this.pixels.length) {
        var color;
        var index = 0;
        for (var i=0; i < pixels.length; i++) {
          if (!color) {
            color = { R: pixels[i]/255 };
          }
          else if (!color.hasOwnProperty('G')) {
            color.G = pixels[i]/255;
          }
          else if (!color.hasOwnProperty('B')) {
            color.B = pixels[i]/255;
          }
          if (color.hasOwnProperty('B')) {
            // pixel is complete
            if (index < this.pixels.length) {
              this.pixels[index++].setColor(color.R, color.G, color.B);
            }
            color = undefined;
          }
        }
      }
    }
  };

  return engine;
})();
