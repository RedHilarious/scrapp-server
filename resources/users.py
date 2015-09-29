# -*- coding: utf-8 -*-
import uuid
from flask_restful import reqparse
from resource_helper import DbResource
from util.exceptions import UserAlreadyExisting


class UserCollection(DbResource):
    """ UserCollection resource.
    Inherits from DbResource, where the database connection is given.
    """

    def __init__(self):
        """ Init argument parser for data validation. """
        self._parser = reqparse.RequestParser()
        self._parser.add_argument("gcm_token", type=str, required=True, location="json")
        self._args = self._parser.parse_args(strict=True)

        super(UserCollection, self).__init__()

    def post(self):
        """ Post method for this resource.
        Creates a new user in database and sends welcome notification.
        :return: response object with new users identity and gcm token
        """

        # generate random unique token
        identity_token = str(uuid.uuid4())
        gcm_token = self._args["gcm_token"]
        code = 201
        # create user in DB
        try:
            self._db.create_user(identity_token, gcm_token)
        except UserAlreadyExisting:
            user = self._db.get_user_by_gcm_token(gcm_token)
            identity_token = user["identity_token"]
            code = 200

        return {
            "identity_token": identity_token,
            "gcm_token": gcm_token
        }, code


class User(DbResource):
    """ User resource.
    Inherits from DbResource, where the database connection is given.
    """

    def get(self, user_id):
        """ Get method for this resource.
        :param user_id: id of requested user
        :return: the found user from DB
        """
        return self._db.get_user_by_user_id(user_id)
