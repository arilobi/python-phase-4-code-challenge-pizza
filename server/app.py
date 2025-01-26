#!/usr/bin/env python3
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

# ---> Getting the restaurants
@app.route("/restaurants", methods=["GET"])
def fetch_restaurants():
    restaurants = Restaurant.query.all()

    restaurant_list = []

    for restaurant in restaurants:
        restaurant_list.append(restaurant.to_dict(only=(
            'id', 
            'name', 
            'address'
        )))
    return jsonify(restaurant_list), 200

# ---> Getting the restaurant by id
@app.route("/restaurants/<int:id>", methods=["GET"])
def single_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if restaurant:
        return jsonify(restaurant.to_dict(only=(
            'id', 
            'name', 
            'address', 
            'restaurant_pizzas.pizza', 
            'restaurant_pizzas.id', 
            'restaurant_pizzas.price', 
            'restaurant_pizzas.pizza_id', 
            'restaurant_pizzas.restaurant_id'
        ))), 200
    
    else:
        return jsonify({"error": "Restaurant not found"}), 404
    
# ---> Delete restaurants by id
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id): 
    restaurant = Restaurant.query.get(id)

    if restaurant: 

        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204 # ---> means no content but the request is successful
    else:
        return jsonify({"error": "Restaurant not found"})

# ---> Fetching pizzas
@app.route("/pizzas", methods=["GET"])
def fetch_pizzas():
    pizzas = Pizza.query.all()

    pizza_list = []

    for pizza in pizzas:
        pizza_list.append(pizza.to_dict(only=(
            'id', 
            'name', 
            'ingredients'
        )))
    return jsonify(pizza_list), 200

# ---> Add a new restaurant_pizza
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    # Checking id the restaurant and pizza exists
    restaurant = Restaurant.query.get(data.get('restaurant_id'))
    pizza = Pizza.query.get(data.get('pizza_id'))

    if not restaurant or not pizza:
        return jsonify({"errors": ["Restaurant and Pizza doesn't exist"]}), 406
    
    # creating the new RestaurantPizza with validation
    try:
        new_restaurant_pizza = RestaurantPizza(
            price = data.get('price'),
            pizza_id = data.get('pizza_id'),
            restaurant_id = data.get('restaurant_id'),
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response_data = new_restaurant_pizza.to_dict(only=(
            'id', 
            'price', 
            'pizza', 
            'restaurant'
        ))
        return jsonify(response_data), 201
    
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
