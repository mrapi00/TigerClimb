#-----------------------------------------------------------------------
# database_defs.py
# Defines database in terms of classes for SQLAlchemy.
#-----------------------------------------------------------------------

from enum import unique
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, Boolean, text
from sqlalchemy.sql import func

Base = declarative_base()

# routes: the main table for information about each route
# primary key: route id
# other columns: name, grade, consensus grade, tape_col, tape_col2,
# date_created, descrip, status, rope, route_type
class Routes(Base):
    __tablename__ = 'routes'
    route_id = Column(Integer, primary_key=True)
    name = Column(String)
    grade = Column(Float) # note change from previous
    consensus_grade = Column(Float)
    tape_col = Column(String)
    tape_col2 = Column(String)
    date_created = Column(Date)
    descrip = Column(String)
    status = Column(String)
    rope = Column(Integer)
    route_type = Column(String)

# route_edits: keeps track of admin edits
class RouteEdits(Base):
    __tablename__ = 'route_edits'
    route_id = Column(Integer, primary_key=True, autoincrement=True)
    netid = Column(String, primary_key=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    version = Column(Integer, default=0, onupdate = text('version + 1'))

    # name = Column(String)
    # grade = Column(Float)
    # consensus_grade = Column(Float)
    # tape_col = Column(String)
    # tape_col2 = Column(String)
    # date_created = Column(Date)
    # descrip = Column(String)
    # status = Column(String)
    # rope = Column(Integer)
    # route_type = Column(String)
    # edit_status = Column(String)


# grades: the grades entered by users
# primary key: route id, netid (each user may only enter one grade)
# other columns: grade (the grade entered)
class Grades(Base):
  __tablename__ = 'grades'
  route_id = Column(Integer, primary_key=True)
  netid = Column(String, primary_key=True)
  grade = Column(Integer)

# comments: the comments entered by users
# primary key: route_id, netid, timestamp (users may comment >1 times)
# other columns: comment (the text of the comment) and public (boolean)
class Comments(Base):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True)
    route_id = Column(Integer)
    netid = Column(String)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
    comment = Column(String)
    public = Column(Boolean)

# ratings: the ratings (how enjoyable the route is) entered by users
# primary key: route_id, netid (each user may only rate once)
# other columns: rating
class Ratings(Base):
    __tablename__ = 'ratings'
    route_id = Column(Integer, primary_key=True)
    netid = Column(String, primary_key=True)
    rating = Column(Integer)

# setters: the setters for the routes
# primary key: route_id, setter (multiple setters may make a route)
class Setters(Base):
    __tablename__ = 'setters'
    route_id = Column(Integer, primary_key=True)
    setter = Column(String, primary_key=True)

# images: images associated with routes
# primary key: route_id, image_id
# other columns: start_visible (Boolean, whether the start hold is in
# the image), start_x (x coordinate of start hold in pixels or 0 if not
# visible), start_y (ditto)
class Images(Base): # check with frontend what they want here
    __tablename__ = 'images'
    route_id = Column(Integer, primary_key=True)
    image_id = Column(String, primary_key=True)
    start_visible = Column(Boolean)
    start_x = Column(Integer)
    start_y = Column(Integer)

# rules: the rule sets associated with each route
# primary key: route_id, rule_num (0 for primary route to display,
# and numbered in order of entry for all others)
# other columns: two_hold, sit_start, features (Booleans), rules_info (a
# String containing other rules information)
class Rules(Base):
    __tablename__ = 'rules'
    route_id = Column(Integer, primary_key=True)
    rule_num = Column(Integer, primary_key=True)
    two_hold = Column(Boolean)
    sit_start = Column(Boolean)
    features = Column(Boolean)
    rules_info = Column(String)

# style: the style keywords associated with a route
# primary key: route_id, netid, style (each user may enter multiple style
# keywords)
class Style(Base):
    __tablename__ = 'style'
    route_id = Column(Integer, primary_key=True)
    netid = Column(String, primary_key=True)
    style = Column(String, primary_key=True)


# profiles: the user profiles
# primary key: netid
# other columns: is_admin
class Profiles(Base):
    __tablename__ = 'profiles'
    netid = Column(String, primary_key=True, unique = True)
    is_admin = Column(Boolean)

# Favorites: users' favorite routes
# primary key: netid of user, route_id of favorite route
class Favorites(Base):
    __tablename__ = 'favorites'
    netid = Column(String, primary_key=True)
    route_id = Column(Integer, primary_key=True)

# Holds: the coordinates of every hold in the database
class Holds(Base):
    __tablename__ = 'holds'
    hold_id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    status = Column(String)
    size = Column(Integer)
    hold_type = Column(String)
    section = Column(String)

# the holds associated with each route
# each row is one route_id and one hold_id
class RouteCoords(Base):
    __tablename__ = 'route_coords'
    route_id = Column(Integer, primary_key = True)
    hold_id = Column(Integer, primary_key = True)

# the section associated with each route
class Sections(Base):
    __tablename__ = 'sections'
    route_id = Column(Integer, primary_key=True)
    section = Column(String) # TODO if multiple sections allowed add primary_key=True
