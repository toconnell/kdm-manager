#!/usr/bin/env python

from bson.objectid import ObjectId
from flask import Response, send_file
import gridfs
from StringIO import StringIO

import utils

class image():
    """ Initialize this with a string of an mdb Object ID, and use
    the render_response() method to create an http response of the
    image. Fuck a file system: props to the immortal rschulz. """

    def __init__(self, img_id):
        try:
            img_oid = ObjectId(img_id)
        except:
            raise utils.InvalidUsage('Invalid OID! Image OIDs must be 12-byte input or 24-character hex string!', status_code=400)
        try:
            self.img = gridfs.GridFS(utils.mdb).get(img_oid)
        except gridfs.errors.NoFile:
            self.img = None

    def render_response(self):
        """ Renders an http response. """
        if self.img is None:
            return Response(response="Image not found!", status=404)
        image_file = StringIO(self.img.read())
        return send_file(image_file, mimetype="image/png")

