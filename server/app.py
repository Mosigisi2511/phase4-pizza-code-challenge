#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class RestaurantResource(Resource):
    def get(self, id=None):
        if id:
            restaurant = db.session.get(Restaurant, id)
            if restaurant:
                return make_response(restaurant.to_dict(), 200)
            return make_response({"error": "Restaurant not found"}, 404)
        restaurants = Restaurant.query.all()
        return make_response([r.to_dict() for r in restaurants], 200)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        return make_response({"error": "Restaurant not found"}, 404)

class PizzaResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response([p.to_dict() for p in pizzas], 200)

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        try:
            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()
            return make_response(restaurant_pizza.to_dict(), 201)
        except ValueError as e:
            return make_response({"errors": [str(e)]}, 400)

api.add_resource(RestaurantResource, '/restaurants', '/restaurants/<int:id>')
api.add_resource(PizzaResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
