from flask.ext.wtf import Form
from wtforms import TextField,TextAreaField,SubmitField, validators, ValidationError, PasswordField, HiddenField
from wtforms.validators import Length, Email
from models import db, User
from RDFhandler import checkEmail, authenticate

class ContactForm(Form):
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = TextField("Email", [validators.Required("Please enter your email address.") , validators.Email()])
  subject = TextField("Subject", [validators.Required("Please enter a subject.")])
  message = TextAreaField("Message", [validators.Required("Please enter a message.")])
  submit = SubmitField("Send")

class SignupForm(Form):
  username = TextField("Username",  [validators.Required("Please enter your username.")])
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password."), Length(min=6, message=(u'Please give a longer password'))])
  location = TextField("Location",  [validators.Required("Please enter your location.")])
  lng = HiddenField("lng")
  lat = HiddenField("lat")
  submit = SubmitField("Create account")
 
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)

 
  def validate(self):
    if not Form.validate(self):
      return False
     
    
    if checkEmail(self.email.data.lower()):
      self.email.errors.append("That email is already taken")
      return False
    else:
      return True


class SigninForm(Form):
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Sign In")
   
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
 
  def validate(self):
    if not Form.validate(self):
      return False
    

    result = authenticate(self.email.data.lower() , self.password.data)

    if result:
      return True
    else:
      self.email.errors.append("Invalid e-mail or password")
      return False


class SearchForm(Form):
  search = TextField("Search Artist", [validators.Required("Please enter an Artist.")])
  submit = SubmitField("Search")

  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs) 

  def validate(self):
    if not Form.validate(self):
      return False