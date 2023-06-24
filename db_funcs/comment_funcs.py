from os import remove
from sys import stderr
from database_defs import Comments, Routes
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_
from datetime import datetime

engine = create_engine("postgresql://wfdogrdljlercb:1fed2ff3281e5ca8619af0c62bd99bda6e5f6dfa2e50cd41866f38b73b92ae34@ec2-54-157-79-121.compute-1.amazonaws.com:5432/d1dgp9c53v4u0n")
Session = sessionmaker(engine)

def add_comment(route_id, net_id, comment, public):
    """
    Adds comment to specified route.
    args: route_id, net_id, comment, and public
    return: 0 for success, 1 for failure
    """
    success = 0
    with Session() as session, session.begin():
        try:
            session.add(Comments(route_id=route_id, netid=net_id, comment=comment, public=public))
            session.commit()
        except Exception as ex:
            print(ex, file=stderr)
            success = 1
    return success


def user_comments(net_id):
    """
    Gets all comments user has made
    args: net_id
    return: list of Comments objects with fields comment, comment_id,
    route_id, timestamp, and public sorted in chronological order
    """
    with Session() as session, session.begin():
        try:
            results = (session.query(Comments, Routes).
                    with_entities(Comments.comment,
                    Comments.comment_id,
                    Comments.route_id,
                    Comments.timestamp,
                    Routes.name).filter(Comments.netid==net_id)
                    .filter(Comments.route_id==Routes.route_id)
                    ).order_by(Comments.comment_id.desc()).all()
            return results
        except Exception as ex:
            print(ex, file=stderr)

def route_comments(route_id, net_id, mine=False):
    """
    Gets all public comments of route and private comments of user
    for that route. If mine is True, gets only current user's comments on
    that route.
    args: route_id, net_id, mine
    return: list of comments objects with fields comment,
    netid, timestamp, comment_id (in chronological order)
    """
    with Session() as session, session.begin():
        try:
            query = (session.query(Comments).
                    with_entities(Comments.comment,
                    Comments.comment_id,
                    Comments.route_id,
                    Comments.netid,
                    Comments.timestamp,
                    Comments.public)
                    ).filter(Comments.route_id==route_id)
            if mine:
                query = query.filter(Comments.netid==net_id)
            else:
                query = query.filter(or_(Comments.netid==net_id, Comments.public==True))

            results = query.order_by(Comments.comment_id.desc()).all()
        except Exception as ex:
            print(ex, file=stderr)
    return results


def remove_comment(comment_id):
    """
    Removes specified comment.
    args: comment_id
    return: 0 for success, 1 for failure
    """
    success = 0
    with Session() as session, session.begin():
        try:
            (session.query(Comments)
                .filter(Comments.comment_id==comment_id).delete())
        except Exception as ex:
            print(ex, file=stderr)
            success = 1
    return success

def edit_comment(comment_id, comment, public):
    """
    Edits specified comment. Can also edit whether comment is public.
    args: comment_id, comment, public
    return: 0 for success, 1 for failure
    """
    success = 0
    with Session() as session, session.begin():
        try:
            (session.query(Comments)
                .filter(Comments.comment_id==comment_id).update({
                    'comment':comment, 'public':public}))
        except Exception as ex:
            print(ex, file=stderr)
            success = 1
    return success


def main():
    comments = route_comments(route_id=45, net_id='mrapi', mine=False)
    # for comment in comments:
    #     remove_comment(comment_id=comment.comment_id)
    # add_comment(route_id=45, net_id='dw26', comment='Davey is a dumb dumb', public=True)
    # add_comment(route_id=45, net_id='dw26', comment='Davey is even more of a dumb dumb', public=True)
    # add_comment(route_id=45, net_id='dw26', comment='Davey is actually a genius', public=True)
    print("Route comments: ")
    for comment in comments:
        print(comment.netid)
        print(comment.comment)
        print()
    print("User comments: ")
    comments = user_comments('mrapi')
    for comment in comments:
        print(comment.name)
        print(comment.comment)
        print()
if __name__ == '__main__':
    main()