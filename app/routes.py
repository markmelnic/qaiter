import os
from flask import (
    request,
    render_template,
    url_for,
    redirect,
    flash,
    get_flashed_messages,
    jsonify,
)
from app import app, db, bcrypt
from app.models import User
from app.forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required

db.create_all()
db.session.commit()

if not User.query.filter_by(username=os.getenv('ADMIN_USER')).first():
    user = User(
            username=os.getenv('ADMIN_USER'),
            role="admin",
            password=bcrypt.generate_password_hash(os.getenv('ADMIN_PASS')).decode("utf-8"),
        )
    db.session.add(user)
    db.session.commit()

@app.route("/")
def home():
    return redirect(url_for("backdoor"))

@app.route("/backdoor")
def backdoor():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    login_form = LoginForm()
    return render_template("backdoor.pug", login_form=login_form)

@app.route("/login", methods=["POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash(u"Incorrect password - username combination!", "login_error")
            return redirect(url_for("backdoor"))
    flash(u"User not found!", "login_error")
    return redirect(url_for("backdoor"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template(
        "dashboard.pug"
    )
