from database_defs import Profiles, Favorites
from flask_login import UserMixin
from search import create_session
from sys import stderr

def add_user(netid, is_admin, existing_session=None):
    """Adds a new user to the database
    The caller should verify/authenticate the user BEFORE calling this
    function!!
    Returns: 0 if success, 1 if failure
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        session.add(Profiles(netid=netid, is_admin=is_admin))
        session.commit()
        ret_val = 0
    except Exception as ex:
        print(ex, file=stderr)
        ret_val = 1

    if existing_session is None:
        session.close()
        engine.dispose()


    return ret_val

def remove_user(netid, existing_session=None):
    """Removes a user from the database

    Arguments:
        netid
    Returns:
        0 if successful, 1 if failure
    """

    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        (session.query(Profiles)
            .filter(Profiles.netid==netid)
            .delete())
        session.commit()

        ret_val = 0

    except Exception as ex:
        print(ex, file=stderr)
        ret_val = 1

    if existing_session is None:
        session.close()
        engine.dispose()

    return ret_val

def is_admin(netid, existing_session=None):
    """Returns True if user is admin, False if user is not an admin
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    is_admin_row = (session.query(Profiles)
                .with_entities(Profiles.is_admin)
                .filter(Profiles.netid == netid)
                .all())

    if existing_session is None:
        session.close()
        engine.dispose()

    try:
        is_admin = is_admin_row[0][0]
    except Exception:
        # if the user doesn't exist, is_admin_row[0][0] will return
        # a list index out of range error - should say False
        is_admin = False

    return is_admin

def user_exists(netid, existing_session=None):
    """Checks if a user exists in the database already
    Arguments:
        netid
    Returns:
        boolean
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    query = (session.query(Profiles)
            .filter(Profiles.netid==netid)
            .all())

    if existing_session is None:
        session.close()
        engine.dispose()

    return (len(query) != 0)

def update_admin_status(netid, new_status, existing_session=None):
    """Updates a user's admin status

    Arguments:
        netid
        new_status (boolean: True if admin, False if not)
    Returns:
        0 if succeeded, 1 if failed
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    # validate new_status
    if new_status in [True, False, 'True', 'False']:
        # update user (if exists)
        if user_exists(netid, existing_session=session):
            (session.query(Profiles)
                    .filter(Profiles.netid == netid)
                    .update({"is_admin": new_status}))
            session.commit()
            ret_val = 0
        else:
            ret_val = 1

        if existing_session is None:
            session.close()
            engine.dispose()
    else:
        ret_val = 1

    return ret_val

def list_all_users():
    """Lists all users in database

    Returns:
        list of (netid, is_admin) tuples for all users in database
    """
    engine, session = create_session()

    query = (session.query(Profiles)
            .with_entities(Profiles.netid, Profiles.is_admin)
            .all())

    session.close()
    engine.dispose()
    return query

def all_params(netid) :
    """Returns all parameters necessary for User object
    Arguments:
        netid
    Returns:
        tuple: (boolean is_admin) # only one param right now
    """
    engine, session = create_session()

    query = (session.query(Profiles)
            .filter(Profiles.netid==netid)
            .all())
    if len(query) == 0:
        add_user(netid, False, existing_session=session)

    is_admin_row = (session.query(Profiles)
                .with_entities(Profiles.is_admin)
                .filter(Profiles.netid == netid)
                .all())

    session.close()
    engine.dispose()

    is_admin = is_admin_row[0][0]

    return is_admin

# necessary user class which defines a user for Flask-login
class User(UserMixin) :
    # initialize parameters from the database
    def __init__(self, netid):
        self._netid = netid
        self._admin = is_admin(netid)

    def is_admin(self) :
        return self._admin

    # following 4 functions required for Flask-login
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the netid to satisfy Flask-Login's requirements."""
        return self._netid

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
    # add more columns as needed once we know about CAS authentication

def add_favorite(netid, route_id, existing_session=None):
    """Adds a new favorite route to the database
    The caller should verify/authenticate the user BEFORE calling this
    function!!

    Arguments: netid, route_id
    Returns: 0 if success, 1 if failure
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        session.add(Favorites(netid=netid, route_id=route_id))
        session.commit()
        ret_val = 0
    except Exception as ex:
        print(ex, file=stderr)
        ret_val = 1

    if existing_session is None:
        session.close()
        engine.dispose()

    return ret_val

def remove_favorite(netid, route_id, existing_session=None):
    """Removes a favorite route from the database

    Arguments:
        netid, route_id
    Returns:
        0 if successful, 1 if failure
    """

    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        (session.query(Favorites)
            .filter(Favorites.netid==netid)
            .filter(Favorites.route_id==route_id)
            .delete())
        session.commit()

        ret_val = 0

    except Exception as ex:
        print(ex, file=stderr)
        ret_val = 1

    if existing_session is None:
        session.close()
        engine.dispose()

    return ret_val


def main():
    # update admin status
    update_admin_status('mrapi', True)
    for user in list_all_users():
         print(user)
    # accept command-line arguments
    # if len(argv) != 3:
    #     print('usage: profile_funcs.py netid admin_val')
    #     exit(1)

    # netid = argv[1]
    # admin_bool = 'Not sure'
    # if argv[2] == 'True':
    #     admin_bool = True
    # elif argv[2] == 'False':
    #     admin_bool == False
    # else:
    #     print('could not convert admin_val to boolean')
    #     exit(1)

    # # add user if user does not already exist in database
    # print("Testing add_user with netid %s and admin_val %s"
    #                                 % (netid, str(admin_bool)))

    # engine, session = create_session()
    # if (session.query(Profiles)
    #                     .filter(Profiles.netid == netid)
    #                     .first()) is not None:
    #     print("User already exists")
    # else:
    #     add_failed = add_user(netid, True)
    #     if add_failed == 1:
    #         print("Add failed")
    #         exit(1)

    # # query database for the user (expected answer: netid admin_val)
    # print("Result of querying database for this user: ")
    # query = (session.query(Profiles)
    #                 .filter(Profiles.netid == netid)
    #                 .one())
    # print("%s %s" % (query.netid, query.is_admin))

    # print("User exists: ", user_exists(netid))

    # # test is_admin for this user
    # print("Testing is_admin for this user: ")
    # print("\tadmin_val: ", is_admin(netid))

    # # test updating the user and check admin status again
    # print("Changing admin status for this user and testing is_admin")
    # (session.query(Profiles)
    #         .filter(Profiles.netid == netid)
    #         .update({"is_admin": (not is_admin)}))
    # session.commit()

    # print("\tadmin_val: ", is_admin(netid))

    # remove the user (since this is a test)
    # print("Removing user")
    # (session.query(Profiles)
    #         .filter(Profiles.netid==netid)
    #         .delete())
    # session.commit()

    # if (session.query(Profiles)
    #             .filter(Profiles.netid==netid)
    #             .first()) is not None:
    #     print("Error removing user!")
    # else:
    #     print("User successfully removed")

    # session.close()
    # engine.dispose()

if __name__ == '__main__':
    main()