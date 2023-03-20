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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code

db_drop_and_create_all()

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    }), 200

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    }), 200

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title is None or recipe is None:
        abort(400)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if title is not None:
        drink.title = title

    if recipe is not None:
        drink.recipe = json.dumps(recipe)

    drink.update()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        "success": True,
        "delete": id
    }), 200
