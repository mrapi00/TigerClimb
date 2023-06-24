#-----------------------------------------------------------------------
# search.py
# Defines database query functions using SQLAlchemy.
#-----------------------------------------------------------------------
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_defs import Routes, Favorites
from sys import stderr, exit
import datetime
#-----------------------------------------------------------------------
engine = create_engine("postgresql://wfdogrdljlercb:1fed2ff3281e5ca8619af0c62bd99bda6e5f6dfa2e50cd41866f38b73b92ae34@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d1dgp9c53v4u0n")
Session = sessionmaker(engine)

def get_routeids_set():
    """Returns the set of routeids (integers) currently in the database
    """
    with Session() as session, session.begin():
        rids = session.query(Routes).with_entities(Routes.route_id).all()

        rids_set = set()
        for rid in rids:
            rids_set.add(rid[0])

    return rids_set

def create_session():
    """Returns a session and an engine connected to Heroku DB
    Hides the details of SQLAlchemy session/engine creation. It is the
    job of the caller to close the session and the engine.
    """
    db_string = "postgresql://wfdogrdljlercb:1fed2ff3281e5ca8619af0c62bd99bda6e5f6dfa2e50cd41866f38b73b92ae34@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d1dgp9c53v4u0n"
    try:
        # create engine, sessionmaker, and session = SQLAlchemy stuff
        engine = create_engine(db_string)
        Session = sessionmaker(engine)
        session = Session()
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

    return engine, session

def search(name = None, min_grade = None, max_grade = None,
            min_date = None, max_date = None, status = None,
            rope_list = None, type_list = None, route_id_list = None,
            sortby='name', existing_session = None,
            return_args_list = ['route_id', 'name', 'grade', 'rope']):
    """Queries database for search results matching a given query.
    Arguments: Dictionary of parameters containing:
        name (string the name contains, or '' if none entered)
        min_grade (inclusive)
        max_grade (inclusive)
        min_date (inclusive)
        max_date (inclusive)
        status (up, in_progress, down, or '' if none specified)
        rope_list (all acceptable ropes)
        type_list (all acceptable types)
        route_id_list
        return_args_list string list of features to return: 'route_id',
        'name', 'grade', 'consensus_grade', 'tape_col', 'tape_col2',
        'date_created', 'descrip', 'status', 'rope', 'route_type'.
        default set to return 'route_id', 'name', 'grade', and 'rope'
    This means you can search by: contains <name>, grade range, date
    range, status, rope (list or range), type (list).
    Returns:
        results: list of (route_id, name, grade, rope) tuples matching
                query parameters
    """

    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        # query Routes for information matching parameters
        query = session.query(Routes)

        select_cols = [getattr(Routes, i) for i in return_args_list]
        query = query.with_entities(*tuple(select_cols))

        if name != None:
            query = query.filter(Routes.name.ilike('%' + name.replace('/','//')
                                 .replace('%', '/%').replace('_', '/_')  + '%',
                                 escape="/")) # LIKE name
        if min_grade != None:
            query = query.filter(Routes.grade>= min_grade) # min grade
        if max_grade != None:
            query = query.filter(Routes.grade <= max_grade) # max grade
        if min_date != None:
            query = query.filter(Routes.date_created >= min_date) # min date
        if max_date != None:
            query = query.filter(Routes.date_created <= max_date) # max date
        if status != None:
            query = query.filter(Routes.status.ilike('%' + status + '%')) # LIKE status
        if rope_list != None:
            query = query.filter(Routes.rope.in_(rope_list)) # IN rope_list
        if type_list != None:
            query = query.filter(Routes.route_type.in_(type_list)) # IN type_list
        if route_id_list != None:
            query = query.filter(Routes.route_id.in_(route_id_list)) # IN type_list


        if sortby == 'name':
            query = query.order_by(Routes.name.asc())
        elif sortby == 'grade':
            query = query.order_by(Routes.grade.asc())
        elif sortby == 'rope':
            query = query.order_by(Routes.rope.asc())
        else:
            query = query.order_by(Routes.grade.asc())
            #print("Other sort types are unimplemented", file=stderr)

        results = query.all() # cursor.fetchall() equivalent

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        if existing_session is None:
            session.close()
            engine.dispose()

    return results

def details_query(route_id):
    """Queries database for details of given route id for secondary page
    Arguments:
        route_id (int)
    Returns:
        details TODO:type
    """

    try:

        route_id = int(route_id)
        allids = get_routeids_set()
        if route_id not in allids:
            raise Exception('Outside of range')
        with Session() as session, session.begin():
            # query Routes for the information associated with that route_id
            details = (session.query(Routes)
                .filter(Routes.route_id == route_id)
                .all())
            details = details[0]
            ret = {'routeid': details.route_id, 'name': details.name,
            'grade' : details.grade,
            'tape_col' : details.tape_col, 'rope' : details.rope,
            'status': details.status, 'date_created': details.date_created,
            'descrip' : details.descrip}
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

    return ret

# ----- favorites searching -----

def favoritesToName(netid) :
    engine, session = create_session()
    favoriteList = favorites(netid, existing_session=session)
    routeids = []
    for favorite in favoriteList:
        routeids.append(favorite.route_id)
    favoriteList = search(route_id_list = routeids,
                            return_args_list=['name', 'route_id'],
                            existing_session=session)
    session.close()
    engine.dispose()

    return favoriteList

def favorites(netid = None, route_id = None,
                return_args_list = ['route_id'],
                existing_session=None):
    """Queries favorites table for favorite route_id's of given netid
    Arguments:
        netid (string)
        route_id (int)
        return_args_list string list of features to return: 'netid',
        'route_id'
    Returns:
        list of Favorites objects that match querries
    """

    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    try:
        query = session.query(Favorites)
        select_cols = [getattr(Favorites, i) for i in return_args_list]
        query = query.with_entities(*tuple(select_cols))

        if netid is not None:
            query = query.filter(Favorites.netid == netid)
        if route_id is not None:
            query = query.filter(Favorites.route_id == route_id)

        favorites = query.all() # cursor.fetchall() equivalent

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)
    finally:
        if existing_session is None:
            session.close()
            engine.dispose()

    return favorites

def favoriteIDlist(netid, existing_session = None):
    """Queries favorites table for favorite route_id's for given netid
    Arguments:
        netid (string)
    Returns:
        set of Favorites objects that match queries
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session

    favoriteList = favorites(netid, existing_session=session)
    routeids = set()
    for favorite in favoriteList:
        routeids.add(favorite.route_id)

    if existing_session is None:
        session.close()
        engine.dispose()

    return routeids

def isFavorite(netid, route_id, existing_session=None):
    """Determines whether route_id is a favorite of given user
    Arguments:
        netid (string)
        route_id (int)
    Returns:
        boolean of whether route is a favorite for given user
    """
    if existing_session is None:
        engine, session = create_session()
    else:
        session = existing_session
    ret = len(favorites(netid, route_id,
                        existing_session=existing_session))!=0
    if existing_session is None:
        session.close()
        engine.dispose()

    return ret


def test():

    print("Testing search")
    results = search()
    for i in results:
        print(i.name)

    print()
    print("Testing details")
    for i in range(46):
        print(details_query(i)[0].name)

    print()
    print("Testing search with name = hint")
    results = search(name = 'hint',
                     return_args_list=['name'])
    for i in results:
        print(i.name)
        try:
            print(i.grade)
        except:
            print("attribute not accessible because not specified")



if __name__ == '__main__':
    test()