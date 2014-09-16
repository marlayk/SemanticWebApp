from SPARQLWrapper import SPARQLWrapper, JSON
import uuid
from werkzeug import generate_password_hash, check_password_hash


def addUser( userid ,username , email , password , location , oauthtoken ,authtype, lng, lat):

	if userid == None:
	   userid = str(uuid.uuid1())
	
	password = generate_password_hash(password)
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	if location == None:
		locSparqlString = ""
	else:
		locSparqlString = """<http://example/hasLocation> '"""+location+"""';
		<http://example/hasLng>  '"""+lng+"""';
		<http://example/hasLat>  '"""+lat+"""';"""
	q = """
	INSERT DATA
	{ <http://example/"""+ userid +""">     a             <http://example/User> ;
					  <http://example/hasPassword> '""" + password+"""';
					  <http://example/hasName> '""" + username+"""';
					  <http://example/hasEmail>	'"""+email+"""';
					  """ + locSparqlString + """
					  <http://example/hasOauthtoken> '"""+oauthtoken+"""';
					  <http://example/hasAuthType> <http://example/"""+ authtype +""">
	 }"""

	sparql.setQuery(q)
	sparql.method = 'POST'
	sparql.query()
	

def checkEmail(email) :

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """
	ASK
	{
	?user <http://example/hasEmail> '"""+email+"""'.
	}"""
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()

	return results["boolean"]


def authenticate(email,password):
	
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """
	SELECT ?password WHERE
	{
	?user <http://example/hasEmail> '"""+email+"""';
	      <http://example/hasPassword> ?password.
	}"""
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	
	resu = results['results']['bindings'][0]['password']['value']
	return check_password_hash(resu,password)


def userType(email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT ?userType WHERE {
	?userid a <http://example/User> ;
	       <http://example/hasEmail> '"""+email+"""';
	       <http://example/hasAuthType> ?userType.
	}"""
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	return results['results']['bindings'][0]['userType']['value'][15:]



def data_by_email(email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT ?username ?location ?userid WHERE {
	?userid a <http://example/User> ;
	       <http://example/hasEmail> '""" + email + """';	       
	       <http://example/hasName> ?username.
	       OPTIONAL{?userid <http://example/hasLocation> ?location.}
	       
	}"""
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	data = []
	print results
	data.append(results['results']['bindings'][0]['username']['value'])
	try :
		data.append(results['results']['bindings'][0]['location']['value'])
	
	except:
		data.append("Undefined")

	data.append(results['results']['bindings'][0]['userid']['value'])

	return data


def latlng_by_email(email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ SELECT ?lat ?lng  WHERE {
	?userid a <http://example/User> ;
	       <http://example/hasEmail> '""" + email + """';	       
	       <http://example/hasLat> ?lat;
	       <http://example/hasLng> ?lng.
	}"""
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	ltnlng = []

	ltnlng.append(results['results']['bindings'][0]['lat']['value'])
	ltnlng.append(results['results']['bindings'][0]['lng']['value'])
	return ltnlng



def update_location(location,lat, lng ,email):
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	q = """
	DELETE {?userid <http://example/hasLocation> ?location.
					?userid <http://example/hasLat> ?lat.
					?userid <http://example/hasLng> ?lng. }
	INSERT {?userid <http://example/hasLocation> '""" + location+"""'.
			?userid <http://example/hasLat> '""" + lat+"""'.
			?userid <http://example/hasLng> '""" + lng+"""'. } 
	WHERE{
	?userid <http://example/hasEmail>	'"""+email+"""' .
			OPTIONAL{
				?userid <http://example/hasLocation> ?location.
				?userid <http://example/hasLat> ?lat.
				?userid <http://example/hasLng> ?lng.
			}
	        
	}"""
	
	sparql.setQuery(q)
	sparql.method = 'POST'
	sparql.query()



def RDFlike(artistid, likeType , email, artistname):
	userid = data_by_email(email)[2]
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	

	if likeType == "Artist":

		sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
		q = """
		INSERT DATA
		{ <"""+userid+"""> <http://example/likes"""+likeType+"""> <http://musicbrainz.org/artist/""" +artistid+""">.
		<http://musicbrainz.org/artist/""" +artistid+"""> <http://example/hasName> '"""+artistname+"""'.
		}"""
	else:
		q = """
		INSERT DATA
		{ <"""+userid+"""> <http://example/likes"""+likeType+"""> <http://example/song/""" +artistname+""">.
		}"""


	sparql.setQuery(q)
	
	sparql.method = 'POST'
	sparql.query()



def add_event(city,latitude,longitude,start_time,description,source,artist,mbid,userid):
	
	if (checkEvent_by_city_name(artist,city)):
		return False

	eventid = str(uuid.uuid1())
	
	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1/statements")
	q = """
	INSERT DATA
	{		<http://example/"""+ eventid +""">     a             <http://example/Event>;
													   <http://example/hasLat> '""" + str(latitude)+"""';
										      		   <http://example/hasLng> '""" + str(longitude)+"""';
													   <http://example/hasCity> '""" + str(city)+"""';
			 										   <http://example/hasStartTime> '""" + str(start_time)+"""';
			 										   <http://example/hasDescription> '""" +description+"""';
			 										   <http://example/hasSource> '""" + str(source)+"""';
			 										   <http://example/hasArtistName> '""" + str(artist)+"""';
			 										   <http://example/hasCreatedByUserid> <""" + str(userid)+""">;
			 										   <http://example/hasArtistId>  <http://musicbrainz.org/artist/"""+ mbid+""">.
        
	}"""
	
	sparql.setQuery(q)
	sparql.method = 'POST'
	sparql.query()
	return True


def checkEvent_by_city_name(artist,city):

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """
	ASK
	{
	?eventid a <http://example/Event>;
			   <http://example/hasArtistName> 	'""" + str(artist)+"""';
			   <http://example/hasCity> 	'""" + str(city)+"""'.

	}"""
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()

	return results["boolean"]


def checkEvent_by_lat_long(lat,lng,mbid):

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """
	ASK
	{
	?eventid  <http://example/hasArtistId>  <http://musicbrainz.org/artist/"""+ mbid+""">;
			   <http://example/hasLat> 	'""" + lat + """';
			   <http://example/hasLong> 	'""" + lng +"""'.

	}"""
	print q
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()

	return results["boolean"]


def show_description(mbid,city):

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ 
	SELECT ?description   
	WHERE { ?eventid a <http://example/Event>;
					   <http://example/hasCity> '""" + city + """';
	       			   <http://example/hasArtistId>  <http://musicbrainz.org/artist/"""+ mbid+""">;      
	   				   <http://example/hasDescription>  ?description.
	}"""
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()

	try:
		return results['results']['bindings'][0]['description']['value']
	except IndexError:
		return "No Description Found for that Event"






def create_event(mbid,artist,email):
	latlng   = latlng_by_email(email)
	city     = data_by_email(email)[1]
	username = data_by_email(email)[0]
	userid   = data_by_email(email)[2]

	lat = latlng[0]
	lng = latlng[1]
	start_time  = "to be anounced..."
	description = "created by user " +username
	source      = "manually"

	if (checkEvent_by_lat_long(lat,lng,mbid)):
		return False

	return add_event(city,lat,lng,start_time,description,source,artist,mbid,userid)



def favourite_artist(email):

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ 
	SELECT ?artistname   
	WHERE { ?userid  <http://example/hasEmail>	'"""+email+"""' ;
					 <http://example/likesArtist> ?artistid.
			?artistid <http://example/hasName> ?artistname.

	}"""
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	
	return results['results']['bindings']



def oauth_type(email):

	sparql = SPARQLWrapper("http://localhost:8080/openrdf-sesame/repositories/1")
	q = """ 
	SELECT ?authtype  
	WHERE {
	?userid a <http://example/User> ;
	       <http://example/hasEmail> '""" + email + """';	       
	       <http://example/hasAuthType> ?authtype.
	}"""
	
	
	sparql.setReturnFormat(JSON)
	sparql.setQuery(q)
	sparql.method = 'GET'
	results = sparql.query().convert()
	
	
	return results['results']['bindings'][0]['authtype']['value']


