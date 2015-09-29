__author__ = 'tginz001'

from gcm import GCM
import config

_gcm = GCM(config.GCM_API_KEY)


def send_update_notification(tokens, rule_id):
    """
    Sends an notification about rule updates to a given list of gcm tokens.

    :param tokens: gcm tokens
    :param rule_id: rule id
    """

    data = {'rule_id': rule_id}
    response = _gcm.json_request(registration_ids=tokens, data=data)

    if 'errors' in response:
        for error, reg_ids in response['errors'].items():
            print 'gcm error:', error, reg_ids
            # TODO: log instead of print
