var map;
var markers = [];
var bounds = new google.maps.LatLngBounds();
var infoWindow = null;


google.maps.event.addDomListener(window, 'load', initialize);