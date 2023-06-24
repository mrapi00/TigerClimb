from xml.etree.ElementTree import Comment
from search import create_session

from database_defs import Base, Favorites, RouteEdits, Routes, Profiles, Comments


def main():
    """Create a new table in the database - example, don't run this again
    or the database will yell at you
    """
    engine, session = create_session()

    Base.metadata.create_all(engine)
    # Routes.__table__.drop(engine)
    # RouteEdits.__table__.drop(engine) 
    # for i in range(40):
    #     if i!=7:
    #         session.add(Favorites(netid='mrapi', route_id=i))
    # session.commit()
    # session.commit()
    # for i in range(0,45):
    #     session.add(RouteEdits(route_id=i, netid='dw26'))
    # session.commit()
    # session.query(RouteEdits).filter(RouteEdits.route_id==44).update({'route_id':44, 'netid':'dw26'})
    # results = session.query(RouteEdits).order_by(RouteEdits.route_id).all()

    # for i in results:
    #     print()
    #     print("Route_id: " + str(i.route_id))
    #     print("version: " + str(i.version))
    #     print("time_created: "+ str(i.time_created))
    #     print("time_updated: " + str(i.time_updated))
    session.commit()
    session.close()
    engine.dispose()


if __name__ == '__main__':
    main()