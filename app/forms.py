from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Tables, MenuCategory

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

class AddCategory(FlaskForm):
    name = StringField("Category name", validators=[Length(max=50)])
    add = SubmitField("Create")

class OrderForm(FlaskForm):
    notes = StringField("Notes")
    order = SubmitField("Order")

class AddDish(FlaskForm):
    # categories option are left out to be dynamically generated within the template
    categories = SelectField("Categories", validators = [DataRequired()])
    price = IntegerField("Price", validators=[DataRequired(), Length(max=3)])
    preparation_time = IntegerField("Preparation Time", validators=[Length(max=3)])
    title = StringField("Dish title", validators=[DataRequired(), Length(max=50)])
    description = StringField("Dish title", validators=[Length(max=200)])
    thumbnail = FileField("Thumbnail", validators=[FileRequired(), FileAllowed(["jpg", "png"], "Only .png & .jpg allowed")])
    add = SubmitField("Create")
