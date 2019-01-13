#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime
from flask import request, Response
import json

from models import users
import utils


def get_webapp_alerts():
    """ Returns all webapp alerts as JSON. """
    alerts = utils.mdb.notifications.find({'type': 'webapp_alert', 'expired': False}).sort('created_on', -1)
    alerts = list(alerts)
    return Response(response=json.dumps(alerts, default=json_util.default), status=200, mimetype="application/json")


class Alert:
    def __init__(self, _id=None):
        """ Initialize a webapp alert object from an _id. If one is not supplied,
        create a new alert. """

        self.logger = utils.get_logger()
        self.alert = {}

        self._id = _id
        if self._id is None and '_id' in request.json:
            self._id = ObjectId(request.json['_id']['$oid'])

        if self._id is None:
            self.new()
        else:
            self.load()


    def new(self):
        """ Creates a new webapp alert; initializes. """

        self.alert = request.json

        # sanity check the incoming
        for req_var in ['body','title']:
            if self.alert[req_var] is None:
                raise utils.InvalidUsage("Webapp Alert key '%s' cannot be None type!" % req_var)

        self.alert['sub_type'] = self.alert['type']
        self.alert['type'] = 'webapp_alert'
        self.alert['created_on'] = datetime.now()
        self.alert['created_by'] = ObjectId(self.alert['created_by'])
        self.alert['expired'] = False
        self.alert['release'] = utils.settings.get('api','version')
        self.alert['remote_ip'] = request.remote_addr

        # finally, save it and return it
        self.alert['_id'] = utils.mdb.notifications.insert(self.alert)

    def load(self):
        self.alert = utils.mdb.notifications.find_one({'_id': self._id})
        if self.alert is None:
            raise utils.InvalidUsage('Notification %s does not exist!' % (self._id), status_code=404)

    def expire(self):
        self.alert['expired'] = True
        self.alert['expiration'] = datetime.now()
        utils.mdb.notifications.save(self.alert)
        self.logger.warn("Expired notification %s" % self.alert['_id'])

    def serialize(self):
        """ Serialize the alert. """
        return Response(response=json.dumps(self.alert, default=json_util.default), status=200, mimetype="application/json")




