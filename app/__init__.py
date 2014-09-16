from flask import Flask
 
app = Flask(__name__)
 
app.secret_key = 'development key'
 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'vu.amsterdam.iwa@gmail.com'
app.config["MAIL_PASSWORD"] = '123qw123qw'
 
from routes import mail
mail.init_app(app)


from models import db
db.init_app(app)
 
import intro_to_flask.routes