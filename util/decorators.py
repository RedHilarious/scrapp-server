from functools import wraps
from flask import request
from flask import g
from database_manager import DatabaseManager

"""
Decorators can be used to inject additional functionality to one or more functions
with just @decorator_name.
"""


def check_token(f):
    """ Checks if Identity-Token is given and if its valid. """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """ Decorator function to authenticate the accessing user.
        :param args:
        :param kwargs:
        :return: this function
        """
        identity_token = request.headers.get("Identity-Token")
        if identity_token:
            db = g.get("db", DatabaseManager())
            user = db.get_user_by_identity_token(identity_token)

            if not user:
                return {"error": "Identity-Token is not valid."}, 403
            # append user to session
            g.user = user
        else:
            return {"error": "Identity-Token is missing"}, 401
        return f(*args, **kwargs)
    return decorated_function
