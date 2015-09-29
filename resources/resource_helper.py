# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import g
import flask
from flask_restful import fields
from database_manager import DatabaseManager


class DbResource(Resource):
    """
    Database Resource.
    All actual resources inherit from this class,
    because here the DB-Connection is given.
    """
    def __init__(self):
        self._db = g.get('db', DatabaseManager())
        super(DbResource, self).__init__()


def empty_response(status_code=200):
    """

    :param status_code: HTTP Status-Code, default=200
    :return: empty response Object
    """
    response = flask.make_response("")
    response.headers['content-type'] = 'application/json'
    response.status_code = status_code
    return response


# define fields for rule_collection
rule_collection_fields = {
    'rule_id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'updated_at_server': fields.DateTime(dt_format='iso8601')
}

# define fields for action_param
action_param_fields = {
    'action_param_id': fields.Integer,
    'title': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
    'key': fields.String,
    'value': fields.String,
    'type': fields.String,
    'required': fields.Boolean,
    'updated_at_server': fields.DateTime(dt_format='iso8601')
}

# define fields for action
action_fields = {
    'action_id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'updated_at': fields.DateTime(dt_format='iso8601'),
    'parse_expression': fields.String,
    'parse_type': fields.String,
    'parse_expression_display': fields.String,
    'parse_type_display': fields.String,
    'position': fields.Integer,
    'method': fields.String,
    'action_params': fields.Nested(action_param_fields, allow_null=True),
    'updated_at_server': fields.DateTime(dt_format='iso8601')
}

# define fields for single rule resource
rule_fields = {
    'rule_id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'actions': fields.Nested(action_fields, allow_null=True),
    'updated_at_server': fields.DateTime(dt_format='iso8601')
}
