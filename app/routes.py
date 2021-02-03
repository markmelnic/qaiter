import os, shutil, pyqrcode, json, datetime
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
from app.models import User, Tables, MenuCategory, MenuDish, Orders, OrderStatuses
from app.forms import LoginForm, AddTable, AddCategory, AddDish, OrderForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict

from flask_login import login_user, current_user, logout_user, login_required
from app.utils import *

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

TABLE_NUMBER, CART = None, {}

@app.route("/", methods=["GET"])
def def_home():
    return render_template("general/index.pug", categories=MenuCategory.query.all())

@app.route("/table/<table_number>", methods=["GET"])
def tab_home(table_number):
    if int(table_number) in [int(table.number) for table in Tables.query.all()]:
        global TABLE_NUMBER, CART
        TABLE_NUMBER = int(table_number)
        CART = {}
    else:
        flash(u"Table not found", "table_error")
    return redirect(url_for("def_home"))

@app.route("/category/<category_name>", methods=["GET"])
def category(category_name):
    dishes = MenuCategory.query.filter_by(name=category_name).first().dishes
    return render_template("general/category.pug", dishes=dishes)

@app.route("/dish/<dish_name>", methods=["GET"])
def dish(dish_name):
    dish = MenuDish.query.filter_by(title=dish_name).first()
    return render_template("general/dish.pug", dish=dish)

@app.route("/cart", methods=["GET"])
def cart():
    order_form = OrderForm()
    products, total_price, preparation_time = handle_cart(CART, MenuDish)
    return render_template("general/cart.pug", products=products, preparation_time=preparation_time, total_price=total_price, order_form=order_form)

@app.route("/add_to_cart/<dish_name>", methods=["GET"])
def add_to_cart(dish_name):
    try:
        CART[dish_name] += 1
    except KeyError:
        CART[dish_name] = 1
    return redirect(url_for("cart"))

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == 'POST':
        global CART
        order_form = OrderForm()
        products, total_price, preparation_time = handle_cart(CART, MenuDish)
        order = Orders(
            products = str(CART),
            created = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M"),
            table_number = TABLE_NUMBER,
            total_price = total_price,
            preparation_time = preparation_time,
            notes = order_form.notes.data
            )
        db.session.add(order)
        db.session.commit()
        CART = {}
    else:
        products = []
        preparation_time = 0
        total_price = 0

    return render_template("general/order.pug", products=products, preparation_time=preparation_time, total_price=total_price)


### DASHBOARD ROUTES ###

@app.route("/backdoor", methods=["GET"])
def backdoor():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    else:
        login_form = LoginForm()
        return render_template("dashboard/backdoor.pug", title="Login", login_form=login_form)

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
    return render_template("dashboard/layout.pug", title="Dashboard")

@login_required
@app.route("/orders", methods=["GET"])
def orders():
    products, orders = {}, {}
    products['placed_products'], products['active_products'], products['completed_products'] = [], [], []

    orders['placed_orders'] = Orders.query.filter_by(status=OrderStatuses.placed).all()
    for order in orders['placed_orders']:
        temp = eval(order.products)
        products['placed_products'].append([(t, temp[t]) for t in temp])

    orders['active_orders'] = Orders.query.filter_by(status=OrderStatuses.active).all()
    for order in orders['active_orders']:
        temp = eval(order.products)
        products['active_products'].append([(t, temp[t]) for t in temp])

    orders['completed_orders'] = Orders.query.filter_by(status=OrderStatuses.complete).all()
    for order in orders['completed_orders']:
        temp = eval(order.products)
        products['completed_products'].append([(t, temp[t]) for t in temp])
    return render_template("dashboard/orders.pug", title="Orders", orders=orders, products=products)

@login_required
@app.route("/activate_order/<order_id>", methods=["GET"])
def activate_order(order_id):
    order = Orders.query.filter_by(id=order_id).first()
    order.status = OrderStatuses.active
    order.activated = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
    db.session.commit()
    return redirect(url_for("orders"))

@login_required
@app.route("/complete_order/<order_id>", methods=["GET"])
def complete_order(order_id):
    order = Orders.query.filter_by(id=order_id).first()
    order.status = OrderStatuses.complete
    order.completed = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M")
    db.session.commit()
    return redirect(url_for("orders"))

@login_required
@app.route("/tables", methods=["GET"])
def tables():
    return render_template("dashboard/tables.pug", title="Tables", tables=Tables.query.all(), table_form=AddTable())

@login_required
@app.route("/settings", methods=["GET"])
def settings():
    return render_template("dashboard/settings.pug", title="Settings", tables=Tables.query.all(), table_form=AddTable())

@login_required
@app.route("/add_table", methods=["POST"])
def add_table():
    table_form = AddTable()

    base_url = request.base_url.replace(url_for("add_table"), "")
    qrurl = base_url + "/table/{}".format(table_form.number.data)
    qrfile = 'table{}.png'.format(table_form.number.data)
    qrcode = pyqrcode.create(qrurl, error='Q', version=5, mode='binary')
    qrcode.png(qrfile, scale=10, module_color=[0, 0, 0, 128])
    qrpath = 'app/' + app.config['QRS_FOLDER'] + str(qrfile)
    shutil.move(qrfile, qrpath)

    if Tables.query.filter_by(number=table_form.number.data).first():
        flash(u"Table already exists", "exists_error")
    else:
        table = Tables(
            number=table_form.number.data,
            seats=table_form.seats.data,
            description=table_form.description.data,
            path=qrpath,
            url=qrurl,
            imgurl=base_url + qrpath[3:],
        )
        db.session.add(table)
        db.session.commit()
    return redirect(url_for("tables"))

@login_required
@app.route("/table_remove/<table_number>", methods=["GET"])
def remove_table(table_number):
    os.remove(Tables.query.filter_by(number=table_number).first().path)
    Tables.query.filter_by(number=table_number).delete()
    db.session.commit()
    return redirect(url_for("tables"))

@login_required
@app.route('/qrdownload/<table_number>', methods=["GET"])
def qrdownload(table_number):
    uploads_dir = os.path.join(app.root_path, app.config['QRS_FOLDER'])
    return send_file(uploads_dir+'table{}.png'.format(table_number), as_attachment=True)

@login_required
@app.route('/qrview/<table_number>', methods=["GET"])
def qrview(table_number):
    uploads_dir = os.path.join(app.root_path, app.config['QRS_FOLDER'])
    return send_from_directory(directory=uploads_dir, filename='table{}.png'.format(table_number))

@login_required
@app.route("/menu", methods=["GET"])
def menu():
    categories = MenuCategory.query.all()
    dishes = [[dishes_ for dishes_ in MenuDish.query.filter_by(category=cat.id).all()] for cat in categories]
    return render_template("dashboard/menu.pug", title="Menu", create_category=AddCategory(), categories=categories, dish_form=AddDish(), dishes=dishes)

@login_required
@app.route("/add_category", methods=["POST"])
def add_category():
    category_form = AddCategory()

    if MenuCategory.query.filter_by(name=category_form.name.data).first():
        flash(u"Category already exists", "exists_error")
    else:
        category = MenuCategory(name=category_form.name.data)
        db.session.add(category)
        db.session.commit()
    return redirect(url_for("menu"))

@login_required
@app.route("/category_remove/<category_id>", methods=["GET"])
def remove_category(category_id):
    for dish in MenuCategory.query.filter_by(id=category_id).first().dishes:
        db.session.delete(dish)
    MenuCategory.query.filter_by(id=category_id).delete()
    db.session.commit()
    return redirect(url_for("menu"))

@login_required
@app.route("/add_dish", methods=["POST"])
def add_dish():
    #dish_form = AddDish()
    dish_form = AddDish(CombinedMultiDict((request.files, request.form)))

    if MenuDish.query.filter_by(title=dish_form.title.data).first() and dish_form.validate_on_submit():
        flash(u"Dish already exists", "exists_error")
    else:
        # handle photo
        thumbnail = dish_form.thumbnail.data
        thumb_name = secure_filename('.'.join([dish_form.title.data, thumbnail.filename.split(".")[1]]))
        thumb_path = os.path.join(app.config['DSHES_FOLDER'], thumb_name)
        thumbnail.save(thumb_path)

        dish = MenuDish(
            category = MenuCategory.query.filter_by(name=dish_form.categories.data).first().id,
            title = dish_form.title.data,
            description = dish_form.description.data,
            price = dish_form.price.data,
            preparation_time = dish_form.preparation_time.data,
            thumbnail = thumb_path[4:]
        )
        db.session.add(dish)
        db.session.commit()
    return redirect(url_for("menu"))

@login_required
@app.route("/dish_remove/<dish_id>", methods=["GET"])
def remove_dish(dish_id):
    MenuDish.query.filter_by(id=dish_id).delete()
    db.session.commit()
    return redirect(url_for("menu"))
