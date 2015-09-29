__author__ = 'Rahel'

"""
All exceptions raised on server.
"""


class UserAlreadyExisting(Exception):
    """ Exception if a user already exists. """

    def __init__(self):
        self.message = 'Gcm-Token already exists.'
        self.error_code = 403
