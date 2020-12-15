"""

    Grinberg-style settings management is a feature of version four.

    The former settings.cfg variables ARE NOT USED in this version of the app
    and are therefore not maintained or persisted.

"""

# standard library
from datetime import datetime
import os
import socket
import sys

class Config(object):

    with open('.api_key', 'r') as file:
        API_KEY = file.read().strip().replace('\n','')

    APP_AGE = int((datetime.now() - datetime(2015, 11, 10)).days / 365)
    APP_DESC = (
        "KDM-Manager is a free, online campaign manager application for "
        "Kingdom Death: Monster that uses interactive forms and "
        "automates repetitive record-keeping tasks. "
    )
    APP_NAME = "KDM-Manager"
    APP_TAG = "The original online campaign manager for Kingdom Death: Monster!"
    SESSION_COOKIE_NAME = 'kdm-manager_session'
    DEBUG = True
    DEVELOPMENT = {
        'api_port': 8013,
    }
    DEV_SSL_CERT = 'deploy/dev_cert.pem'
    DEV_SSL_KEY = 'deploy/dev_key.pem'
    PORT = 8014
    PRODUCTION = {
        'api_url': 'https://api.kdm-manager.com/',
        'app_fqdn': 'advanced-kdm-manager.c.kdm-manager.internal'
    }
    SECRET_KEY = os.environ.get('SECRET_KEY') or str(sys.path)
    VERSION = "4.0.0"


    def __init__(self):
        """ Whenever we initialize the Config object, we need to set API
        variables. """

        if socket.getfqdn() == self.PRODUCTION['app_fqdn']:
            self.API = {
                'url': self.PRODUCTION['api_url'],
                'verify_ssl': True,
            }
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip_address = s.getsockname()[0]
            s.close()

            self.API = {
                'url': 'https://%s:%s/' % (
                    local_ip_address,
                    self.DEVELOPMENT['api_port']
                ),
                'verify_ssl': False,
            }
