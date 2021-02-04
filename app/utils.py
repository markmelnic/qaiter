import os
from werkzeug.utils import secure_filename

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

    return products, total_price, preparation_time

def handle_image(image, filename, path):
    name = secure_filename('.'.join([filename, image.filename.split(".")[1]]))
    path = os.path.join("app", path, name)
    print(os.getcwd())
    print(path)
    image.save(path)
    return path[4:]
