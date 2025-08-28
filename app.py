#!/usr/bin/python
import logging
from flask import Flask, request

app = Flask(__name__)
logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('test.log')
logger.addHandler(handler)


def check_user_validity(user):
    user_required_fields = ['username', 'enabled', 'firstName', 'lastName', 'email']

    for field in user_required_fields:
        if field not in user:
            return False
    return True


def check_user_credentials(user):
    user_credentials = ['value', 'temporary']

    for field in user_credentials:
        if field not in user['credentials']:
            return False
    return True


@app.route('/users', methods=['POST'])
def create_user():
    user = request.json
    print(check_user_validity(user))
    print(check_user_credentials(user))
    return 'Created User!'


@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    return f'Here is {id} User!'


@app.route('/users', methods=['GET'])
def get_users():
    return 'Here are Users!'


@app.route('/users/<id>/reset-password', methods=['PUT'])
def reset_password(id):
    return f'{id} User\'s password reset!'


@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    return f'{id} User deleted!'


app.run()
