from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Users, Tables, MenuCategory

class OrderForm(FlaskForm):
    notes = StringField("Notes")
    order = SubmitField("Order")

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
    name = StringField("Category name", validators=[DataRequired(), Length(min=1, max=50),])
    thumbnail = FileField("Thumbnail", validators=[FileAllowed(["jpg", "png"], "Only .png & .jpg allowed"),])
    add = SubmitField("Create")

class AddDish(FlaskForm):
    categories = SelectField("Categories", choices=[], validators=[DataRequired()])
    price = IntegerField("Price", validators=[DataRequired()])
    preparation_time = IntegerField("Preparation Time")
    title = StringField("Dish title", validators=[DataRequired(), Length(min=1, max=60)])
    description = StringField("Dish title")
    ingredients = StringField("Ingredients")
    thumbnail = FileField("Thumbnail", validators=[FileAllowed(["jpg", "png"])])
    add = SubmitField("Add")
