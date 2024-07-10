from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        my_restaurant_list = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
            for restaurant in restaurants
        ]
        response = make_response(
            jsonify(my_restaurant_list),
            200
        )
        return response

api.add_resource(Restaurants, "/restaurants")

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
            pizza_details = [
                {
                    "id": rp.id,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients
                    },
                    "pizza_id": rp.pizza_id,
                    "price": rp.price,
                    "restaurant_id": rp.restaurant_id
                }
                for rp in restaurant_pizzas
            ]
            restaurant_data = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "restaurant_pizzas": pizza_details
            }
            response = make_response(
                jsonify(restaurant_data),
                200
            )
            return response
        else:
            return make_response(
                jsonify({"error": "Restaurant not found"}),
                404
            )

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            response = {
                "error": "Restaurant not found"
            }
            return make_response(
                jsonify(response),
                404
            )

        restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
        for rp in restaurant_pizzas:
            db.session.delete(rp)
        
        db.session.delete(restaurant)
        db.session.commit()

        response_dict = {
            "message": "Restaurant successfully deleted"
        }
        response = make_response(
            response_dict,
            204
        )
        return response

api.add_resource(RestaurantById, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()  
        pizza_list = [
            {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
            for pizza in pizzas
        ]
        response = make_response(
            jsonify(pizza_list),
            200
        )
        return response

api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        
        if not (price and pizza_id and restaurant_id):
            return jsonify({"errors": ["validation errors"]}), 400

     
        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)

        if not pizza:
            return jsonify({"errors": ["Pizza not found"]}), 404
        if not restaurant:
            return jsonify({"errors": ["Restaurant not found"]}), 404
        try:
            validated_price = int(price)
            if not (1 <= validated_price <= 30):
                return jsonify({"errors": ["validation errors"]}), 400
        except ValueError:
            return jsonify({"errors": ["validation errors"]}), 400

        new_restaurant_pizza = RestaurantPizza(
            price=validated_price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        try:
            db.session.add(new_restaurant_pizza)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"errors": [str(e)]}), 500  
        response_data = {
            "id": new_restaurant_pizza.id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "pizza_id": new_restaurant_pizza.pizza_id,
            "price": new_restaurant_pizza.price,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            },
            "restaurant_id": new_restaurant_pizza.restaurant_id
        }

        return jsonify(response_data), 201 

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
