import pyqrcode, datetime, stripe
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
from app import *
from app.forms import *
from app.utils import *
from app.models import *
from werkzeug.datastructures import CombinedMultiDict

from flask_login import login_user, current_user, logout_user, login_required

### PUBLIC ROUTES ###

@app.route("/", methods=["GET"])
def def_home():
    now = datetime.datetime.now().hour
    if 5 < now < 12:
        greeting = 'Good Morning'
    elif 12 < now < 18:
        greeting = 'Good Afternoon'
    else:
        greeting = 'Good Evening'

    categories = [c for c in MenuCategory.query.all() if c.dishes]
    return render_template("general/index.pug", greeting=greeting, categories=categories, table=TABLE_NUMBER)

@app.route("/table/<table_number>", methods=["GET"])
def tab_home(table_number):
    if int(table_number) in [int(table.number) for table in Tables.query.filter_by(status=True).all()]:
        global TABLE_NUMBER, CART
        TABLE_NUMBER = int(table_number)
        CART = {}
    else:
        flash(u"Either table is disabled or non-existent", "table_error")
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
    details = {}
    details["products"], amount, details["preparation_time"] = handle_cart(CART, MenuDish)
    return render_template("general/cart.pug", app_settings=APP_SETTINGS, amount=amount, error=None, order_form=order_form, details=details)

@app.route("/add_to_cart/<dish_name>", methods=["GET"])
def add_to_cart(dish_name):
    try:
        CART[dish_name] += 1
    except KeyError:
        CART[dish_name] = 1
    return redirect(url_for("cart"))

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == 'GET':
        products = []
        preparation_time = 0
        amount = 0
        receipt = None

    elif request.method == 'POST':
        global CART
        order_form = OrderForm()
        products, amount, preparation_time = handle_cart(CART, MenuDish)

        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],
            source=request.form['stripeToken']
        )

        client = Customers(
            all_data = str(customer),
            identifier = customer["id"],
            created = customer["created"],
            phone = customer["phone"],
            name = customer["name"],
            email = customer["email"],
            )
        db.session.add(client)
        db.session.commit()

        try:
            charge = stripe.Charge.create(
                customer=customer.id,
                amount=amount,
                currency=APP_SETTINGS.stripe_currency,
                description=APP_SETTINGS.stripe_transaction_description,
            )
            receipt = charge["receipt_url"]

            if charge["paid"]:
                order = Orders(
                    all_data=str(charge),
                    placed = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M"),
                    products = str(CART),
                    table_number = TABLE_NUMBER,
                    preparation_time = preparation_time,
                    notes = order_form.notes.data,
                    amount = amount,
                    receipt=receipt,
                    )
                db.session.add(order)
                db.session.commit()
                CART = {}
        except stripe.error.CardError as e:
            #flash(f"{e.message}", "card_error")
            return redirect(url_for("cart"), error=e.message)

    return render_template("general/order.pug", products=products, preparation_time=preparation_time, amount=amount, receipt=receipt)


### DASHBOARD ROUTES ###

@app.route("/backdoor", methods=["GET"])
def backdoor():
    return redirect(url_for("dashboard")) if current_user.is_authenticated else render_template("dashboard/backdoor.pug", title="Login", login_form=LoginForm())

@app.route("/login", methods=["POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = Users.query.filter_by(username=login_form.username.data).first()
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
    products, orders = load_orders(Orders, OrderStatuses)
    return render_template("dashboard/dashboard.pug", title="Dashboard", user=current_user, orders=orders, products=products)

@login_required
@app.route("/orders", methods=["GET"])
def orders():
    products, orders = load_orders(Orders, OrderStatuses)
    return render_template("dashboard/orders.pug", title="Orders", user=current_user, orders=orders, products=products)

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
    tables = {}
    tables['active_tables'] = Tables.query.filter_by(status=True).all()
    tables['disabled_tables'] = Tables.query.filter_by(status=False).all()
    return render_template("dashboard/tables.pug", title="Tables", user=current_user, tables=tables, table_form=AddTable())

@login_required
@app.route("/settings", methods=["GET"])
def settings():
    return render_template("dashboard/settings.pug", title="Settings", user=current_user, settings=Settings.query.first(), settings_form=UpdateSettings())

@login_required
@app.route("/update_settings", methods=["POST"])
def update_settings():
    APP_SETTINGS = Settings.query.first()

    settings = UpdateSettings()
    APP_SETTINGS.stripe_secret_key = settings.stripe_secret_key.data
    APP_SETTINGS.stripe_publishable_key = settings.stripe_publishable_key.data
    APP_SETTINGS.stripe_currency = settings.stripe_currency.data
    APP_SETTINGS.stripe_transaction_description = settings.stripe_transaction_description.data

    APP_SETTINGS.aws_s3_bucket = settings.aws_s3_bucket.data
    APP_SETTINGS.aws_s3_key_id = settings.aws_s3_key_id.data
    APP_SETTINGS.aws_s3_key_secret = settings.aws_s3_key_secret.data
    db.session.commit()
    return redirect(url_for("settings"))

@login_required
@app.route("/add_table", methods=["POST"])
def add_table():
    table_form = AddTable()

    base_url = request.base_url.replace(url_for("add_table"), "")
    url = base_url + "/table/{}".format(table_form.number.data)
    filename = 'table_qr_{}.png'.format(table_form.number.data)
    qrcode = pyqrcode.create(url, error='Q', version=5, mode='binary')
    qrcode.png(filename, scale=10, module_color=[0, 0, 0, 128])

    if Tables.query.filter_by(number=table_form.number.data).first():
        flash(u"Table already exists", "exists_error")
    else:
        qrfilename, qrurl = upload_image(filename)
        table = Tables(
            number=table_form.number.data,
            seats=table_form.seats.data,
            description=table_form.description.data,
            url=url,
            qrfilename=qrfilename,
            qrurl=qrurl,
        )
        db.session.add(table)
        db.session.commit()
    return redirect(url_for("tables"))

@login_required
@app.route('/qrview/<table_number>', methods=["GET"])
def qrview(table_number):
    return send_from_directory(directory=app.config['QRS_FOLDER'][4:], filename='table{}.png'.format(table_number))

@login_required
@app.route("/qrtoggle/<table_number>", methods=["POST"])
def qrtoggle(table_number):
    table = Tables.query.filter_by(number=table_number).first()
    table.status = True if table.status else False
    db.session.commit()
    return redirect(url_for("tables"))

@login_required
@app.route("/table_remove/<table_number>", methods=["POST"])
def remove_table(table_number):
    filename = Tables.query.filter_by(number=table_number).first().qrfilename
    delete_image(filename)
    Tables.query.filter_by(number=table_number).delete()
    db.session.commit()
    return redirect(url_for("tables"))

@login_required
@app.route('/qrdownload/<table_number>', methods=["GET"])
def qrdownload(table_number):
    return send_file(Tables.query.filter_by(number=table_number).first().qrurl)

@login_required
@app.route("/menu", methods=["GET"])
def menu():
    dish_form = AddDish()
    dish_form.categories.choices = [(c.id, c.name) for c in MenuCategory.query.all()]

    indexed_ingredients = [(i.id, i.name) for i in Ingredients.query.all()]

    categories = MenuCategory.query.all()
    ingredients = get_all_ingredients(MenuCategory, MenuDish)

    return render_template("dashboard/menu.pug", title="Menu", user=current_user, create_category=AddCategory(), dish_form=dish_form, categories=categories, ingredients=ingredients, indexed_ingredients=indexed_ingredients)

@login_required
@app.route("/add_category", methods=["POST"])
def add_category():
    category_form = AddCategory(CombinedMultiDict((request.files, request.form)))

    if MenuCategory.query.filter_by(name=category_form.name.data).first():
        flash(u"Category already exists", "exists_error")
    elif category_form.validate_on_submit():
        filename, thumbnail = upload_image(category_form.name.data, image=category_form.thumbnail.data)
        category = MenuCategory(
            name=category_form.name.data,
            filename=filename,
            thumbnail=thumbnail,
        )
        db.session.add(category)
        db.session.commit()
    else:
        flash(u"Category validation error", "validation_error")

    return redirect(url_for("menu"))

@login_required
@app.route("/category_remove/<category_id>", methods=["GET"])
def remove_category(category_id):
    category = MenuCategory.query.filter_by(id=category_id).first()
    for dish in category.dishes:
        delete_image(dish.filename)
        db.session.delete(dish)
    delete_image(category.filename)
    db.session.delete(category)
    db.session.commit()

    return redirect(url_for("menu"))

@login_required
@app.route("/add_dish", methods=["POST"])
def add_dish():
    dish_form = AddDish(CombinedMultiDict((request.files, request.form)))
    dish_form.categories.choices = [(c.id, c.name) for c in MenuCategory.query.all()]

    if MenuDish.query.filter_by(title=dish_form.title.data).first():
        flash(u"Dish already exists", "exists_error")
    elif dish_form.validate_on_submit():
        for ingredient in dish_form.ingredients.data.split("|")[:-1]:
            name, _, _ = ingredient.split("-")
            #name = name.replace(" ", "_")
            if not Ingredients.query.filter_by(name=name).first():
                ingr = Ingredients(
                    name=name
                )
                db.session.add(ingr)

        filename, thumbnail = upload_image(dish_form.title.data, image=dish_form.thumbnail.data)
        dish = MenuDish(
            category = dish_form.categories.data,
            title = dish_form.title.data,
            description = dish_form.description.data,
            ingredients = dish_form.ingredients.data[:-1],
            price = dish_form.price.data,
            preparation_time = dish_form.preparation_time.data,
            filename=filename,
            thumbnail=thumbnail,
        )
        db.session.add(dish)
        db.session.commit()
    else:
        flash(u"Dish validation error", "validation_error")

    return redirect(url_for("menu"))

@login_required
@app.route("/dish_remove/<dish_id>", methods=["GET"])
def remove_dish(dish_id):
    dish = MenuDish.query.filter_by(id=dish_id).first()
    delete_image(dish.filename)
    db.session.delete(dish)
    db.session.commit()
    return redirect(url_for("menu"))
