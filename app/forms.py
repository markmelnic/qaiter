from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Table, MenuCategory

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

class AddDish(FlaskForm):
    categories = SelectField("Categories", choices=[cat.name for cat in MenuCategory.query.all()], validators = [DataRequired()])
    price = IntegerField("Price", validators=[DataRequired(), Length(max=3)])
    preparation_time = IntegerField("Preparation Time", validators=[Length(max=3)])
    title = StringField("Dish title", validators=[DataRequired(), Length(max=50)])
    description = StringField("Dish title", validators=[Length(max=200)])
    add = SubmitField("Create")
