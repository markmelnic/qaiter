from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Table

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")

class AddTable(FlaskForm):
    number = IntegerField("Table Number", validators=[DataRequired(), Length(max=3)])
    seats = IntegerField("Number of seats", validators=[Length(max=3)])
    description = StringField("Number of seats", validators=[Length(max=50)])
    add = SubmitField("Add")
