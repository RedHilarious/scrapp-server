#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import g
from flask_restful import Api
from resources.rules import Rule, RuleCollection
from resources.subscriptions import Subscription, RuleSubscriptionCollection
from resources.users import User, UserCollection
from resources.results import Result
import config
from database_manager import DatabaseManager
from flask import render_template, request

"""
Scrapp Server RESTful-Api.
Built with Flask and Flask-RESTful.
"""

app = Flask(__name__)
api = Api(app)

PREFIX = "/api/v1"

# add Resources to API
api.add_resource(RuleCollection, PREFIX+"/rules")
api.add_resource(Rule, PREFIX+"/rules/<int:rule_id>")
api.add_resource(Result, PREFIX+"/rules/<int:rule_id>/result")

api.add_resource(RuleSubscriptionCollection, PREFIX+"/rules/<int:rule_id>/subscriptions")
api.add_resource(Subscription, PREFIX+"/subscriptions/<int:subscription_id>")

api.add_resource(UserCollection, PREFIX+"/users")
api.add_resource(User, PREFIX+"/users/<int:user_id>")


@app.before_request
def before_request():
    """
    Gets called before each request.
    Stores DatabaseManager instance in global g object.
    """
    g.db = DatabaseManager()


@app.teardown_request
def teardown_request(exception):
    """
    Gets called after each request.
    Closes Database Connection.
    """
    db = g.get('db', None)
    if db:
        db.close()


@app.route('/')
def hello_world():
    create_rule_url = request.base_url + PREFIX[1:] + "/rules"
    return render_template('editor.html', create_rule_url=create_rule_url)

if __name__ == '__main__':
    app.run(debug=True, host=config.SERVER_URL, port=config.SERVER_PORT)
