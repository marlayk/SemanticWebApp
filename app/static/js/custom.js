var player;
var artist;



function getartists(){
	// Do a GET request on the '/show' URL, with the data payload 'Hello World'.
	var message = $('#artist').val();
	$.get('/artists' , data = {'artist' : message}, function(data){
		result = "";
		var artist;

		artistlist = data['artist-list'];
		result = "";
		for(var i=0; i<artistlist.length;i++){
			text = "<p><strong><a class='closedropdown' style='text-decoration: none; cursor: pointer' onclick = 'getSongsFromLastFm(\"" + data['artist-list'][i]['id'] + "\",\"" + data['artist-list'][i]['name'] + "\")'>" + data['artist-list'][i]['name'] + "</a></strong><button onclick='likeArtist(\""+data['artist-list'][i]['id']+"\",\""+data['artist-list'][i]['name'] +"\")' class='btn-xs pull-right btn btn-primary' >LIKE</button><p>";
			result = result + text;
		}

		$('#artist-list').html(result);
	});

}

function likeArtist(id,name){
	$.get('/like' , data = {'id' : id, 'name': name, 'likeType' : 'Artist'})
}


function likeSong(name){
	$.get('/like' , data = {'id' : 'To_Be_fixed','name' : name, 'likeType' : 'Song'})
}


function getSongsFromLastFm(id , name){

	$.get('/artistinfo', data={'id':id , 'name':name },function(data){
		$('#artistinfo').html(data);
	})
	document.getElementById("artist").value =name;
	artistid = id;
	$.get('/songs' , data = {'id' : artistid}, function(data){
		$('#song-list').html(data);
	});

}

function onYouTubeIframeAPIReady() {
	player = new YT.Player('player', {
      	height: '200',
        width: '450',

    });
}

function getvideo(name){
	$.ajax({
    url: "http://gdata.youtube.com/feeds/api/videos?q=" + escape(name) + "&alt=json&max-results=1&format=5",
    dataType: "jsonp",
    success: function (data) {
    		var id = data.feed.entry[0].id.$t.split('/').reverse()[0];
    		player.loadVideoById(id, 0, "small")
    	}
	});
}

// -----------------------------------------------------------------

function initialize(){
	var lat, lng;
	$.get('/getLatLng' , function(data){
 			lat = JSON.parse(data)["lat"];
 			lng = JSON.parse(data)["lng"];
 			mapinitialize(lat,lng);
	});
	
}


function mapinitialize(lat,lng) {
	var mapOptions = {
		center: new google.maps.LatLng(lat, lng),
        zoom: 10,
        maxZoom: 10,
        minZoom: 2,
        mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById('map-canvas'),
        	mapOptions);
}
   
function setAllMap(map) {
	for (var i = 0; i < markers.length; i++) {
   		markers[i].setMap(map);
    }
}
// Removes the markers from the map, but keeps them in the array.
function clearMarkers() {
  	setAllMap(null);
} 
      
function deleteMarkers() {
  	clearMarkers();
 	markers = [];
}

function addInfoWindow(marker, message) {
	var info = message;
	google.maps.event.addListener(marker, 'mouseover', function () {
    if (infoWindow){
    	infoWindow.close();
    }
                infoWindow = new google.maps.InfoWindow();
                infoWindow.setContent("<div class='infowindow'>"+info+"</div>");
                infoWindow.open(map, marker);
            });
}

function addMarker(latitude,longitude,i,color){
	var marker = new google.maps.Marker({
    	position: new google.maps.LatLng (latitude, longitude),
    	map: map,
    	title: 'test',
    });
    switch(color){
	case "green":
    	marker.setIcon('/static/img/green-dot.png');
    	break;
    case "red":
    	marker.setIcon('/static/img/red-dot.png');
    	break;
    }	

return marker;
}

function submitted(artist,mbid){

	var lld_eventful_url = 'http://api.eventful.com/json/events/search?app_key=gKwVVMz88t773B4Q&keywords='+artist+'&date=Future&callback=?';
	var lld_lastf_url = 'http://ws.audioscrobbler.com/2.0/?method=artist.getevents&artist='+artist+'&api_key=4bea9a7cfe15b09d2ada827592605ee0&format=json';
	var data = {'q': artist , 'limit': 100}
	var ul = $('<ul></ul>');
		ul.addClass('list-group');
	deleteMarkers();
	$.getJSON(lld_eventful_url, data=data, function(json){
		
	if (json.total_items == "0"){
			addElement("no eventful events found...",ul,"event",mbid);
		}  else {

		for (var i in json.events.event) {
			var r = json.events.event[i];
			
			var message =  'title: '+ r.title + '\n' + 'start time: ' + r.start_time + '\n' + 'city: ' + r.city_name ;

			$.get('/addEvent', data = {'city':r.city_name, 'latitude': r.latitude , 'longitude':r.longitude , 'start_time': r.start_time ,'description': r.description, 'source': "eventful" , 'artist': artist, 'mbid': mbid}, function(data){

	});

			marker = addMarker (r.latitude, r.longitude,i,"green");
			addInfoWindow(marker, message);
    		markers.push(marker);
    		bounds.extend(marker.position);
			addElement(r.city_name,ul,"event",mbid);
			//console.log(mbid);
			
		}
	}
		
	});


$.getJSON(lld_lastf_url, data=data, function(json){
			
	if (!json.events.hasOwnProperty('event')){
		addElement("no lastfm events found...",ul,"event",mbid);
	}else{
		for (var i in json.events.event) {
			var r = json.events.event[i];
			var message = 'title: '+ r.title + '\n' + 'start time: ' + r.startDate + '\n' + 'city: ' + r.venue.location.city ;
			evLat = r['venue']['location']['geo:point']['geo:lat'];
			evLong = r['venue']['location']['geo:point']['geo:long'];
			$.get('/addEvent', data = {'city':r.venue.location.city, 'latitude': evLat , 'longitude':evLong , 'start_time': r.startDate ,'description': r.description, 'source': "lastfm" , 'artist': artist, 'mbid': mbid}, function(data){

			});
			marker = addMarker (evLat,evLong,i,"red");
			addInfoWindow(marker, message);
    		markers.push(marker);
    		bounds.extend(marker.position);
			addElement(r.venue.location.city,ul,"event",mbid);	
		}
	}	
	map.fitBounds(bounds);	
	});
	$('#event_list').html(ul);
}



function addElement(element,ul,type,mbid){
	var li = $('<p></p>');
	if (type=="artist"){
		li.append("<strong><a style='text-decoration: none; cursor: pointer' onclick='submitted(\""+element+"\",\""+mbid+"\")'>"+element+"</strong></a>");
	}
	else if (type=="event"){
		li.append("<strong><a style='text-decoration: none; cursor: pointer' onclick='showDescription(\""+element+"\",\""+mbid+"\")'>"+element+"</a></strong>");
	}
	ul.append(li);
}




function fetchArtist() {
	artist = $('#artist').val();

	$.get('/artists', data = {'artist':artist} , function(data){
		var artistlist = data['artist-list'];
		var ul = $('<ul></ul>');
		ul.addClass('list-group');

		for (var i =0 ; i<artistlist.length;i++){
			ended = data['artist-list'][i]['life-span']['ended'];
			
			if (ended=="false"){
			addElement(data['artist-list'][i]['name'],ul,"artist",data['artist-list'][i]['id']);
			}	
		}
		$('#artist_suggestion').html(ul);
	}
		)
}


function changeLocation(){
	var location = $('#location').val();
	var lat = $('#lat').val();
	var lng = $('#lng').val();
	//console.log(lat);
	$.get('/changeLocation', data = {'location':location, 'lat':lat , 'lng':lng}, function(data){
	});
	initialize();
	$('#loc').html(location);

}



function searchArtists(){

	var loadUrl = 'searchArtists';
    $("#BodyContent").load(loadUrl); 	    
}

function browseEvent(){

	var loadUrl = 'browseEvent';
    $("#BodyContent").load(loadUrl); 	    
}

function demandEvent(){

	var loadUrl = 'demandEvent';
    $("#BodyContent").load(loadUrl); 	    
}



function browseArtists(){
	// Do a GET request on the '/show' URL, with the data payload 'Hello World'.
	var message = $('#artist').val();
	
		$.get('/artists' , data = {'artist' : message}, function(data){
		var artist;

		
		artistlist = data['artist-list'];
		var result = $('<span></span>');
		
		for(var i=0; i<artistlist.length;i++){
			ended = data['artist-list'][i]['life-span']['ended'];
			
			if (ended=="false"){

			name = data['artist-list'][i]['name'];
			mbid = data['artist-list'][i]['id'];
			
			var str = $('<strong></strong>');
			var link = $('<a>' ,{ text: data['artist-list'][i]['name'] });
			link = link.attr("href", 'javascript:requestEvents("'+mbid+'","'+name+'" );');
			link = link.attr("style",'text-decoration: none; cursor: pointer');
			var p = $('<p></p>');
			str.append(link);
			p.append(str);
			result.append(p);
			}

		}
		$('#artist_list').html(result);
	});
}

/*

function browseArtists(){
	// Do a GET request on the '/show' URL, with the data payload 'Hello World'.
	var message = $('#artist').val();
	
		$.get('/artists' , data = {'artist' : message}, function(data){
		result = "";
		var artist;

		var str = $('<strong></strong>');
		artistlist = data['artist-list'];
		var result = $('<span></span>');
		
		for(var i=0; i<artistlist.length;i++){

			name = data['artist-list'][i]['name'];
			mbid = data['artist-list'][i]['id'];
			link = $("<a>" ,{ text: data['artist-list'][i]['name'] }, "</a>");
			link = link.attr("href", 'javascript:createEvent("'+mbid+'","'+name+'" );');
			result.append($('<p>').append( link ));
		}
		$('#artist_list').html(result);
	});
}

*/

function requestEvents(mbid,name){
		
	$.get('/requestEvents' , data = {'mbid' : mbid}, function(data){
		var resu = $('<span></span>');
		var d = $('<div></div>');
		var table = $ ('<table></table>');
		table.attr('class' , 'table');
		var thead = $ ('<thead></thead>');
		var tr = $('<tr></tr>');
		var tb = $("<tbody></tbody>");
		
		var th_loc = $('<th>', {text: "Location"});
		th_loc.attr('style', 'text-align:center');
		var th_n_vot = $('<th>', {text: "Number of Votes"});
		th_n_vot.attr('style', 'text-align:center');
		var th_vot = $('<th>', {text: "Do you want to vote?"});
		th_vot.attr('style', 'text-align:center');


		var head= thead.append(tr.append(th_loc).append(th_n_vot).append(th_vot));

		data = JSON.parse(data);
		if (data[0].hasOwnProperty('location')){
		for(var i=0; i<data.length;i++){

			tr = $("<tr></tr>");

			loc = $("<td>", {text: data[i]['location']['value'] });
			loc.attr('style', 'text-align: center');
			n_votes = $("<td>", {text: data[i]['votes']['value'] });
			n_votes.attr('style', 'text-align: center');
			td=$('<td></td>');
			votes = $("<a>", {text: "Vote" }, "</a>");
			votes.attr("href", 'javascript:vote("'+data[i]['eventid']['value'].substring(15)+'")' );
			votes.attr('style', 'color: "red"')
			td.attr('style', 'text-align: center');
			
			tb.append(tr.append(loc).append(n_votes).append(td.append(votes)));

			
		}
		d.append(table.append(head).append(tb));

	}		

			var add_but = $('<div></div>');
			add_but.attr('style', 'text-align:center');
			but = $('<button>',{text: "CREATE NEW EVENT!"});
			but.attr('class','btn btn-md btn-primary');
			but.attr('onclick','showModal("'+mbid+'","'+name+'" );');

			resu.append(d).append(add_but.append(but));
		$('#event_list').html(resu);

});
}


function create_Event(){
		var mbid = $('#mbid').val();
		var artist = $('#name').val();
	
		$.get('/createEvent' , data = {'mbid' : mbid, 'artist':artist}, function(data){
		console.log(data);
		if (data=="OK") {
			
		$('#succesModal').modal('show');

		}
	});
}

function showModal(mbid,name){
	$('#createEventModal').modal('show'); 
	$('.modal .chosenArtist').html(name);
	$(' #mbid').val(mbid);
	$(' #name').val(name);
	
}

function vote(eventid){
	console.log(eventid);
	$.get('/vote' , data = {'eventid' : eventid}, function(data){
		console.log(data);
});
}



function showDescription(city,mbid) {
	console.log(mbid)
	console.log(city)
	$.get('/showDescription', data = { 'city':city , 'mbid':mbid}, function(data){
		   $('#event_description').html(data);
		   
	});
}

function favouriteArtist(){

	$.get('/favouriteArtist', function(data){
		result = "";
		var fartist;

		data=JSON.parse(data);
		var result = $('<span></span>');
		
		for(var i=0; i<data.length;i++){
			str = $("<strong></strong>")
			r = $("<p>", { text: data[i]['artistname']['value'] }, "</p>");
			str.append(r)
			result.append(str);
		}
		$('#favouriteArtist').html(result);
		   
	});
}



function getmyEvents(){

	$.get('/getmyEvents', function(data){
		result = "";
		var mEvent;

		data=JSON.parse(data);

		var table = $ ('<table></table>');
		table.attr('class' , 'table');
		var thead = $ ('<thead></thead>');
		var tr = $('<tr></tr>');
		var tb = $("<tbody></tbody>");
		
		var th_art = $('<th>', {text: "Artist"});
		th_art.attr('style', 'text-align:center');
		var th_loc = $('<th>', {text: "Location"});
		th_loc.attr('style', 'text-align:center');
		var th_vot = $('<th>', {text: "Votes"});
		th_vot.attr('style', 'text-align:center');

		var head= thead.append(tr.append(th_art).append(th_loc).append(th_vot));


		for(var i=0; i<data.length;i++){
			tr = $("<tr></tr>");

			art = $("<td>", {text: data[i]['artist']['value']});
			art.attr('style', 'text-align:center');
			loc = $("<td>", {text: data[i]['location']['value'] });
			loc.attr('style', 'text-align: center');
			votes = $("<td>", {text:data[i]['votes']['value'] });
			votes.attr('style', 'text-align: center');
			
			tb.append(tr.append(art).append(loc).append(votes));

			
		}
		table.append(head).append(tb);

		$('#myEvents').html(table);
		   
	});

}


function getinterestingEvents(){

	$.get('/getinterestingEvents', function(data){
		result = "";
		var mEvent;

		data=JSON.parse(data);
		console.log(data)

		var table = $ ('<table></table>');
		table.attr('class' , 'table');
		var thead = $ ('<thead></thead>');
		var tr = $('<tr></tr>');
		var tb = $("<tbody></tbody>");
		
		var th_art = $('<th>', {text: "Artist"});
		th_art.attr('style', 'text-align:center');
		var th_loc = $('<th>', {text: "Location"});
		th_loc.attr('style', 'text-align:center');
		var th_n_vot = $('<th>', {text: "Votes"});
		th_loc.attr('style', 'text-align:center');
		var th_vot = $('<th>', {text: "Do you want to Vote?"});
		th_vot.attr('style', 'text-align:center');

		var head= thead.append(tr.append(th_art).append(th_loc).append(th_n_vot).append(th_vot));

		
		for(var i=0; i<data.length;i++){

			tr = $("<tr></tr>");

			art = $("<td>", {text: data[i][1]});
			art.attr('style', 'text-align:center');
			loc = $("<td>", {text: data[i][0] });
			loc.attr('style', 'text-align: center');
			n_votes = $("<td>", {text:data[i][2]});
			n_votes.attr('style', 'text-align: center');
			td=$('<td></td>');
			td.attr('style', 'text-align: center');
			votes = $("<a>", {text: "Vote" }, "</a>");
			votes.attr("href", 'javascript:vote("'+data[i][4].substring(15)+'")' );
			
			
			tb.append(tr.append(art).append(loc).append(n_votes).append(td.append(votes)));

			
		}
		table.append(head).append(tb);

		
		$('#interestingEvents').html(table);
		   
	});

}


