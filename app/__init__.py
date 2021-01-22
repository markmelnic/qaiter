import os, sass
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

sass.compile(dirname=('app/static/scss', 'app/static/css'), output_style='compressed')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "backdoor"
login_manager.login_message_category = "backdoor"

from app import routes