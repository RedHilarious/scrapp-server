# -*- coding: utf-8 -*-

from flask import g
from flask_restful import marshal_with
from resource_helper import DbResource
from resources import resource_helper
from util.decorators import check_token
from flask_restful import reqparse
from flask_restful import fields
import datetime


class RuleSubscriptionCollection(DbResource):
    """ RuleSubscriptionCollection.
    Inherits from DbResource, where the database connection is given.
    """

    def __init__(self):
        """ Init argument parser for data validation. """
        self._parser = reqparse.RequestParser()
        self._parser.add_argument("start_time", type=fields.DateTime, location="json")
        self._parser.add_argument("interval", type=int, location="json")
        self._args = self._parser.parse_args()

        super(RuleSubscriptionCollection, self).__init__()

    @check_token
    @marshal_with(resource_helper.rule_collection_fields)
    def post(self, rule_id):
        """ Post method for this subscription.
        Creates a new subscription for this user and given rule id.
        :param rule_id: id of related rule
        :return: response with related rule
        """

        user = g.get('user', None)

        # convert DateTime object from client to matching database format
        start_time = datetime.datetime.strptime(self._args["start_time"].dt_format, "%Y-%m-%dT%H:%M:%S%f")

        # create subscription in DB
        self._db.create_subscription(user["user_id"], rule_id, start_time, self._args["interval"])

        return self._db.get_rule(rule_id), 201

    @check_token
    @marshal_with(resource_helper.rule_collection_fields)
    def put(self, rule_id):
        """ Put method for this subscription.
        Update subscription for this user and given rule id.
        :param rule_id: id of related rule
        :return: response with related rule
        """

        user = g.get('user', None)

        # convert DateTime object from client to matching database format
        start_time = datetime.datetime.strptime(self._args["start_time"].dt_format, "%Y-%m-%dT%H:%M:%S%f")

        # create subscription in DB
        self._db.update_subscription(user["user_id"], rule_id, start_time, self._args["interval"])

        return resource_helper.empty_response(204)

    @check_token
    def delete(self, rule_id):
        """ Delete method for subscription.
        :param rule_id: related rule id
        :return: empty response object
        """

        user = g.get('user', None)
        self._db.set_deleted_flag_for_subscription(user["user_id"], rule_id)

        return resource_helper.empty_response(204)


class Subscription(DbResource):
    """ SubscriptionCollection.
    Inherits from DbResource, where the database connection is given.
    """

    def get(self, subscription_id):
        """ Get method for subscription.
        :param subscription_id: id of requested subscription
        :return: the matching subscription
        """

        return self._db.get_rule(subscription_id)
