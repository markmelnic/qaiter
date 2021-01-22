from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def get_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(60), nullable=False)

    firstname = db.Column(db.String(30))
    surname = db.Column(db.String(30))
    profile_picture = db.Column(db.String(20), nullable=False, default="default.jpeg")

    def __repr__(self):
        return f"User({self.role} - {self.username}, {self.email} - {self.firstname} {self.surname})"
