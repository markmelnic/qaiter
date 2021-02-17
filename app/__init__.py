import os, sass, boto3, stripe
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

from app.models import Users, Settings

db.create_all()
db.session.commit()

if not Users.query.filter_by(username=os.getenv('ADMIN_USER')).first():
    user = Users(
            username=os.getenv('ADMIN_USER'),
            email=os.getenv('ADMIN_EMAIL'),
            role="admin",
            password=bcrypt.generate_password_hash(os.getenv('ADMIN_PASS')).decode("utf-8"),
        )
    db.session.add(user)
    db.session.commit()

if not Settings.query.first():
    db.session.add(Settings())

APP_SETTINGS = Settings.query.first()
stripe.api_key = APP_SETTINGS.stripe_secret_key

S3_CLI = boto3.client(
    "s3",
    aws_access_key_id=APP_SETTINGS.aws_s3_key_id,
    aws_secret_access_key=APP_SETTINGS.aws_s3_key_secret
)
S3_RES = boto3.resource(
    "s3",
    aws_access_key_id=APP_SETTINGS.aws_s3_key_id,
    aws_secret_access_key=APP_SETTINGS.aws_s3_key_secret
)

TABLE_NUMBER, CART = None, {}

from app import routes