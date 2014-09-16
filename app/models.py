from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
 
db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'users'
  uid = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(54))
  location = db.Column(db.String(100))
  oauth_token = db.Column(db.String(200))
   
  def __init__(self, username, email, password, location, oauth_token):
    self.username = username.title()
    self.email = email.lower()
    self.set_password(password)
    self.location = location.title()
    if oauth_token == None:
      self.oauth_token = None
    else:
      self.oauth_token = oauth_token.title()
     
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)
