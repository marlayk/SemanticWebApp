from intro_to_flask import app
from flask import Flask, render_template, request, flash, session, redirect, url_for,jsonify
from forms import ContactForm, SignupForm, SigninForm, SearchForm
from flask.ext.mail import Message, Mail
from models import db, User
from flask.ext.wtf import Form
from flask_oauth import OAuth
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
import json
import urllib2
from urllib2 import Request, urlopen, URLError
from RDFhandler import addUser, checkEmail , userType, data_by_email, update_location ,latlng_by_email, add_event, create_event, show_description, RDFlike, favourite_artist,oauth_type
import musicbrainzngs
import pylast
from pylast import _extract
from RDFeventhandler import getartistinfo, request_events, getuserevents,event_vote, getinteresting
from xml.dom.minidom import parseString
from math import radians, cos, sin, asin, sqrt
from operator import itemgetter
from pylast import _extract

#--------------------------------------------------------------------------------------------------

FACEBOOK_APP_ID = '1425475621033434'
FACEBOOK_APP_SECRET = '5fa7fbad4a2edcc639524fd71f34fa09'

GOOGLE_CLIENT_ID = '485739322209-764j5vj22o5uc869bjpuuaqer03d08oq.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'f3F0UksoCqiO1tuTrGYC1oLV'
REDIRECT_URI = '/authorized'


#---------------------------------------------------------------------------------------------------

oauth = OAuth()
mail = Mail()


@app.route('/')
def home():
  return render_template('index.html')


#--------------------------------------------------------------

@app.route('/about')
def about():
  return render_template('about.html')

#---------------------------------------------------------------

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form)
    else:

      msg = Message(form.subject.data, sender='vu.amsterdam.iwa@gmail.com', recipients=['vu.amsterdam.iwa@gmail.com'])
      msg.body = """
      From: %s <%s>
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)

      return render_template('contact.html', success=True)
 
  elif request.method == 'GET':
    return render_template('contact.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm()

  if 'email' in session:
    return redirect(url_for('profile'))
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:

      addUser(None,form.username.data,form.email.data.lower(),form.password.data,form.location.data,"","Normal", form.lng.data , form.lat.data)

      session['email'] = form.email.data.lower()
      return redirect(url_for('profile'))

  elif request.method == 'GET':
    return render_template('signup.html', form=form)



@app.route('/profile', methods=['GET', 'POST'])
def profile():

  if 'email' not in session:
    return redirect(url_for('signin'))

  data = data_by_email(session['email'])
  oauthType = oauth_type(session['email'])[15:]

  return render_template('profile.html', username=data[0], location=data[1], userid=data[2][15:] ,oauthType=oauthType)



@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()

  if 'email' in session:
    return redirect(url_for('profile'))
   
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('profile'))
                 
  elif request.method == 'GET':
    return render_template('signin.html', form=form)



@app.route('/signout')
def signout():
 
  if 'email' not in session:
    return redirect(url_for('signin'))
     
  session.pop('email', None)
  return redirect(url_for('home'))


#----------ERROR HANDLING PAGES------------------

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500

#----------------------------------------------------

@app.route('/changeLocation', methods=['GET', 'POST'])
def changeLocation():

  location=request.args.get("location")
  lat=request.args.get("lat")
  lng=request.args.get("lng")
  print session['email']
  update_location(location,lat,lng, session['email'])
  return "ok"


@app.route('/getLatLng', methods=['GET', 'POST'])
def getLatLng():
  data =  latlng_by_email(session['email'])
  
  result = {"lat": data[0] , "lng" : data[1] }

  return json.dumps(result)


#------------------------------------------------------
#--------    FACEBOOK   -------------------------------
#------------------------------------------------------


facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email, user_location'}
)


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
     
    if checkEmail(me.data['email'])== False :
      url = "http://graph.facebook.com/"+ me.data['location']['id']
      result = urllib2.urlopen(url).read()
      result = json.loads(result)

      addUser(me.data['id'],me.data['username'], me.data['email'], 'abcde',me.data['location']['name'],resp['access_token'],"facebook",str(result['location']['longitude']),str(result['location']['latitude']))
      session['email'] = me.data['email'] 
      return redirect(url_for('profile'))      
    else:
      if userType(me.data['email']) == "facebook":
        session['email'] = me.data['email']
        return redirect(url_for('profile'))
      else:
        form = SigninForm()
        form.email.errors = ["Wrong Account Type"]
        return render_template('signin.html', form=form)
      


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


#------------------------------------------------------
#--------    GOOGLE   -------------------------------
#------------------------------------------------------

google = oauth.remote_app('google',
        base_url='https://www.google.com/accounts/',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        request_token_url=None,
        request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_method='POST',
        access_token_params={'grant_type': 'authorization_code'},
        consumer_key=GOOGLE_CLIENT_ID,
        consumer_secret=GOOGLE_CLIENT_SECRET)


@app.route('/glogin')
def glogin():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)



@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token
    

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('glogin'))

    res = json.load(res)
    if checkEmail(res['email'])== False :

      addUser(res['id'],res['name'],res['email'],"123",None, access_token , "google",None, None)
      session['email'] = res['email']

      return  redirect(url_for('profile'))    
    else:
      if userType(res['email']) == "google":
        session['email'] = res['email']

        return  redirect(url_for('profile'))
      else:
        form = SigninForm()
        form.email.errors = ["Wrong Account Type"]
        return render_template('signin.html', form=form)

@google.tokengetter
def get_access_token():
    return session.get('access_token')



#------------------------------------------------------------------------


@app.route('/artists', methods=['GET', 'POST'])
def artists():
  q = request.args.get('artist')
  musicbrainzngs.set_useragent("test",1,None)
  artists = musicbrainzngs.search_artists(q,["ended"])
  return jsonify(artists)


@app.route('/songs',methods=['GET', 'POST'])
def songs():
  id = request.args.get('id')


  API_KEY = '4bea9a7cfe15b09d2ada827592605ee0'
  API_SECRET = '13b346b26064a3537796608d27802711'

  username = "nicksar11"
  password_hash = pylast.md5("cavcle501")
  network = pylast.LastFMNetwork(api_key=API_KEY,api_secret=API_SECRET,username=username,password_hash=password_hash)

  fetchedArtist = network.get_artist_by_mbid(id)
  tracks = fetchedArtist._request("artist.getTopTracks", True)
  result = ""  

  for track in tracks.getElementsByTagName('track'):
    name = track.getElementsByTagName('name')[0].firstChild.nodeValue
    result = result + "<p ><strong><a style='text-decoration: none; cursor: pointer' Onclick=\'getvideo(\""+fetchedArtist.get_name()+" "+name+"\")\'>"+name+"</a></strong> <button onclick='likeSong(\""+name.replace (" ", "_")+"\")' class='btn-xs pull-right btn btn-primary'>Like</button></p>"
  return result

@app.route('/like')
def like():
  if 'email' not in session:
    return "Not logged in"

  ArtistId = request.args.get('id')
  ArtistName = request.args.get('name')
  likeType = request.args.get('likeType')

  RDFlike(ArtistId, likeType ,session['email'], ArtistName)
  return "Ok"


@app.route('/createEvent')
def createEvent():

  mbid    = request.args.get("mbid")
  artist  = request.args.get("artist")
  print mbid,artist
  boolean = create_event(mbid ,artist, session['email'])
  if boolean: 
    return "OK"
  else:
    return "already exist"


@app.route('/addEvent' , methods = ['GET','POST'])
def addEvent():

  if ((request.args.get('description') == None) or (request.args.get('description') == " ") or (request.args.get('description') == '')):
    desc='sorry no description is provided for this event...'    
  else:
    desc       = request.args.get('description')

  city_dec     = request.args.get('city') 
  city_encoded = str(city_dec.encode('utf-8', 'ignore'))
  city_decoded = str(city_dec.decode('utf-8', 'ignore'))
  desc_encoded = str(desc.encode('utf-8', 'ignore'))
  desc_decoded = str(desc.decode('utf-8', 'ignore'))
  

  longitude    = request.args.get('longitude')
  latitude     = request.args.get('latitude')
  start_time   = request.args.get('start_time')
  source       = request.args.get('source')
  artist       = request.args.get('artist')
  mbid         = request.args.get('mbid')
  userid       = data_by_email(session['email'])[2]

  add_event(city_decoded,latitude,longitude,start_time,desc_decoded,source,artist,mbid,userid)

  return "Ok"


@app.route('/showDescription' , methods = ['GET','POST'])
def showDescription():
  mbid = request.args.get('mbid')
  city = request.args.get('city')
  desc = show_description(mbid,city)

  return desc


@app.route('/favouriteArtist')
def favouriteArtist():

  Fartist= favourite_artist(session['email'])
  print Fartist
  return json.dumps(Fartist)


@app.route('/searchArtists')
def browseArtists():
  return render_template('browseArtists.html')


@app.route('/browseEvent')
def browseEvent():
  return render_template('BrowseEvents.html')


@app.route('/demandEvent')
def demandEvent():
  return render_template('createEvent.html')


@app.route('/artistinfo',methods=['GET', 'POST'])
def artistinfo():
  artistid = request.args.get('id')
  artistname = request.args.get('name')
  return getartistinfo(artistid,artistname)


@app.route('/requestEvents' , methods = ['GET','POST'])
def requestEvents():
  mbid = request.args.get('mbid')
  return json.dumps(request_events(mbid))


@app.route('/vote' , methods = ['GET','POST'])
def vote():
  eventid = request.args.get('eventid')

  event_vote(eventid,session['email'])
  return "ok"


@app.route('/getmyEvents')
def getmyEvents():
  myEvents = getuserevents(session['email'])

  return json.dumps(myEvents)

@app.route('/getinterestingEvents')
def getinterestingEvents():
  myEvents = getinteresting(session['email'])
  userdata = latlng_by_email(session['email'])
  userlat = userdata[0]
  userlng = userdata[1]
  result = []

  
  for event in myEvents:
    dist = haversine(float(userlng),float(userlat),float(event['lng']['value']),float(event['lat']['value']))
    result.append((event['location']['value'] , event['artist']['value'],event['votes']['value'] ,dist ,event['eventid']['value']))

  result = sorted(result, key=itemgetter(3))

  return json.dumps(result)



def haversine(lon1, lat1, lon2, lat2):
  """
  Calculate the great circle distance between two points 
  on the earth (specified in decimal degrees)
  """
  # convert decimal degrees to radians 
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
  # haversine formula 
  dlon = lon2 - lon1 
  dlat = lat2 - lat1 
  a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a)) 
  km = 6367 * c
  return km
