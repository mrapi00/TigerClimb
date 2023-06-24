from search import create_session
from database_defs import Routes, Holds, RouteCoords, RouteEdits, Sections
from database_defs import Comments, Favorites
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sys import stderr
from datetime import datetime

engine = create_engine("postgresql://wfdogrdljlercb:1fed2ff3281e5ca8619af0c62bd99bda6e5f6dfa2e50cd41866f38b73b92ae34@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d1dgp9c53v4u0n")
Session = sessionmaker(engine)

# ----------------------------------------------------------------------
# Functions for dealing with routes directly
# ----------------------------------------------------------------------
def add_route(name=None, grade=None, consensus_grade=0, tape_col=None,
            tape_col2="", date_created=None, descrip=None, status=None, rope=0, route_type="",
            existing_session = None):
    """Adds a new route to the database
    The caller should verify/authenticate the user BEFORE calling this
    function!!
    Arguments: route_id, name, grade, consensus_grade, tape_col,
    tape_col2, date_created, descrip, status, rope, route_type
    Returns: 0 if success, 1 if failure
    """
    print("in the first add route")
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    ret_val = 0
    try:
        if isinstance(date_created, str) :
            format_str = '%Y-%m-%d' # The format
            date_created = datetime.strptime(date_created, format_str)
            print(date_created)

        session.add(Routes(name=name, grade=grade,
                            consensus_grade=consensus_grade,
                            tape_col=tape_col, tape_col2=tape_col2,
                            date_created=date_created, descrip=descrip,
                            status=status, rope=rope,
                            route_type=route_type))
        session.add(RouteEdits(version=0, netid='dw26'))
        session.commit()
    except Exception as ex:
        print(ex, file=stderr)
        ret_val = 1

    if existing_session is None:
        session.close()
        engine.dispose()

    return ret_val

# def add_route(route_id, name, grade, consensus_grade, tape_col, tape_col2, date_created, descrip, status, rope, route_type):
#     """An alternative, older method of adding a route; deprecated
#     """
#     print("in the deprecated add route")
#     #TODO: what shoudl be optional in args?

#     engine, session = create_session()

#     #TODO: verify input here
#     #TODO: sanitize
#     new_route = Routes(route_id=route_id, name=name, grade=grade,
#     consensus_grade=consensus_grade, tape_col=tape_col,
#     tape_col2=tape_col2, date_created=date_created, descrip=descrip,
#     status=status, rope=rope, route_type=route_type)

#     session.add(new_route)
#     session.commit()

#     session.close()
#     engine.dispose()

def update_route(route_id, name, grade, tape_col,
            date_created, descrip, status, rope,
            route_type = None,
            consensus_grade = None,
            tape_col2 = None,
            existing_session = None):
    """Edits a route in the database
    The caller should verify/authenticate the user BEFORE calling this
    function!!
    Arguments: route_id, name, grade, consensus_grade, tape_col,
    tape_col2, date_created, descrip, status, rope, route_type
    Returns: 0 if success, 1 if failure
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        # convert date_created to Date object
        if isinstance(date_created, str) :
            format_str = '%Y-%m-%d' # The format
            date_created = datetime.strptime(date_created, format_str)
            print(date_created)

        (session.query(Routes).filter(Routes.route_id == route_id).
            update({'route_id':route_id,
                    'name':name,
                    'grade':grade,
                    #{'consensus_grade':consensus_grade},
                    'tape_col':tape_col,
                    #{'tape_col2':tape_col2},
                    'date_created':date_created, # need to be careful with date object, ignore for now
                    'descrip':descrip,
                    'status':status,
                    #{'route_type':route_type},
                    'rope':rope})
                    )
        session.query(RouteEdits).filter(RouteEdits.route_id==route_id).update({'route_id':route_id, 'netid':'dw26'})

        # old_time = session.query(RouteEdits).with_entities(Routes.route_id).filter(Routes.route_id == route_id)[0]
        # if old_time > func.now():
        #   throw exception
        session.commit()
        ret_val = 0
    except Exception as ex:
        print(ex, file=stderr)
        ret_val = 1

    if existing_session is None:
        session.close()
        engine.dispose()

    return ret_val

def delete_route(route_id):
    """Deletes a route in the database and all associated information:
            comments, unique holds, hold id/route id associations,
            favorites, route-section association.
        Don't use this to take something down - this is a full delete.
        Authenticate users FIRST.

        Arguments: route_id
    """
    try:
        with Session() as session, session.begin():
            # delete the route itself
            num_routes = (session.query(Routes)
                    .filter(Routes.route_id == route_id)
                    .delete())

            # delete comments
            try:
                num_comments = (session.query(Comments)
                    .filter(Comments.route_id == route_id)
                    .delete())
            except:
                num_comments = 0

            # delete all unique holds
            hold_ids = (session.query(RouteCoords)
                                .filter(RouteCoords.route_id == route_id)
                                .with_entities(RouteCoords.hold_id)
                                .all())

            num_holds = 0
            for hold_id in hold_ids:
                hold_id = hold_id[0]
                routes = (session.query(RouteCoords)
                                .filter(RouteCoords.hold_id == hold_id)
                                .with_entities(RouteCoords.route_id)
                                .all())

                if len(routes) == 1:
                    try:
                        num_holds += (session.query(Holds)
                            .filter(Holds.hold_id == hold_id)
                            .delete())
                    except:
                        num_holds += 0


            # delete hold id / route id associations
            try:
                num_routecoords = (session.query(RouteCoords)
                    .filter(RouteCoords.route_id == route_id)
                    .delete())
            except:
                num_routecoords = 0

            # delete favorites
            try:
                num_favorites = (session.query(Favorites)
                    .filter(Favorites.route_id == route_id)
                    .delete())
            except:
                num_favorites = 0

            # delete route section association
            try:
                num_sections = (session.query(Sections)
                                    .filter(Sections.route_id == route_id)
                                    .delete())
            except:
                num_sections = 0

            print("Deleted: \n%d routes \n%d comments \n%d holds "
                        "\n%d routecoords \n%d favorites \n%d sections"
                        % (num_routes, num_comments, num_holds, num_routecoords, num_favorites, num_sections))

    except Exception as ex:
        print("exception in delete_route: " + str(ex), file=stderr)
        raise Exception("failed to delete")

# ----------------------------------------------------------------------
# Functions for getting route details
# ----------------------------------------------------------------------

def get_rope_by_route(route_id):
    """ Returns the rope number (integer) associated with the route,
    or None if nothing matching found.
    """
    # TODO error handling?

    with Session() as session, session.begin():
        try:
            rope = (session.query(Routes)
                            .filter(Routes.route_id == route_id)
                            .with_entities(Routes.rope)
                            .first())[0]
        except Exception as ex:
            print("error in get_rope_by_route " + str(ex), file=stderr)
            rope = None

    return rope

def get_rope_list(route_list):
    """ Given a list of route_ids, returns the set of ropes associated
    with the routes listed. No duplicate ropes will be returned.
    Empty set if none found.
    """
    ropes = set()
    for route in route_list:
        curr_rope = get_rope_by_route(route)
        if curr_rope is not None:
            ropes.add(curr_rope)

    return ropes

def get_all_routeids(in_order=False):
    """Returns the list of routeids (integers) currently in the database
    """
    with Session() as session, session.begin():
        rids = session.query(Routes).with_entities(Routes.route_id).all()

        rids = [rid[0] for rid in rids]

    return rids

def get_tape_col(route_id):
    """ Returns the tape color (string) associated with the route,
    or None if nothing matching found.
    """
    # TODO error handling?

    with Session() as session, session.begin():
        tape_col = (session.query(Routes)
                .filter(Routes.route_id == route_id)
                .with_entities(Routes.tape_col)
                .first())[0]
    return tape_col

def get_maxid() :
    """Gets maxid of a route (used for generating random route feature)
    Arguments: None
    Returns: max route_id (int)
    """
    try:
        engine, session = create_session()
        max_id = (session.query(Routes).with_entities(Routes.route_id).
                order_by(Routes.route_id.desc()).first())[0]

        return max_id
    except Exception as ex:
        print(ex, file=stderr)
    finally:
        session.close()
        engine.dispose()

def last_edit(route_id, existing_session = None):
    """Gets time of last edit of a route in the database
    Arguments: route_id
    Returns: timestamp
    """
    time_updated = None
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        query = session.query(RouteEdits).filter(RouteEdits.route_id == route_id).with_entities(RouteEdits.time_updated, RouteEdits.version)
        time_updated = query.all()
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        if existing_session is None:
            session.close()
            engine.dispose()

    return time_updated


# ------ test ----
def _test():
    print(get_all_routeids())
    # try:
    #     with Session() as s1, s1.begin():
    #         print('adding necessary info')
    #         maxid = get_maxid()
    #         rid = maxid+1
    #         new_route = Routes(route_id=rid, name='test', grade=5.1, consensus_grade=5.1, tape_col='test', tape_col2='test', date_created='05/29/2001', status='up', rope=3, route_type='test')
    #         s1.add(new_route)

    #         new_comment = Comments(route_id=rid, netid='rivkam', comment='test', public=True)
    #         s1.add(new_comment)

    #         try:
    #             add_hold(1,2,'up',1,'default','test')
    #         except:
    #             print('duplicate hold')
    #         try:
    #             add_hold(1,7,'up',1,'default','test')
    #         except:
    #             print('duplicate hold')
    #         try:
    #             add_hold(1,9,'up',1,'default','test')
    #         except:
    #             print('duplicate hold')

    #         s1.commit()

    #         connect_hold_by_coord(1,2,'test',rid)
    #         connect_hold_by_coord(1,7,'test',rid)
    #         connect_hold_by_coord(1,9,'test',rid)

    #         add_favorite('rivkam', rid)

    #         assign_section(rid, 'the_roof')

    #     print('exited with')
    # except:
    #     print('exception in wrapper')

    # with Session() as s2, s2.begin():
    #     print(s2.query(Routes).filter(Routes.route_id == rid).all())
    #     print(s2.query(RouteCoords).filter(RouteCoords.route_id == rid).all())
    #     print(s2.query(Comments).filter(Comments.route_id == rid).all())
    #     print(s2.query(Favorites).filter(Favorites.route_id == rid).all())
    #     print(s2.query(Sections).filter(Sections.route_id == rid).all())

    # delete_route(rid)

    # delete_hold_by_coord(1,2,'test')
    # delete_hold_by_coord(1,7,'test')
    # delete_hold_by_coord(1,9,'test')

    # with Session() as session, session.begin():
    #     print(session.query(Routes).filter(Routes.route_id == rid).all())
    #     print(session.query(RouteCoords).filter(RouteCoords.route_id == rid).all())
    #     print(session.query(Comments).filter(Comments.route_id == rid).all())
    #     print(session.query(Favorites).filter(Favorites.route_id == rid).all())
    #     print(session.query(Sections).filter(Sections.route_id == rid).all())

    # x = 3
    # y = 7
    # section = 'test'
    # size = 2

    # print("Before add")
    # with Session() as session, session.begin():
    #     print(session.query(Holds).with_entities(Holds.x, Holds.y, Holds.section).filter(Holds.x == x).order_by(Holds.x).all())

    # add_hold(x, y, 'up', size, 'default', section)

    # print("added")
    # with Session() as session, session.begin():
    #     print(session.query(Holds).with_entities(Holds.x, Holds.y, Holds.section).filter(Holds.x == x).order_by(Holds.x).all())

    # delete_hold_by_coord(x, y, section)

    # print("deleted")
    # with Session() as session, session.begin():
    #     print(session.query(Holds).with_entities(Holds.x, Holds.y, Holds.section).filter(Holds.x == x).order_by(Holds.x).all())

    # names = ["A Dream of Spring", "foo", "Test"]
    # for name in names:
    #     print("Testing get_routeid_by_name with name %s: %s"
    #                                 % (name, str(get_routeid_by_name(name))))
    # # print the current holds
    # print("Holds initially in database:")
    # holds = get_all_holds()
    # print(holds)

    # # add a hold and show all holds
    # print("Adding new hold")
    # x = 1
    # y = 3
    # section = 'test3'
    # add_hold(x, y, 'up', 1, 'test', section)
    # holds = get_all_holds()
    # print(holds)

    # # remove that hold and show all holds
    # print("Removed new hold")
    # remove_hold_by_coord(x, y, section)
    # holds = get_all_holds()
    # print(holds)

    # # add a hold and connect it
    # print("Adding new hold")
    # x += 1
    # section = 'test4'
    # add_hold(x, y, 'up', 1, 'test', section)

    # holds = get_all_holds()
    # print(holds)

    # route = 3
    # connect_hold_by_coord(x, y, section, route)

    # # show that it's connected
    # print("Connecting to new route")
    # result = get_holds_by_route(route)
    # print("Holds associated with route " + str(route) + ": ")
    # print(result)

    # # update type
    # print("Updating type")
    # update_type(x, y, section, 'test3')
    # holds = get_all_holds()
    # print(holds)

    # update_type(x, y, section, 'test')

    # # update size
    # print("Updating size")
    # update_size(x, y, section, 4)
    # holds = get_all_holds()
    # print(holds)

    # # get holds by route for other route
    # print("Get holds by route for other route type")
    # route = 4
    # result = get_holds_by_route(route)
    # print("Holds associated with route " + str(route) + ": ")
    # print(result)

    # # get hold locs ditto
    # print("Get hold locations for correct route")
    # route = 3
    # result = get_hold_locs_by_route(route)
    # print("Hold locs associated with route " + str(route) + ": ")
    # print(result)

    # print("Get hold locations for other routes")
    # route = 4
    # result = get_hold_locs_by_route(route)
    # print("Hold locs associated with route " + str(route) + ": ")
    # print(result)

    # # disconnect it and show that it's not connected
    # print("Disconnecting hold")
    # disconnect_hold_by_coord(x, y, section, 3)

    # route = 3
    # result = get_holds_by_route(route)
    # print("Holds associated with route " + str(route) + ": ")
    # print(result)

    # # remove the final test hold
    # print("Deleting test holds")
    # delete_test_holds()
    # holds = get_all_holds()
    # print(holds)

if __name__ == '__main__':
    _test()