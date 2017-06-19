/*
 * Model creation script for a 48x64 grid arranged into a tunnel.
 *
 * 2017 Pat Long (plong0)
 * This file is released into the public domain.
 */

var model = [];

var scale = 12;
var radiusH = 4*scale;
var radiusV = 6*scale;
var numChannels = 48;
var ledsPerChannel = 64;
var spacing = 7*scale/ledsPerChannel;
var angle1 = 0;
var angle2 = 180;

for (var i=0; i < numChannels; i++) {
  var angle = angle1 + i*((angle2-angle1)/(numChannels-1)) * (Math.PI / 180);
  var x = radiusH * Math.cos(angle);
  var y = radiusV * Math.sin(angle);
  for (var j=0; j < ledsPerChannel; j++) {
    var z = j * spacing;
    model.push({
      point: [x, y, z]
    });
  }
}
