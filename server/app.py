#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

# HELPER FUNCTIONS
def find_restaurants_byID(restaurant_id):
    return Restaurant.query.where(Restaurant.id == restaurant_id).first()

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

@app.get('/restaurants')
def get_all_restaurants():
    all_restaurants = Restaurant.query.all()
    restaurant_dicts = [restaurant.to_dict(rules = ['-pizzas', '-restaurant_pizzas',]) for restaurant in all_restaurants]
    return restaurant_dicts, 200

@app.get('/restaurants/<int:id>')
def get_restaurant_by_id(id):

    found_restaurant = find_restaurants_byID(id)

    if found_restaurant:
        return found_restaurant.to_dict(rules = ['-pizzas', '-restaurant_pizzas.pizza.restaurants',]), 200
    else:
        return { "error": "Restaurant not found" }, 404

@app.delete('/restaurants/<int:id>')
def delete_restaurant(id):
    found_restaurant = find_restaurants_byID(id)

    if found_restaurant:
        db.session.delete( found_restaurant )
        db.session.commit()
        return{}, 204 
    else:
        return {"error":"Restaurant not found"}

@app.get('/pizzas')
def get_all_pizzas():
    all_pizzas = Pizza.query.all()
    pizza_dicts = [pizza.to_dict(rules = ['-restaurant_pizzas', '-restaurants',]) for pizza in all_pizzas]
    return pizza_dicts, 200

@app.post('/restaurant_pizzas')
def create_new_rp():
    data = request.json

    try:
        new_restaurant_pizza = RestaurantPizza( price = data.get("price"),
                                                pizza_id = data.get("pizza_id"),
                                                restaurant_id = data.get("restaurant_id"))
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return new_restaurant_pizza.to_dict(rules = ['-pizza.restaurants', '-restaurant.pizzas']), 201
    
    except:
        return{ "errors": ["validation errors"]}, 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
