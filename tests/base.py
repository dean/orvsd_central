from functools import wraps
import unittest

from contextlib import contextmanager
from flask import appcontext_pushed, g

import orvsd_central
from orvsd_central.database import create_db_session
from orvsd_central.models import Model


def db_context(f):
    @wraps(f)
    def decorated(inst, *args, **kwargs):
        with database_set(inst.app):
            with inst.app.app_context():
                f(inst, *args, **kwargs)
    return decorated


@contextmanager
def database_set(app):
    def handler(sender, **kwargs):
        g.db_session = create_db_session()
    with appcontext_pushed.connected_to(handler, app):
        yield


class TestBase(unittest.TestCase):

    def setUp(self):
        """
        Create a test database in memory and a test app to be referenced as
        self.db_session and self.app respectively.
        """

        # Config modifications for testing
        db = 'sqlite:///:memory:'
        cfg = {
            'SQLALCHEMY_DATABASE_URI': db,
            'CELERY_BROKER_URL': 'sqla+' + db,
            'CELERY_RESULT_DBURI': db,
            'TESTING': True,
            'DEBUG': True
        }

        # Create the app
        self.app = orvsd_central.create_app(config_changes=cfg)
        self.app.testing = True
