var transform = ol.proj.getTransform('EPSG:3857', 'EPSG:4326');

var map = new ol.Map({
  // controls: [],
  // interactions : ol.interaction.defaults({
  //   doubleClickZoom: false,
  //   dragZoom: false,
  //   keyboardZoom: false,
  //   mouseWheelZoom: false,
  //   pinchZoom: false,
  // }),
  target: 'map',
  renderer: 'canvas', // Force the renderer to be used
  layers: [
    new ol.layer.Tile({
      source: new ol.source.BingMaps({
        key: 'AnGHr16zmRWug0WA8mJKrMg5g6W4GejzGPBdP-wQ4Gqqw-yHNqsHmYPYh1VUOR1q',
        imagerySet: 'AerialWithLabels',
        // imagerySet: 'Road',
      })
    })
  ],
  view: new ol.View({
    center: ol.proj.transform([-122.3020636,37.8732388], 'EPSG:4326', 'EPSG:3857'),
    zoom: 18
  })
});

// Create an image layer
var FUDGE = 0.0005;
var OFFSETX = 0.0001;
var OFFSETY = -0.0002;

function addImage(lat, lon, src) {
  var imageLayer = new ol.layer.Image({
    // opacity: 0.75,
    source: new ol.source.ImageStatic({
      attributions: [
      ],
      url: src,
      // imageSize: [691, 541],
      projection: map.getView().getProjection(),
      imageExtent: ol.extent.applyTransform([lon-OFFSETX, lat-OFFSETY, lon-OFFSETX - FUDGE, lat-OFFSETY - FUDGE], ol.proj.getTransform("EPSG:4326", "EPSG:3857"))
    })
  });

  map.addLayer(imageLayer);
}

var overlayContent = document.createElement('div');
overlayContent.style.position = 'relative';
overlayContent.style.height = '80px';
overlayContent.style.width = '80px';
overlayContent.innerHTML = '' +
'<div style="background: rgba(0, 220, 255, 1); opacity: 0.2; width: 100%; height: 100%; border-radius: 50%; position: absolute; top: 0; left: 0; box-sizing: border-box; border: 2px solid rgb(0, 100, 150);"></div>' +
'<div style="width: 100%; height: 100%; position: absolute; top: 0; left: 0; -webkit-transform: rotate(45deg);" class="heading"><div style="width: 0; height: 0; border-width: 10px; border-style: solid; border-color: red transparent transparent red; position: absolute; top: 0; left: 0;"></div></div>' +
'<img src="static/images/solo.png" height="50" style="z-index: 100; position: absolute; top: 50%; left: 50%; margin-left: -43px; margin-top: -20px;">';

var overlay = new ol.Overlay({
    element: overlayContent,
    position: ol.proj.transform([0, 0], 'EPSG:4326', 'EPSG:3857'),
    positioning: 'center-center'
});

// var iconFeature = new ol.Overlay({
//   element = 
//   geometry: new ol.geom.Point(ol.proj.transform([0, 0], 'EPSG:4326', 'EPSG:3857')),
//   name: 'Solo',
// });

// iconFeature.setStyle(new ol.style.Style({
//   image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
//     anchor: [0.5, 46],
//     anchorXUnits: 'fraction',
//     anchorYUnits: 'pixels',
//     opacity: 1,
//     src: 'static/images/solo.png',
//     scale: .15,
//   }))
// }));

// var vectorLayer = new ol.layer.Vector({
//   source: new ol.source.Vector({
//     features: [ iconFeature ]
//   }),
// });

// map.addLayer(vectorLayer)

map.addOverlay(overlay);

// map.on('dblclick', function(evt) {
//   var coord = transform(evt.coordinate);
//   $.ajax({
//     method: 'PUT',
//     url: '/api/location',
//     contentType : 'application/json',
//     data: JSON.stringify({ lat: coord[1], lon: coord[0] }),
//   })
//   .done(function( msg ) {
//     console.log('sent data')
//   });
// });

$('#header-arm').on('click', function () {
  $.ajax({
    method: 'PUT',
    url: '/api/arm',
    contentType : 'application/json',
    data: JSON.stringify({ arm: true }),
  })
  .done(function( msg ) {
    console.log('sent arming message')
  });
})

$('#header-mode-loiter').on('click', function () {
  $.ajax({
    method: 'PUT',
    url: '/api/mode',
    contentType : 'application/json',
    data: JSON.stringify({ mode: 'LOITER' }),
  })
  .done(function( msg ) {
    console.log('sent mode change')
  });
})

$('#header-mode-stabilize').on('click', function () {
  $.ajax({
    method: 'PUT',
    url: '/api/mode',
    contentType : 'application/json',
    data: JSON.stringify({ mode: 'STABILIZE' }),
  })
  .done(function( msg ) {
    console.log('sent mode change')
  });
})

var globmsg = null;

var source = new EventSource('/api/sse/state');
source.onmessage = function (event) {
  var msg = JSON.parse(event.data);
  if (!globmsg) {
    console.log('FIRST', msg);
    $('body').removeClass('disabled')
    map.getView().setCenter(ol.proj.transform([msg.lon, msg.lat], 'EPSG:4326', 'EPSG:3857'));
  }
  globmsg = msg;

  $('#header-state').html('<b>Armed:</b> ' + msg.armed + '<br><b>Mode:</b> ' + msg.mode + '<br><b>Altitude:</b> ' + msg.alt.toFixed(2))
  $('#header-arm').prop('disabled', msg.armed);
  
  overlay.setPosition(ol.proj.transform([msg.lon, msg.lat], 'EPSG:4326', 'EPSG:3857'));
  $(overlay.getElement()).find('.heading').css('-webkit-transform', 'rotate(' + ((msg.heading) + 45) + 'deg)')
};

$('#header-center').on('click', function () {
  map.getView().setCenter(ol.proj.transform([globmsg.lon, globmsg.lat], 'EPSG:4326', 'EPSG:3857'));
})
