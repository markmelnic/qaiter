import os, sass, stripe
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["QRS_FOLDER"] = "app/static/img/qrcodes/"
app.config["DSHES_FOLDER"] = "app/static/img/dishes/"
app.config["CATGS_FOLDER"] = "app/static/img/categories/"

CORS(app, resources={r'/*': {'origins': '*'}})

sass.compile(dirname=('app/static/scss', 'app/static/css'), output_style='compressed')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "backdoor"
login_manager.login_message_category = "backdoor"

from app import routes