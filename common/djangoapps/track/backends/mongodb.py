from __future__ import absolute_import

import logging

import pymongo

from track.backends import BaseBackend


log = logging.getLogger('track.backends.mongo')


class MongoBackend(BaseBackend):
    def __init__(self, **options):
        super(MongoBackend, self).__init__(**options)

        # Extract connection parameters from options

        host = options.pop('host', 'localhost')
        port = options.pop('port', 27017)

        user = options.pop('user', '')
        password = options.pop('password', '')

        db_name = options.pop('database', 'track')
        collection_name = options.pop('collection', 'events')

        # By default disable write acknoledgements
        write_concern = options.pop('w', 0)

        # Connect to database and get collection

        self.connection = pymongo.connection.MongoClient(
            host=host,
            port=port,
            w=write_concern,
            tz_aware=True,
            **options)

        self.collection = self.connection[db_name][collection_name]

        if user or password:
            self.collection.database.authenticate(user, password)

        self._create_indexes()

    def _create_indexes(self):
        self.collection.create_index('event_type')
        self.collection.create_index([('time', pymongo.DESCENDING)])

    def send(self, event):
        self.collection.insert(event)
