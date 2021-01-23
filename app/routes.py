import os, shutil, pyqrcode
from flask import (
    request,
    render_template,
    url_for,
    redirect,
    flash,
    get_flashed_messages,
    jsonify,
    send_from_directory,
    send_file,
)
from app import app, db, bcrypt
from app.models import User, Table
from app.forms import LoginForm, AddTable
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

@app.route("/table-<table_number>", methods=["GET"])
def home(table_number):
    return render_template("general/index.pug")

@app.route("/backdoor", methods=["GET"])
def backdoor():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        login_form = LoginForm()
        return render_template("backdoor.pug", login_form=login_form)

@app.route("/login", methods=["POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash(u"Incorrect password - username combination!", "login_error")
            return redirect(url_for("backdoor"))
    else:
        flash(u"User not found!", "login_error")
        return redirect(url_for("backdoor"))

@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("backdoor"))

@login_required
@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard/dashboard.pug")

@login_required
@app.route("/tables", methods=["GET"])
def tables():
    add_table_form = AddTable()
    tables = Table.query.all()
    return render_template("dashboard/tables.pug", tables=tables, table_form=add_table_form)

@login_required
@app.route("/add_table", methods=["POST"])
def add_table():
    table_form = AddTable()

    base_url = '/'.join(request.base_url.split("/")[:-1])
    qrurl = base_url + "/table-{}".format(table_form.number.data)
    qrfile = 'table{}.png'.format(table_form.number.data)
    qrcode = pyqrcode.create(qrurl, error='Q', version=5, mode='binary')
    qrcode.png(qrfile, scale=10, module_color=[0, 0, 0, 128])
    qrpath = 'app/' + app.config['UPLOAD_FOLDER'] + str(qrfile)
    shutil.move(qrfile, qrpath)

    table = Table(
        number=table_form.number.data,
        seats=table_form.seats.data,
        description=table_form.description.data,
        path=qrpath,
        url=qrurl,
        imgurl=base_url + "/" + qrpath[3:],
    )
    db.session.add(table)
    db.session.commit()
    return redirect(url_for("tables"))

@login_required
@app.route("/remove-table-<table_number>", methods=["GET"])
def remove_table(table_number):
    Table.query.filter_by(number=table_number).delete()
    db.session.commit()
    return redirect(url_for("tables"))

@login_required
@app.route('/qrdownload/<table_number>', methods=["GET", 'POST'])
def qrdownload(table_number):
    uploads_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_file(uploads_dir+'table{}.png'.format(table_number), as_attachment=True)

@login_required
@app.route('/qrview/<table_number>', methods=["GET", 'POST'])
def qrview(table_number):
    uploads_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads_dir, filename='table{}.png'.format(table_number))
