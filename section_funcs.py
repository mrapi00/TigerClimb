# ----------------------------------------------------------------------
# section_funcs.py
# library for interaction with sections of the wall
# ----------------------------------------------------------------------
from sys import stderr

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database_defs import Sections, Routes
# ----------------------------------------------------------------------
engine = create_engine("postgresql://wfdogrdljlercb:1fed2ff3281e5ca8619af0c62bd99bda6e5f6dfa2e50cd41866f38b73b92ae34@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d1dgp9c53v4u0n")
Session = sessionmaker(engine)
# ----------------------------------------------------------------------

def assign_section(route_id, new_section):
    """Updates the session associated with a route in Sections, or adds
    a new row to Sections using add_route_section if new"""

    #TODO: sanitize input - what if route_id or new_section are invalid format?

    with Session() as session, session.begin():
        # get existing section/route_id rows
        existing_rows = (session.query(Sections)
                    .filter(Sections.route_id == route_id)
                    .all())

        # add row if doesn't exist
        if len(existing_rows) == 0:
            add_route_section(route_id, new_section)
        # update row with new section
        elif len(existing_rows) == 1:
            (session.query(Sections)
                    .filter(Sections.route_id == route_id)
                    .update({'section': new_section}))
        else:
            raise Exception('Database error: multiple sections per route is not allowed')
            # Note: to allow multiple sections per route, change the 'elif' line
            # to just be 'else'
            # and sqlalchemy will update all rows where route_id matches
            # the parameter given

def add_route_section(route_id, section):
    """ Adds a new route-section correspondence in the Sections table
    """

    # TODO: sanitize input - what if new_section is invalid? and is invalid route_id handling good?
    with Session() as session, session.begin():

        # raise exception if the route id does not exist
        if (session.query(Routes)
                    .filter(Routes.route_id == route_id)
                    .first()) is None:
            raise Exception("Cannot add section to non-existing route")

        # add new row
        session.add(Sections(route_id=route_id, section=section))

def get_section(route_id):
    """ Gets the section associated with a given route or None if no
    section found"""

    #TODO error handling / input sanitizing

    with Session() as session, session.begin():
        try:
            section_list = (session.query(Sections)
                                .filter(Sections.route_id == route_id)
                                .with_entities(Sections.section)
                                .all())

            if len(section_list) == 0:
                section = None
            elif len(section_list) > 1: #remove this if multiple sections allowed
                raise Exception("Database error: Multiple sections")
            else:
                section = section_list[0][0]
        except:
            section = None

    return section

def get_routes_by_section(section):
    """ Returns a list of routes associated with the given section, or
    an empty list if none found.
    """
    #TODO error handling / input sanitizing
    routes = []
    try:
        with Session() as session, session.begin():
            route_ids = (session.query(Sections)
                                .filter(Sections.section == section)
                                .with_entities(Sections.route_id)
                                .all())
            for route_id in route_ids :
                route_id = route_id[0]
                getRoute = (session.query(Routes)
                        .filter(Routes.route_id == route_id)
                        .with_entities(Routes.name, Routes.route_id, Routes.grade, Routes.rope)
                        .first())
                routes.append(getRoute)
    except Exception as ex:
        print("error in get_routes_by_section: ", str(ex), file=stderr)

    return routes

def get_routeid_by_name(name):
    """Returns the route id of a route given its name.
    Sanitize name input before calling this function.

    Returns None in case of error or if nothing found.
    """
    try:
        with Session() as session, session.begin():
            route_id = (session.query(Routes)
                                .filter(Routes.name == name)
                                .with_entities(Routes.route_id)
                                .first())
            if route_id is not None:
                route_id = route_id[0]
    except Exception as ex:
        print("error in get_routeid_by_name: "+ str(ex), file=stderr)
        route_id = None

    return route_id


def _test():
    # Test get_routeid_by_name
    name = "Women in STEM"
    routeid = get_routeid_by_name(name)
    print("routeid for name %s: %d" % (name, routeid))

    # Test get_routes_by_section
    section = "right_crack"
    print("routes on section %s: " % section)
    print(get_routes_by_section(section))

    # Test get_section
    print("section of %s: %s" % (name, get_section(routeid)))

    # Test assign_section (and then undo the change)
    new_section = 'the_roof'
    print("assign section %s to %s" % (new_section, name))
    assign_section(routeid, new_section)

    print("section of %s: %s" % (name, get_section(routeid)))

    print("assign section %s to %s" % (section, name))
    assign_section(routeid, section)

    print("section of %s: %s" % (name, get_section(routeid)))

    #TODO: test "add_route_section" without breaking anything

if __name__ == '__main__':
    _test()