from hold_funcs import get_holds_by_route, get_hold_locs_by_route
from search import create_session
from database_defs import Routes, Holds, RouteCoords, RouteEdits, Sections
from database_defs import Comments, Favorites
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sys import stderr
from datetime import datetime

engine = create_engine("postgresql://wfdogrdljlercb:1fed2ff3281e5ca8619af0c62bd99bda6e5f6dfa2e50cd41866f38b73b92ae34@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d1dgp9c53v4u0n")
Session = sessionmaker(engine)

if __name__ == '__main__':
    route_id = 2
    list = get_holds_by_route(route_id)

    print(list)
    print(get_hold_locs_by_route(route_id))
    # # delete all unique holds
    # with Session() as session, session.begin():
    #     hold_ids = (session.query(RouteCoords)
    #                         .filter(RouteCoords.route_id == route_id)
    #                         .with_entities(RouteCoords.hold_id)
    #                         .all())

    #     num_holds = 0
    #     for hold_id in hold_ids:
    #         hold_id = hold_id[0]
    #         routes = (session.query(RouteCoords)
    #                         .filter(RouteCoords.hold_id == hold_id)
    #                         .with_entities(RouteCoords.route_id)
    #                         .all())

    #         if len(routes) == 1:
    #             try:
    #                 num_holds += (session.query(Holds)
    #                     .filter(Holds.hold_id == hold_id)
    #                     .delete())
    #             except:
    #                 num_holds += 0


    #     # delete hold id / route id associations
    #     try:
    #         num_routecoords = (session.query(RouteCoords)
    #             .filter(RouteCoords.route_id == route_id)
    #             .delete())
    #     except:
    #         num_routecoords = 0