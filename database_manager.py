# -*- coding: utf-8 -*-

import config
import psycopg2 as pg
import psycopg2.extensions as extensions
import psycopg2.extras as extras
from util.exceptions import UserAlreadyExisting


class DatabaseManager(object):
    """ Class to connect to a given database. """

    _connection = None
    _cursor = None

    def __init__(self):
        """ Connect to the database. """

        try:
            self._connection = pg.connect(database=config.DATABASE, user=config.USER,
                                          password=config.PASSWORD, host=config.HOST,
                                          port=config.PORT)
            self._cursor = self._connection.cursor(cursor_factory=extras.RealDictCursor)  # DictCursor does not work
            # retrieve all data as unicode
            extensions.register_type(extensions.UNICODE, self._cursor)
        except:
            raise pg.DatabaseError('Unable to connect to the database. Please check your configuration.')

    def __del__(self):
        """ Disconnect the database. """
        self.close()

    def close(self):
        """ Close database connection. """
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()

    #
    # Rules
    #
    def get_rules(self, updated_at_server):
        """
        Get all rules.
        :param updated_at_server: If not None, only newer rules will be returned.
        :return: list of rules
        """

        sql = "SELECT rule_id, title, description, updated_at AT TIME ZONE 'utc' AS updated_at_server FROM rule "

        if updated_at_server:
            sql += " WHERE updated_at AT TIME ZONE 'utc' > %s;"
            self._cursor.execute(sql, (updated_at_server, ))
        else:
            sql += ";"
            self._cursor.execute(sql)

        return self._cursor.fetchall()

    def get_rule(self, rule_id, updated_at_server=None):
        """
        Get a rule by given rule_id with relationships of action and action_param.
        :param rule_id: rule_id of the requested rule
        :param updated_at_server: If not None, only newer rules will be returned.
        :return: rule with relationships as dict
        """

        # select rule by id
        self._cursor.execute("SELECT rule_id, title, description, updated_at AT TIME ZONE 'utc' AS updated_at_server "
                             "FROM rule WHERE rule_id = %s ;", (rule_id,))
        rule = self._cursor.fetchone()

        # select its actions
        sql = "SELECT action_id, title, rule_id, position, method, url, parse_expression, parse_type, " \
              "parse_expression_display, parse_type_display, updated_at AT TIME ZONE 'utc' AS updated_at_server " \
              "FROM action WHERE rule_id = %s "

        if updated_at_server:
            sql += " AND updated_at AT TIME ZONE 'utc' > %s;"
            self._cursor.execute(sql, (rule_id, updated_at_server))
        else:
            sql += ";"
            self._cursor.execute(sql, (rule_id,))

        actions = self._cursor.fetchall()

        for action in actions:
            self._cursor.execute("SELECT action_param_id, title, key, type, value, required, "
                                 "updated_at AT TIME ZONE 'utc' AS updated_at_server FROM action_param "
                                 "WHERE action_id = %s ;", (action["action_id"],))
            action_params = self._cursor.fetchall()
            if action_params:
                action["action_params"] = action_params
        print rule
        rule["actions"] = actions

        return rule

    def create_rule(self, rule_dict):
        """
        Inserts a Rule with Actions and ActionParams.
        :param rule_dict: rule to insert
        :return: created rule with actions and action params
        """
        sql_rule = "INSERT INTO rule (title, description) VALUES (%(title)s, %(description)s) RETURNING rule_id;"
        sql_action = "INSERT INTO action (title, rule_id, position, method, url, parse_expression, parse_type, " \
                     "parse_expression_display, parse_type_display)" \
                     "VALUES (%(title)s, %(rule_id)s, %(position)s, %(method)s, %(url)s, %(parse_expression)s, %(parse_type)s, " \
                     "%(parse_expression_display)s, %(parse_type_display)s)" \
                     "RETURNING action_id;"
        sql_action_param = "INSERT INTO action_param (action_id, title, key, value, type, required) " \
                           "VALUES (%(action_id)s, %(title)s, %(key)s, %(value)s, %(type)s, %(required)s);"

        try:
            # insert rule
            self._cursor.execute(sql_rule, rule_dict)
            rule_id = self._cursor.fetchone()['rule_id']

            # insert actions
            for action in rule_dict["actions"]:
                # set rule id for relation
                action["rule_id"] = rule_id
                self._cursor.execute(sql_action, action)
                action_id = self._cursor.fetchone()["action_id"]

                # insert action params if any given
                if "action_params" in action and action["action_params"]:
                    for action_param in action["action_params"]:
                        # set action id for relation
                        action_param["action_id"] = action_id
                        self._cursor.execute(sql_action_param, action_param)
        except:
            self._connection.rollback()
            return None

        self._connection.commit()
        return self.get_rule(rule_id)

    #
    # Users
    #
    def create_user(self, identity_token, gcm_token):
        """
        Inserts a new user.
        :param identity_token: identity token
        :param gcm_token: gcm token
        """

        try:
            sql = "INSERT INTO app_user (identity_token, gcm_token) VALUES (%s, %s);"
            self._cursor.execute(sql, (identity_token, gcm_token))
        except pg.IntegrityError:
            self._connection.rollback()
            raise UserAlreadyExisting
        self._connection.commit()

    def get_user_by_identity_token(self, identity_token):
        """
        Selects a user by a given identity token.
        :param identity_token: identity token
        :return: user
        """

        sql = "SELECT * FROM app_user WHERE identity_token = %s;"
        self._cursor.execute(sql, (identity_token, ))
        return self._cursor.fetchone()

    def get_user_by_user_id(self, user_id):
        """
        Selects a user by a given user id.
        :param user_id: user id
        :return: user
        """

        sql = "SELECT * FROM app_user WHERE user_id = %s;"
        self._cursor.execute(sql, (user_id, ))
        return self._cursor.fetchone()

    def get_user_by_gcm_token(self, gcm_token):
        """
        Selects a user by a given gcm token.
        :param gcm_token: gcm token
        :return: user
        """

        sql = "SELECT * FROM app_user WHERE gcm_token = %s;"
        self._cursor.execute(sql, (gcm_token, ))
        return self._cursor.fetchone()

    def get_users_by_rule_id(self, rule_id):
        """
        Selects all users for a subscription by given rule id.
        :param rule_id: rule id
        :return: list of users
        """

        sql = "SELECT * FROM app_user AS a JOIN subscription AS s ON(a.user_id = s.user_id) WHERE s.rule_id = %s;"
        self._cursor.execute(sql, (rule_id,))
        return self._cursor.fetchall()

    def get_users(self):
        """
        Selects all users.
        :return: list of users
        """

        sql = "SELECT * FROM app_user;"
        self._cursor.execute(sql)
        return self._cursor.fetchall()

    #
    # Subscriptions
    #
    def create_subscription(self, user_id, rule_id, start_time, interval):
        """
        (Re)subscribe to a rule.

        :param user_id: user_id
        :param rule_id: rule_id to subscribe
        :param start_time: timestamp of scrape start
        :param interval: frequency of scraping
        """

        dic = {'user_id': user_id, 'rule_id': rule_id, 'start_time': start_time, 'interval': interval}
        # TODO: anstatt manuell UPDATE ausführen methode update_subscription aufrufen?
        # try to update a (maybe) existing subscription
        update_sql = "UPDATE subscription SET deleted_at = NULL, start_time = %(start_time)s, interval = %(interval)s  " \
                     "WHERE user_id = %(user_id)s AND rule_id = %(rule_id)s;"
        self._cursor.execute(update_sql, dic)

        # try to insert if row does not exist already
        insert_sql = "INSERT INTO subscription (user_id, rule_id, start_time, interval) " \
                     "  SELECT %(user_id)s, %(rule_id)s, %(start_time)s, %(interval)s " \
                     "      WHERE NOT EXISTS " \
                     "      (SELECT 1 FROM subscription WHERE user_id = %(user_id)s AND rule_id = %(rule_id)s);"
        self._cursor.execute(insert_sql, dic)

        # commit transaction
        self._connection.commit()

    def get_subscription(self, user_id, rule_id):
        """
        Get a subscription by given user and rule ids.

        :param user_id: user_id
        :param rule_id: rule_id
        :return: subscription
        """

        sql = "SELECT * FROM subscription WHERE user_id = %s AND rule_id = %s;"
        self._cursor.execute(sql, (user_id, rule_id))
        return self._cursor.fetchone()

    def update_subscription(self, user_id, rule_id, start_time, interval):
        """
        Update a subscription by given user, rule id, start time and frequency of scraping.

        :param user_id: user_id
        :param rule_id: rule_id
        :param start_time: timestamp of scrape start
        :param interval: frequency of scraping
        """

        dic = {'user_id': user_id, 'rule_id': rule_id, 'start_time': start_time, 'interval': interval}

        # try to update a (maybe) existing subscription
        update_sql = "UPDATE subscription SET deleted_at = NULL, start_time = %(start_time)s, interval = %(interval)s  " \
                     "WHERE user_id = %(user_id)s AND rule_id = %(rule_id)s;"
        self._cursor.execute(update_sql, dic)

        # commit transaction
        self._connection.commit()


    def set_deleted_flag_for_subscription(self, user_id, rule_id):
        """
        Set the deleted_at flag for a subscription to indicate that the user un-subscribed to this rule.

        :param rule_id: rule to un-subscribe
        :param user_id: user_id
        """

        sql = "UPDATE subscription SET deleted_at = now() WHERE rule_id = %s AND user_id = %s;"
        self._cursor.execute(sql, (rule_id, user_id))
        self._connection.commit()

    #
    # Results
    #
    def get_results(self, subscription_id=None):
        """ Retrieves either all results for given subscription or all results of all subscriptions.
        :param subscription_id: related subscription
        :return: results
        """

        sql = "SELECT * FROM result"
        if subscription_id is None:
            sql += ";"
            self._cursor.execute(sql)
        else:
            sql += " WHERE subscription_id = %s;"
            self._cursor.execute(sql, (subscription_id,))
        return self._cursor.fetchall()

    def get_result(self, result_id):
        """ Retrieves result by its id.
        :param result_id: id of requested result
        :return: the requested result
        """

        self._cursor.execute("SELECT * FROM result WHERE result_id = %s ;", (result_id,))
        return self._cursor.fetchone()

    def create_result(self, subscription_id, result_hash, last_modified):
        """ Creates a result for passed subscription.
        :param subscription_id: related subscription
        :param result_hash: new results hash
        :param last_modified: new results last modified time
        :return: id of new inserted result
        """

        sql = "INSERT INTO result (subscription_id, hash, last_modified) VALUES (%s, %s, %s) RETURNING result_id;"
        self._cursor.execute(sql, (subscription_id, result_hash, last_modified))
        self._connection.commit()
        # retrieve result_id of new inserted result
        return self._cursor.fetchone()

    #
    # Current_results
    #
    def get_current_result(self, rule_id, proof_read=False):
        """ Retrieve the last result for related rule. Depending on proof_read flag, relation is locked
        for other clients.
        :param rule_id: related rule
        :param proof_read: flag, if relation is needed to be locked for other inserts/updates
        :return: last result
        """

        sql = "SELECT * FROM current_result WHERE rule_id = %s"
        update = ";"
        if proof_read:
            update = " FOR UPDATE NOWAIT;"
        sql += update
        self._cursor.execute(sql, (rule_id,))
        return self._cursor.fetchone()

    def update_current_result(self, rule_id, result_hash, last_modified):
        """ Update last result of related rule with new hash and new last modified time.
        :param rule_id: related rule
        :param result_hash: new hash
        :param last_modified: new last modified time
        """

        sql = "UPDATE current_result SET (hash, last_modified) = (%s,%s) WHERE rule_id = %s;"
        self._cursor.execute(sql, (result_hash, last_modified, rule_id))
        self._connection.commit()

    def insert_current_result(self, rule_id, result_hash, last_modified):
        """ Insert a last result for related rule.
        :param rule_id: related rule
        :param result_hash: results hash
        :param last_modified: results last modified time
        """

        sql = "INSERT INTO current_result (rule_id, hash, last_modified) VALUES (%s,%s,%s);"
        self._cursor.execute(sql, (rule_id, result_hash, last_modified))
        self._connection.commit()
