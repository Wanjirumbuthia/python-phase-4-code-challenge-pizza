from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
    return make_response(jsonify(restaurants), 200)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        restaurant_data = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [rp.to_dict() for rp in restaurant.restaurant_pizzas]
        }
        return make_response(jsonify(restaurant_data), 200)
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response(jsonify({"message": "Restaurant deleted successfully"}), 204)
    else:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    return make_response(jsonify(pizzas), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not all([price, pizza_id, restaurant_id]):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    try:
        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)

        if pizza is None or restaurant is None:
            return make_response(jsonify({"errors": ["Pizza or Restaurant not found"]}), 404)

        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response_data = new_restaurant_pizza.to_dict()
        return make_response(jsonify(response_data), 201)

    except ValueError as e:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)