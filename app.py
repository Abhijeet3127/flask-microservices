# app.py (User Authentication Microservice)

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Product, Order
import logging


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this in production
jwt = JWTManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
def create_tables():
    with app.app_context():
        db.create_all()

@app.before_first_request
def setup():
    return create_tables()

# users = []

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(person_name = data['person_name'],email = data['email'], username=data['username'], password=data['password'])
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify(message=str(e)), 409
    return jsonify(message='User registered successfully'), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    return jsonify(users_data), 200

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'password': user.password
        }), 200
    else:
        return jsonify(message='User not found'), 404

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Retrieve user by username and password
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Invalid username or password'), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(name=data['name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify(message='Product created successfully'), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    products_data = [{'id': product.id, 'name': product.name, 'price': product.price} for product in products]
    return jsonify(products_data), 200

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price
        }), 200
    else:
        return jsonify(message='Product not found'), 404

@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    product_id = data['product_id']
    product_data = Product.query.get(product_id)
    # logging.info("getting product %s ::",product)
    # print(product)
    price = product_data.price
    quantity = data['quantity']
    total_price = price * quantity
    new_order = Order(user_id=data['user_id'], product_id=data['product_id'], quantity=data['quantity'],total_price = total_price)
    db.session.add(new_order)
    db.session.commit()
    return jsonify(message='Order created successfully'), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    orders_data = [{'id': order.id, 'user_id': order.user_id, 'product_id': order.product_id, 'quantity': order.quantity, 'total_price': order.total_price} for order in orders]
    return jsonify(orders_data), 200

@app.route('/orders/<order_id>',methods = ['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        return jsonify({
            'id': order.id,
            'user_id': order.user_id,
            'product_id': order.product_id,
            'quantity': order.quantity,
            'total_price': order.total_price
        }), 200
    else:
        return jsonify(message='Order not found'), 404
    
@app.route('/<entity>/<int:id>', methods=['DELETE'])
def delete_entity(entity, id):
    model = getattr(globals()[entity.capitalize()], 'query', None)
    if model is not None:
        entity_obj = model.get(id)
        if entity_obj:
            db.session.delete(entity_obj)
            db.session.commit()
            return jsonify(message=f'{entity.capitalize()} deleted successfully'), 200
        else:
            return jsonify(message=f'{entity.capitalize()} not found'), 404
    else:
        return jsonify(message='Invalid entity'), 400
    

if __name__ == '__main__':
    app.run(debug=True)
