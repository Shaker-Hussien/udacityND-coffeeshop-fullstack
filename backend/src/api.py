import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def retrieve_drinks():
    try:
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in Drink.query.all()],
        }), 200
    except Exception as error:
        # print(error)
        abort(500)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_details(token):

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in Drink.query.all()],
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    data = request.get_json()
    drink_title = data.get('title', None)
    drink_recipe = data.get('recipe', None)

    if not drink_title or not drink_recipe or Drink.query.filter(Drink.title == drink_title).one_or_none():
        abort(400)

    try:
        new_drink = Drink(title=drink_title, recipe=json.dumps(drink_recipe))
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        }), 200

    except Exception as error:
        # print(error)
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(token , drink_id):
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(404)

    data = request.get_json()
    drink_title = data.get('title', None)
    drink_recipe = data.get('recipe', None)

    try:

        if drink_title and drink.title != drink_title:
            drink.title = drink_title
        if drink_recipe and json.loads(drink.recipe) != drink_recipe:
            drink.recipe = json.dumps(drink_recipe)

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except Exception as error:
        # print(error)
        abort(422)


@ app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token , drink_id):

    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": drink.id
        })
    except Exception as error:
        # print(error)
        abort(422)

# Error Handlers

@ app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@ app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@ app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@ app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@ app.errorhandler(500)
def internal_erver_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def authentication_err(exception):
    return jsonify({
        "success": False,
        "error": exception.status_code,
        "message": exception.error
    }), exception.status_code
