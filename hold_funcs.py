# ----------------------------------------------------------------------
# hold_funcs.py
# library for dealing with holds in tigerclimb
# ----------------------------------------------------------------------
from sys import stderr

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_defs import Holds, RouteCoords, Routes
# ----------------------------------------------------------------------
engine = create_engine("postgresql://wfdogrdljlercb:1fed2ff3281e5ca8619af0c62bd99bda6e5f6dfa2e50cd41866f38b73b92ae34@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d1dgp9c53v4u0n")
Session = sessionmaker(engine)
# ----------------------------------------------------------------------
def add_hold(x, y, status, size, hold_type, section):
    """Adds a new hold to the Holds database. Does not allow two holds
    to be in the same place (x, y, section).
    """
    #TODO: How to do error handling here? Return?

    with Session() as session, session.begin():
        # find the largest hold_id in database
        try:
            max_id = (session.query(Holds)
                .with_entities(Holds.hold_id)
                .order_by(Holds.hold_id.desc())
                .first())[0]
        except: # empty database
            max_id = 0

        # disallow duplicate holds (by coordinate)
        if get_id_by_coord(x, y, section) != None:
            raise Exception("Cannot create hold in duplicate location.")

        # assign new hold id and create new hold
        new_hold = Holds(hold_id=(max_id+1), x=x, y=y, status=status,
        size=size, hold_type=hold_type, section=section)

        session.add(new_hold)

# ----------------------------------------------------------------------
# functions that update database "by coordinate"
# ----------------------------------------------------------------------
def remove_hold_by_coord(x, y, section):
    """Removes a hold from view (changes status to 'down') given x- and
    y-coordinates and a section.
    Only removes holds that are not part of any active (status=up)
    routes.
    """
    #TODO: Error handling. What if get_id_by_coord doesn't find anything?
    remove_hold_by_id(get_id_by_coord(x, y, section))

def delete_hold_by_coord(x, y, section):
    """Given coordinates, deletes the hold from the Holds database and from
    all relevant rows of RouteCoords.
    """

    hold_id = get_id_by_coord(x, y, section)
    delete_hold_by_id(hold_id)

def connect_hold_by_coord(x, y, section, route_id):
    """Connects a hold (existing) to a route_id
    """
    hold_id = get_id_by_coord(x, y, section)
    connect_hold_by_id(hold_id, route_id)

def disconnect_hold_by_coord(x, y, section, route_id):
    """Removes a hold from a specific route, while leaving the hold
    status unchanged.
    """
    hold_id = get_id_by_coord(x, y, section)
    disconnect_hold_by_id(hold_id, route_id)

def update_size(x, y, section, new_size):
    """Updates the size of a hold given x, y, section and new_size
    """
    #TODO: Error handling
    update_by_coord(x, y, section, 'size', new_size)

def update_type(x, y, section, new_type):
    """Updates the type of a hold given x, y, section and new_type
    """
    #TODO: Error handling
    update_by_coord(x, y, section, 'hold_type', new_type)

def update_by_coord(x, y, section, update_key, update_val):
    """Updates the update_key of a hold (identified by x, y, section)
    to be the update_val. Only updates one field at a time. Will not
    update x, y, section, or hold_id.
    """
    #TODO: Error handling

    hold_id = get_id_by_coord(x, y, section)

    if update_key in ['x', 'y', 'section', 'hold_id']:
        raise Exception("hold_id, x, y, section cannot be updated")

    with Session() as session, session.begin():
        (session.query(Holds)
                .filter(Holds.hold_id == hold_id)
                .update({update_key: update_val}))
# ----------------------------------------------------------------------
# functions that update database "by id"
# ----------------------------------------------------------------------
def remove_hold_by_id(hold_id):
    """Removes a hold from view (changes status to 'down') given an ID.
    Only removes holds that are not part of any active (status=up)
    routes.
    """
    #TODO: How to do error handling?

    with Session() as session, session.begin():
        # check that all routes associated have status down
        route_ids = (session.query(RouteCoords)
                            .with_entities(RouteCoords.route_id)
                            .filter(RouteCoords.hold_id == hold_id)
                            .all())
        route_statuses = (session.query(Routes)
                                .with_entities(Routes.status)
                                .filter(Routes.route_id.in_(route_ids))
                                .all())
        for status in route_statuses:
            if status[0] != 'down':
                raise Exception("Error: Cannot remove holds from active routes")

        # update the hold to have status down
        (session.query(Holds)
                .filter(Holds.hold_id == hold_id)
                .update({'status': 'down'}))

def delete_hold_by_id(hold_id):
    """Given hold_id, deletes the hold from the Holds database and from
    all relevant rows of RouteCoords.
    Returns the deleted hold id, or None if none found.
    """

    with Session() as session, session.begin():
        # delete from Holds
        (session.query(Holds)
                .filter(Holds.hold_id == hold_id)
                .delete())

        # delete from RouteCoords
        (session.query(RouteCoords)
                .filter(RouteCoords.hold_id == hold_id)
                .delete())

def connect_hold_by_id(hold_id, route_id):
    """Given a hold_id and route_id, adds hold to associated route
    Existing holds only
    """
    with Session() as session, session.begin():
        hold_list = (session.query(Holds)
                        .filter(Holds.hold_id == hold_id)
                        .all())

        if len(hold_list) == 0:
            raise Exception("No such hold in database")
        elif len(hold_list) != 1:
            raise Exception("Database error. Contact administrator.")
        else:
            route_hold = RouteCoords(route_id=route_id, hold_id=hold_id)
            session.add(route_hold)

def disconnect_hold_by_id(hold_id, route_id):
    """Given a hold_id and route_id, removes hold from being associated
    with route without changing hold or route status.
    """
    #TODO: Error handling

    with Session() as session, session.begin():
        row = (session.query(RouteCoords)
                .filter(RouteCoords.route_id == route_id)
                .filter(RouteCoords.hold_id == hold_id)
                .one())

        session.delete(row)

# ----------------------------------------------------------------------
# "getter" functions - fetch information from database
# ----------------------------------------------------------------------
def get_id_by_coord(x, y, section):
    """Helper function to get a hold_id given location (x, y, section)
    """

    with Session() as session, session.begin():
        hold_id = (session.query(Holds)
                            .with_entities(Holds.hold_id)
                            .filter((((Holds.x - x) <= 1.0) & ((Holds.x - x) >= 0.0)) | (((x - Holds.x) <= 1.0) & ((x - Holds.x) >= 0.0)))
                            .filter((((Holds.y - y) <= 1.0) & ((Holds.y - y) >= 0.0)) | (((y - Holds.y) <= 1.0) & ((y - Holds.y) >= 0.0)))
                            .filter(Holds.section == section)
                            .all())

        if len(hold_id) == 0:
            return None
        elif len(hold_id) != 1:
            raise Exception("Database error. Please contact administrator.")
        else:
            return hold_id[0][0]

def get_routes_by_coord(x, y, section):
    """Given a hold location (x, y, section) returns a list of route_ids
    of all routes that use that hold.
    """
    #TODO: Error handling
    hold_id = get_id_by_coord(x, y, section)
    return get_routes_by_id(hold_id)

def get_routes_by_id(hold_id):
    """Gets a list of route_ids associated with a given hold_id, or
    empty list in case of error or no match.
    """
    #TODO: Error handling

    with Session() as session, session.begin():
        try:
            routes = (session.query(RouteCoords)
                    .filter(RouteCoords.hold_id == hold_id)
                    .with_entities(RouteCoords.route_id)
                    .all())
            routes = [route[0] for route in routes] # want array of ints, not tuples
        except Exception as ex:
            print(ex, file=stderr)
            routes = []

    return routes

def get_all_holds():
    """For debugging - gets all holds
    Returns a list of tuples: (hold_id, x, y, section, status, size, type)
    ordered by hold_id
    """
    with Session() as session, session.begin():
        holds = (session.query(Holds)
                        .with_entities(Holds.hold_id, Holds.x, Holds.y,
                        Holds.section, Holds.status, Holds.size,
                        Holds.hold_type)
                        .order_by(Holds.hold_id)
                        .all())

    return holds

def get_holds_by_section(section):
    """Given a section name, get a list of (x, y, hold_id) tuples for
    holds associated with that route_id. Empty list if no match or error.
    """
    with Session() as session, session.begin():
        try:
            hold_locs = (session.query(Holds)
                                .with_entities(Holds.x, Holds.y, Holds.hold_id)
                                .filter(Holds.section == section)
                                .all())
        except:
            hold_locs = []
        return hold_locs

def get_hold_locs_by_route(route_id):
    """ Given a route_id, get a list of (x, y, section) tuples for hold
    associated with that route_id. Returns empty list if no match or error.
    """
    with Session() as session, session.begin():
        try:
            hold_ids = get_holds_by_route(route_id)
            hold_locs = (session.query(Holds)
                        .with_entities(Holds.x, Holds.y, Holds.section)
                        .filter(Holds.hold_id.in_(hold_ids))
                        .all())
        except:
            hold_locs = []

        return hold_locs

def get_holds_by_route(route_id):
    """Given a route_id, get all hold_ids associated with that route_id
    Returns empty list if no match or if error occurs.
    """
    with Session() as session, session.begin():
        try:
            holds = (session.query(RouteCoords)
                            .with_entities(RouteCoords.hold_id)
                            .filter(RouteCoords.route_id == route_id)
                            .all())
            holds = [hold[0] for hold in holds] # array of hold_ids, not tuples
        except Exception as ex:
            print(ex)
            holds = []

    return holds
# ----------------------------------------------------------------------
# helpers for testing
# ----------------------------------------------------------------------
def _delete_test_holds():
    """ For debugging - deletes all holds with type 'test'
    """
    with Session() as session, session.begin():
        holds = (session.query(Holds)
                        .filter(Holds.hold_type == 'test')
                        .delete())

def _test():
    x = 2
    y = 3
    status = 'up'
    size= 1
    hold_type = 'foo'
    section = 'test'

    def hold_exists(x, y, section):
        with Session() as session, session.begin():
            hold = (session.query(Holds)
                            .filter(Holds.x == x)
                            .filter(Holds.y == y)
                            .filter(Holds.section == section)
                            .all())
        return len(hold) != 0

    def hold_status(x, y, section):
        with Session() as session, session.begin():
            status = (session.query(Holds)
            .filter(Holds.x==x).filter(Holds.y==y)
            .filter(Holds.section==section)
            .with_entities(Holds.status)
            .all())
        return status[0][0]

    def hold_size(x, y, section):
        with Session() as session, session.begin():
            size = (session.query(Holds)
            .filter(Holds.x==x).filter(Holds.y==y)
            .filter(Holds.section==section)
            .with_entities(Holds.size)
            .all())
        return size[0][0]

    def get_hold_type(x, y, section):
        with Session() as session, session.begin():
            hold_type = (session.query(Holds)
            .filter(Holds.x==x).filter(Holds.y==y)
            .filter(Holds.section==section)
            .with_entities(Holds.hold_type)
            .all())
        return hold_type[0][0]

    # print the status before adding the hold
    print("holds with 10 largest hold ids: ")
    print(get_all_holds()[-10:])

    print("hold exists: " + str(hold_exists(x,y,section)))

    # add the hold
    print("adding hold")
    add_hold(x,y,status,size,str(hold_type),section)

    try:
        # print the status now; test some getterfunctions
        print("hold exists: " + str(hold_exists(x,y,section)))
        hold_id = get_id_by_coord(x, y, section)
        print("hold id: %d" % hold_id)
        print("all holds in " + section + " section: ")
        print(get_holds_by_section(section))

        # test some update functions not having to do with routes
        print(hold_status(x,y,section))
        print("hold status: " + hold_status(x, y, section))

        print("removing hold (status down)")
        remove_hold_by_coord(x, y, section)

        print("hold status: " + hold_status(x, y, section))

        print("updating status")
        update_by_coord(x, y, section, 'status', 'up')
        print("hold status: " + hold_status(x, y, section))

        print("updating size (current size: " + str(hold_size(x, y, section)) + ")")
        update_size(x, y, section, 2)
        print("new hold size: " + str(hold_size(x, y, section)) + ")")

        print("updating type (current size: " + str(get_hold_type(x, y, section)) + ")")
        update_type(x, y, section, 'test2')
        print("new hold type: " + str(get_hold_type(x, y, section)) + ")")
        update_type(x, y, section, 'test')

        # test the update and getter functions relating to routes
        def is_connected(x, y, section, route_id):
            hold_id = get_id_by_coord(x, y, section)

            with Session() as session, session.begin():
                rows = (session.query(RouteCoords)
                        .filter(RouteCoords.hold_id == hold_id)
                        .filter(RouteCoords.route_id == route_id)
                        .all())

            return len(rows) != 0

        route_id = 1
        print("hold is currently connected to route %d: %s" % (route_id, str(is_connected(x,y,section,route_id))))

        print("connecting hold")
        connect_hold_by_coord(x, y, section, route_id)

        print("hold is currently connected to route %d: %s" % (route_id, str(is_connected(x,y,section,route_id))))

        print("routes this hold is connected to: ")
        print(get_routes_by_coord(x, y, section))

        print("holds on route %d:" % route_id)
        print(get_holds_by_route(route_id))
        print(get_hold_locs_by_route(route_id))

        print("disconnecting hold")
        disconnect_hold_by_coord(x, y, section, route_id)

        print("hold is currently connected to route %d: %s" % (route_id, str(is_connected(x,y,section,route_id))))

        print("routes this hold is connected to: ")
        print(get_routes_by_coord(x, y, section))

        print("holds on route %d:" % route_id)
        print(get_holds_by_route(route_id))
        print(get_hold_locs_by_route(route_id))

        print("deleting hold")
        delete_hold_by_id(hold_id)
        print("hold exists: " + str(hold_exists(x,y,section)))
        print("holds on route %d:" % route_id)
        print(get_holds_by_route(route_id))
        print(get_hold_locs_by_route(route_id))

        print("done")
    except Exception as ex:
        print("exception")
        print(ex)
        delete_hold_by_id(get_id_by_coord(x, y, section))

if __name__ == '__main__':
    _test()