#!/usr/bin/env python


#
#   The only thing that should be in this file are model dictionaries:
#   any logic, procesing, etc. happens elsewhere
#

users = {
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
    'cache_control': '',    # disable caching for this endpoint because we don't
    'cache_expires': 0,     # want the browser to cache user info, I think.
    "schema": {
        'active': {'type': 'boolean'},
        'created_on': {'type': 'datetime'},
        'login': {
            'type': 'string',
            'minlength': 5,
            'maxlength': 255,
            'required': True,
            'unique': True,
        },
        'password': {
            'type': 'string',
            'required': True,
        },
        'role': {
            'type': 'list',
            'allowed': ["user", "admin"],
        },
        'preferences': {'type': 'dict'},
        'user_agents': {'type': 'list'},
    },
}
