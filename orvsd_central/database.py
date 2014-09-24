import os

from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func

from orvsd_central.database_validation import *
from orvsd_central.models import Model, User
from orvsd_central.constants import USER_PERMS

def create_db_session():
    # Get the db address from the current app
    _db_address = current_app.config['SQLALCHEMY_DATABASE_URI']

    engine = create_engine(_db_address, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Model.query = db_session.query_property()
    return db_session


def create_admin_account(silent):
    """
    Create an admin account. This con be done via raw input from the user or
    through config variables

    config: Bool - use config vars
    """

    if not silent:
        # make sure the role is defined
        admin_role = USER_PERMS.get('admin')
        if not admin_role:
            raise ValueError, "admin key needed in constants.USER_PERMS"

        # get the number of admins
        admin_list = engine.                     \
                     query(func.count('*')).     \
                     select_from(User).          \
                     filter_by(role=admin_role). \
                     scalar()

        #User.query().filter_by(role=admin_role).all()

        if admin_list == 0:
            print("There are currently no admin accounts.")

        ans = raw_input("Would you like to create an admin account? (Y/N) ")
        if not ans.lower().startswith("y"):
            return

        # Proceed to making the admin user.
        username = get_valid_username()
        email = get_valid_email()
        password = get_matching_passwords()
    else:
        username = os.getenv('CENTRAL_ADMIN_USERNAME', 'admin')
        password = os.getenv('CENTRAL_ADMIN_PASSWORD', 'admin')
        email = os.getenv('CENTRAL_ADMIN_EMAIL', 'example@example.com')

    admin = User (
        name=username,
        email=email,
        password=password,
        role=admin_role
    )

    g.db_session.add(admin)
    g.db_session.commit()

    print "Administrator account created!"


def init_db():
    engine = g.db_session.get_bind()
    from orvsd_central import models
    Model.metadata.create_all(bind=engine)
