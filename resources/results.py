# -*- coding: utf-8 -*-

from flask import g
from resource_helper import DbResource
from util.decorators import check_token
from flask_restful import reqparse
from util import gcm_manager
import psycopg2
from flask_restful import fields
import datetime


class ResultCollection(DbResource):
    """ ResultCollection.
    Inherits from DbResource, where the database connection is given.
    """

    @check_token
    def get(self):
        """ Get method for this resource.
        :return: all results from database
        """
        return self._db.get_results()


class Result(DbResource):
    """ Result Resource.
    Inherits from DbResource, where the database connection is given.
    """

    def __init__(self):
        """ Init argument parser for data validation. """
        self._parser = reqparse.RequestParser()
        self._parser.add_argument("hash", type=str, location="json")
        self._parser.add_argument("last_modified", type=fields.DateTime, location="json")
        self._args = self._parser.parse_args()

        super(Result, self).__init__()

    @check_token
    def get(self, result_id):
        """ Get method for this resource.
        :param result_id: id of requested result
        :return: the matching result
        """
        return self._db.get_result(result_id)

    @check_token
    def post(self, rule_id):
        """ Post method for this result.
        Inserts a new result into database and notifies other subscribers if necessary.
        :param rule_id: id of related rule
        :return: response with id of new result
        """
        return self._process_result(rule_id, self._args["hash"], self._args["last_modified"])

    def _process_result(self, rule_id, new_hash, new_lm):
        """ Process a result.
        Determines if incoming result is newest and in this case notifies all subscribers.
        Inserts the new result to database.
        :param rule_id: related rule id
        :param new_hash: new results hash value
        :param new_lm: new results last modified time
        :return: response with id of new result
        """
        current_result = self._db.get_current_result(rule_id)

        # convert DateTime object from client to matching database format
        new_lm = datetime.datetime.strptime(new_lm.dt_format, "%Y-%m-%dT%H:%M:%S%f")

        # insert into result table
        new_result_id = self._insert_new_result(rule_id, new_hash, new_lm)

        if current_result is None:
            # there is no result for this rule yet
            try:
                self._db.insert_current_result(rule_id, new_hash, new_lm)
                self._send_notification(rule_id)
            except psycopg2.IntegrityError:
                pass
        elif current_result["hash"] != new_hash:
            # there is already a result for this rule but hash is unlike
            # reading again to proof if current_result is unchanged
            check_result = self._db.get_current_result(rule_id, True)
            # hash is still the same
            if current_result['hash'] == check_result['hash']:
                self._db.update_current_result(rule_id, new_hash, new_lm)
                self._send_notification(rule_id)

        return {"result_id": new_result_id["result_id"]}, 201

    def _insert_new_result(self, rule_id, new_hash, new_lm):
        """ Inserts new result to database.
        :param rule_id: related rule id
        :param new_hash: new results hash
        :param new_lm: new results last modified time
        :return: new results id
        """
        user = g.get('user', None)
        # insert new result in result relation for my subscription
        subscription = self._db.get_subscription(user["user_id"], rule_id)
        return self._db.create_result(subscription["subscription_id"], new_hash, new_lm)

    def _send_notification(self, rule_id):
        """ Sends notification to all related subscribers.
        :param rule_id: related rule id
        """
        me = g.get('user', None)
        # retrieve all gcm tokens of subscribed users for this rule
        gcm_tokens = [user["gcm_token"] for user in self._db.get_users_by_rule_id(rule_id)
                      if me["identity_token"] != user["identity_token"]]
        if gcm_tokens:
            gcm_manager.send_update_notification(gcm_tokens, rule_id)
