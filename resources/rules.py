# -*- coding: utf-8 -*-

from resource_helper import DbResource
from flask_restful import marshal_with
from resources import resource_helper
from util.decorators import check_token
from flask import request
from flask_restful import reqparse


class RuleCollection(DbResource):
    @marshal_with(resource_helper.rule_fields)
    def post(self):
        """
        Post Method for this resource.
        Creates a Rule with given Actions and ActionParams.
        :return: created Rule with Actions and ActionParams
        """
        parser = reqparse.RequestParser()
        parser.add_argument("title", required=True, location="json")
        parser.add_argument("description", required=True, location="json")
        parser.add_argument('actions', type=dict, action='append', required=True)
        args = parser.parse_args()

        # check actions whether all required params are set
        for action in args["actions"]:
            if "method" not in action:
                return {"message": {"method": "Missing required parameter in the Action body"}}, 400
            if "position" not in action:
                return {"message": {"position": "Missing required parameter in the Action body"}}, 400

            # add None to dict to insert NULL values
            set_dict_fields(action, action_fields)

            # if action params are given -> check required parameters
            if "action_params" in action and action["action_params"]:
                for action_param in action["action_params"]:
                    if "key" not in action_param:
                        return {"message": {"key": "Missing required parameter in the Action Param body"}}, 400
                    if "type" not in action_param:
                        return {"message": {"type": "Missing required parameter in the Action Param body"}}, 400

                    # add None to dict to insert NULL values
                    set_dict_fields(action_param, action_param_fields)

                    if action_param["required"] is None:
                        action_param["required"] = True

        return self._db.create_rule(args), 201

    @check_token
    @marshal_with(resource_helper.rule_collection_fields)
    def get(self):
        """ Get method for this resource.
        :return: all rules from database
        """

        updated_at_server = request.headers.get('Updated-At-Server')
        return self._db.get_rules(updated_at_server)


class Rule(DbResource):
    """ Rule Resource.
    Inherits from DbResource, where the database connection is given.
    """

    def __init__(self):
        super(Rule, self).__init__()

    @check_token
    @marshal_with(resource_helper.rule_fields)
    def get(self, rule_id):
        """ Get method for this resource.
        :return: one rule with requested rule id
        """

        updated_at_server = request.headers.get('Updated-At-Server')
        return self._db.get_rule(rule_id, updated_at_server)


action_fields = ["title", "url", "parse_expression", "parse_type", "parse_expression_display", "parse_type_display"]
action_param_fields = ["title", "value", "required"]


def set_dict_fields(action, fields):
    for field in fields:
        if field not in action:
            action[field] = None
