import os
from werkzeug.utils import secure_filename
from app import APP_SETTINGS, S3_CLI, S3_RES

def handle_cart(cart, dish_db):
    products = []
    if cart != {}:
        for product in cart:
            dish = dish_db.query.filter_by(title=product).first()
            products.append((dish.title, dish.price, cart[product], dish.preparation_time))
        total_price = sum([p[1]*p[2] for p in products])
        preparation_time = max([p[3] for p in products])
    else:
        total_price = 0
        preparation_time = 0

    return products, int(total_price * 100), preparation_time

def load_orders(orders_db, order_statuses):
    products, orders = {}, {}
    products['placed_products'], products['active_products'], products['completed_products'] = [], [], []

    orders['placed_orders'] = orders_db.query.filter_by(status=order_statuses.placed).all()
    for order in orders['placed_orders']:
        temp = eval(order.products)
        products['placed_products'].append([(t, temp[t]) for t in temp])

    orders['active_orders'] = orders_db.query.filter_by(status=order_statuses.active).all()
    for order in orders['active_orders']:
        temp = eval(order.products)
        products['active_products'].append([(t, temp[t]) for t in temp])

    orders['completed_orders'] = orders_db.query.filter_by(status=order_statuses.complete).all()
    for order in orders['completed_orders']:
        temp = eval(order.products)
        products['completed_products'].append([(t, temp[t]) for t in temp])

    return products, orders

def get_all_ingredients(category_db, dish_db):
    return [[[[ing for ing in ing_list.split("-")] for ing_list in dishes_.ingredients.split("|")] for dishes_ in dish_db.query.filter_by(category=cat.id).all()] for cat in category_db.query.all()]

def upload_image(filename, image=False):
    filename = secure_filename(filename)
    if not ".png" in filename:
        filename += ".png"
    if image:
        image.save(filename)

    S3_CLI.upload_file(
        Bucket = APP_SETTINGS.aws_s3_bucket,
        Filename=filename,
        Key=filename,
        ExtraArgs={
            "ACL": 'public-read-write',
        }
    )
    os.remove(filename)

    return filename, 'http://{}.s3.amazonaws.com/{}'.format(APP_SETTINGS.aws_s3_bucket, filename)

def delete_image(filename):
    S3_RES.Object(APP_SETTINGS.aws_s3_bucket, filename).delete()
