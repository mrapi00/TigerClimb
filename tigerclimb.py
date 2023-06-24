# ----------------------------------------------------------------------
# tigerclimb.py
# ----------------------------------------------------------------------

# ------------------- standard library imports -------------------------
import datetime
from datetime import datetime

from sys import stderr
from json import dumps
from html import escape
from random import choice

from flask import Flask, request, make_response, redirect, url_for, flash
from flask import render_template
from flask_login import login_user, LoginManager, login_required, logout_user, current_user

# ------------------- imports from own codebase ------------------------
from search import favoriteIDlist, favoritesToName, isFavorite, search, details_query, create_session

from profile_funcs import User, add_favorite, remove_favorite
from comment_funcs import add_comment, remove_comment, route_comments, user_comments
from gradeconversion import number_to_grade, grade_to_number

from hold_funcs import connect_hold_by_id, delete_hold_by_id, disconnect_hold_by_id, add_hold
from hold_funcs import connect_hold_by_coord, get_holds_by_route, get_holds_by_section

from section_funcs import assign_section, get_section, get_routes_by_section, get_routeid_by_name

from route_funcs import update_route, add_route, delete_route, last_edit, get_all_routeids
from route_funcs import get_tape_col
#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.', static_url_path="/static",
            static_folder='./static')

# as discussed in lecture, might want to store secret key in seperate file
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

# necessary to import this here so above 'app' keyword not conflicting
import auth

# create 404 page if user goes to non-existent route
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errorpage.html', err = "Page does not Exist."), 404

#---------------------------------------------------------------------------
# Set up for creating login system and users

# required for Flask_Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# load in user, checking from database
@login_manager.user_loader
def load_user(netid):
    user = User(netid)
    return user

# routes to login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    username = auth.authenticate()

    try:
        netid = username.rstrip('\n')
        # login as CAS user. new user automatically created if new.
        user = User(netid)
        login_user(user)
        flash("Login Successful!")
        return redirect(url_for('profile'))
    except Exception:
        flash("Too many failed logins. Try again later.")

    # should hypothetically never reach this
    html = render_template("index.html")
    return make_response(html)

# Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out.")
    auth.logout()

#---------------------------------------------------------------------------
# Content related to routes

# home page
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index() :
    html = render_template('index.html')
    response = make_response(html)
    return response

# search routes page
@app.route('/searchresults', methods=['GET'])
def searchresults():
     # render and display
    html = render_template('searchresults.html', route_active = 'active')
    response = make_response(html)
    return response

# companion to searchroutes, referenced by AJAX for SPA
@app.route('/results', methods = ['GET'])
def results():
    route_name = request.args.get('route_name')
    min_grade = request.args.get('min_grade')
    max_grade = request.args.get('max_grade')
    rope_list = request.args.get('rope_list')
    sortby = request.args.get('sortby')

    min_grade = grade_to_number('5.' + min_grade)
    max_grade = grade_to_number('5.' + max_grade)
    if rope_list == '':
        rope_list = None
    else:
        rope_list = rope_list.replace(',',' ').split()
        try:
            rope_list = list(map(int, rope_list))
        except:
            rope_list = None
    engine, session = create_session()
    try:
        # build out html for search querying
        results = search(name=route_name, min_grade=min_grade,
                max_grade=max_grade, rope_list = rope_list, sortby=sortby,
                existing_session=session)

        html = '<thead>'
        html += '<tr>'
        html += '<th><strong>Route Name</strong></th>'
        html += '<th><strong>Grade</strong></th>'
        html += '<th><strong>Rope#</strong></th>'

        pattern = '<tr id="%s"><td class = "spacetd" id="title_%s"><a href= %s>%s</a></td>'
        pattern += '<td>%s</td>'
        pattern += '<td>%d</td>'

        # favorite section if user is logged in
        if (current_user.is_authenticated):
            html += '<th><strong>Favorited?<strong></th></tr></thead><tbody id="body">'
            pattern += '<td>%s</td></tr>'
            # set of route ids that are favorited by current user
            # note: previously was list, but set more efficient (O(1) search access time)
            favorite_set = favoriteIDlist(current_user._netid, existing_session=session)
        else:
            html += '<tbody id="body">'

        # generate each necessary result in table rows
        for result in results :
            href = "/routedetails?route_id=%d target=\"_blank\"" % result.route_id
            if (current_user.is_authenticated):
                checked = result.route_id in favorite_set
                if (checked) :
                    checked = "Yes"
                else: checked = "" # entry is empty to emphasize the 'Yes' favorites
                html += pattern % (result.route_id, result.route_id, href, escape(result.name), number_to_grade(result.grade, 'roped'), result.rope, checked)
            else :
                html += pattern % (result.route_id, result.route_id, href, escape(result.name), number_to_grade(result.grade, 'roped'), result.rope)
        html += '</tbody>'

    except:
        html = render_template('errorpage.html', err = "Unable to load Routes. Try to refresh page.")
        return make_response(html)
    # important: always make to close session to prevent database issues
    finally:
        session.close()
        engine.dispose()
    response = make_response(html)
    return response


# Routes to page that allows user to view details for routes
@app.route('/routedetails', methods=['GET'])
def routedetails():
    try:
        route_id = request.args.get('route_id')
        results = details_query(route_id)
        already_fav = False
        comments = []
        if (current_user.is_authenticated):
            if isFavorite(current_user._netid, route_id) :
                already_fav = True
            comments = route_comments(route_id, current_user._netid)

        html = render_template('routedetails.html',
            name = results['name'], routeid = results['routeid'],
            tape_col = results['tape_col'], rope = results['rope'],
            status = results['status'], date_created = results['date_created'],
            descrip = results['descrip'],
            grade_str = number_to_grade(results['grade'], 'roped'),
            date=results['date_created'].strftime('%m/%d/%Y'),
            alreadyFav = already_fav, comments = comments)
        response = make_response(html)
        return response
    except:
        html = render_template('errorpage.html', err = "Unable to load that Route ID.")
        return make_response(html)


# used to get image info specific to a route (including section info)
@app.route('/routeimage', methods = ['GET'])
def routeimage():

    route_id = request.args.get('route_id')

    # REPLACE WITH SIMPLER FUNCTION
    # hold_locs = get_hold_locs_by_route(route_id)
    # if len(hold_locs) > 0:
    #     section = hold_locs[0][2]
    # else:
    #     section = 'white'

    section = get_section(route_id)
    # print(section)

    # map a color to its HEX value for applying proper CSS coloring of hold
    parse_colors = {'Purple': '800080', 'Pink': 'EE5CA5', 'Red': 'E71616',
                    'Orange': 'FF8C00', 'Yellow': 'FFD700', 'Lime Green': '32CD32',
                    'Teal': '2A9D8F', 'Blue': '1E67DC', 'Green': '238E23',
                    'Brown': '8B4513', 'Black': '000000', 'White': 'F5F5F5'}

    tape_col = get_tape_col(route_id)
    if tape_col in parse_colors.keys():
        tape_col = parse_colors[tape_col]
    else:
        # if unknown color in DB, use this purplish color
        tape_col = 'DA70D6'

    hold_ids = get_holds_by_route(route_id)

    # REPLACE WITH SIMPLER FUNCTION
    section_locs = get_holds_by_section(section)
    section_holds = []
    # print(len(section_locs))
    for i in range(len(section_locs)):
        section_holds.append(list(section_locs[i]))
    #     section_holds.append((id,x,y))
    #     # print(get_id_by_coord(x,y,section))

    data = {'section': section, 'tape_col': tape_col, 'route_holds': hold_ids, 'section_holds': section_holds}
    # print(data)

    json = dumps(data)
    response = make_response(json)
    return response

# Routes to page that allows user to view wall section information
@app.route('/sections', methods = ['GET'])
def sections():
    # render and display
    html = render_template('sections.html', sections_active="active")
    response = make_response(html)
    return response

# companion to sections, referenced by AJAX for giving routes
# associated with section
@app.route('/section_routes', methods = ['GET'])
def section_routes():
    try:
        section = request.args.get('section')
        # get list of routes on wall section 'section'
        routes = get_routes_by_section(section)
        html = '<thead>'
        html += '<tr>'
        html += '<th><strong>Route Name</strong></th>'
        html += '<th><strong>Grade</strong></th>'
        html += '<th><strong>Rope#</strong></th>'
        pattern = '<tr id="%s"><td class = "spacetd" id="title_%s"><a href= %s>%s</a></td>'
        pattern += '<td>%s</td>'
        pattern += '<td>%d</td>'
        # favorite section if user is logged in
        if (current_user.is_authenticated):
            html += '<th><strong>Favorited?<strong></th></tr></thead><tbody id="body">'
            pattern += '<td>%s</td></tr>'
            # set of route ids that are favorited by current user
            # note: previously was list, but set more efficient (O(1) search access time)
            favorite_set = favoriteIDlist(current_user._netid)
        else:
            html += '</tr></thead><tbody id="body">'

        # generate each necessary result in table rows
        if len(routes) != 0 :
            for route in routes :
                href = "/routedetails?route_id=%d target=\"_blank\"" % route.route_id
                if (current_user.is_authenticated):
                    checked = route.route_id in favorite_set
                    if (checked) :
                        checked = "Yes"
                    else: checked = "" # entry is empty to emphasize the 'Yes' favorites
                    html += pattern % (route.route_id, route.route_id, href, escape(route.name), number_to_grade(route.grade, 'roped'), route.rope, checked)
                else :
                    html += pattern % (route.route_id, route.route_id, href, escape(route.name), number_to_grade(route.grade, 'roped'), route.rope)
        html += '</tbody>'
    except :
        html = render_template('errorpage.html', err = "Unable to load Routes.")
        return make_response(html)
    response = make_response(html)
    return response

# used to get image info specific to a route (including section info)
@app.route('/routeonly', methods = ['GET'])
def routeonly():

    route_id = request.args.get('route_id')

    parse_colors = {'Purple': '800080', 'Pink': 'EE5CA5', 'Red': 'E71616',
                    'Orange': 'FF8C00', 'Yellow': 'FFD700', 'Lime Green': '32CD32',
                    'Teal': '2A9D8F', 'Blue': '1E67DC', 'Green': '238E23',
                    'Brown': '8B4513', 'Black': '000000', 'White': 'F5F5F5'}

    tape_col = get_tape_col(route_id)
    if tape_col in parse_colors.keys():
        tape_col = parse_colors[tape_col]
    else:
        tape_col = 'DA70D6'

    hold_ids = get_holds_by_route(route_id)

    data = {'tape_col': tape_col, 'route_holds': hold_ids}
    # print(data)

    json = dumps(data)
    response = make_response(json)
    return response

#---------------------------------------------------------------------------
# Content related to user functionality

# Routes to page that allows user to view details for routes
@app.route('/favorites', methods=['GET'])
@login_required
def favorites():
    route_id = request.args.get('route_id')
    add_route = request.args.get('add_route')
    if add_route == 'True':
        add_favorite(current_user._netid, route_id)
        flash("Route added to favorites!")
    else:
        remove_favorite(current_user._netid, route_id)
        flash("Route removed from favorites!")

    return redirect('routedetails?route_id=' + route_id)

# profile page with info unique to a user (such as Favorites)
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    favorite_list = favoritesToName(current_user._netid)
    randid = choice(get_all_routeids())
    href_rand = "/routedetails?route_id=%d" % randid
    own_comments = user_comments(current_user._netid)
    html = render_template('profile.html', profile_active = 'active', hrefRand=href_rand,
                            favorites = favorite_list, own_comments = own_comments)
    response = make_response(html)
    return response

#----------------------------------------------------------------------------
# Pages related to admin functionality

# helper function for checking if user is admin, if not kick user from page
def not_admin() :
    if not current_user._admin :
        flash("Sorry you must be an Admin to access this page.")
        return True
    return False

# routes to admin page, which requires login
@app.route('/admin')
@login_required
def admin():
    if not_admin():
        return redirect(url_for('index'))

    new_route = request.get_json()
    if new_route is not None:
        print(new_route)
    return render_template("admin.html", admin_active = 'active')

# gives a table of routes displayed from admin side
@app.route('/admin_editroutes')
@login_required
def admin_editroutes():
    if not_admin():
        return redirect(url_for('index'))

    html = render_template('adminsearch.html', admin_active = 'active',
            action = 'Edit', search = 'adminsearch')
    response = make_response(html)
    return response

# called for SPA functionality for /adminroutes page
@app.route('/adminsearch')
@login_required
def adminsearch():
    if not_admin():
        return redirect(url_for('index'))

    route_name = request.args.get('route_name')
    engine, session = create_session()
    try:
        results = search(name=route_name,
                existing_session=session)


        html = '<tbody>'
        html += '<thead class="thead-dark"><tr><th>Edit Route</th>'
        html += '<th>Last Edited</th></tr></thead>'

        pattern = '<tr><td class = "spacetd"><a href= %s>%s</a></td>'
        pattern += '<td>%s</td></tr>' # associated with date string

        # generate each necessary result in table rows
        for result in results :
            try:
                time_stamp = last_edit(route_id=result.route_id, existing_session=session)[0]
                href = "/admin_edit?route_id=%d&version=%d" % (result.route_id, time_stamp.version)
                html += pattern % (href, escape(result.name), time_stamp.time_updated.strftime('%c'))
            except Exception as ex:
                print('except', ex)
        html += '</tbody>'
    finally:
        session.close()
        engine.dispose()
    response = make_response(html)
    return response

# page for editing a given route
@app.route('/admin_edit')
@login_required
def admin_edit():
    if not_admin():
        return redirect(url_for('index'))

    route_id = request.args.get('route_id')
    version = request.args.get('version')
    results = details_query(route_id)

    try :
        html = render_template('routeedit.html', admin_active = 'active',
            name = results['name'], route_id = results['routeid'],
            tape_col = results['tape_col'], rope = results['rope'],
            status = results['status'], date_created = results['date_created'],
            descrip = results['descrip'],
            grade_str = number_to_grade(results['grade'], 'roped'),
            date=results['date_created'], version = version)
        response = make_response(html)

        return response

    except:
        html = render_template('errorpage.html', err = "Unable to load that Route ID.")
        return make_response(html)


# Submits the database command for updating, typically after admin
# hits 'Submit Edits' on the admin_edit page
@app.route('/submitedit', methods=['POST', 'GET'])
@login_required
def submitedit():

    if not_admin():
        return redirect(url_for('index'))

    json = request.get_json()
    # print(json)

    colors = ['Purple', 'Pink', 'Red', 'Orange', 'Yellow', 'Lime Green',
              'Teal', 'Blue', 'Green', 'Brown', 'Black', 'White']

    success = 0
    try:
        route_id = json['route_id']
        name = json['name']
        grade = json['grade']
        grade = grade_to_number(grade)
        tape_col = json['tape_col']
        rope = json['rope']
        status = json['status']
        date = json['date']
        date_object = datetime.strptime(date.strip(), '%Y-%m-%d')
        descrip = json['descrip']
        # IMPORTANT: convert Left Wall -> left_wall
        section = json['section'].replace(" ", "_").lower()

        if tape_col not in colors:
            tape_col = None

        # if grade is None then is invalid
        if grade is not None :
            success = update_route(route_id, name, grade, tape_col, date, descrip, status,
                                    rope)
            print('update route success value: ', success)
            if (get_section(route_id) is None):
                assign_section(route_id, section)

            new_holds = json['new_coords']
            for hold in new_holds:
                x_per = float(hold[0])
                y_per = float(hold[1])
                included = hold[2]

                add_hold(x_per, y_per, 'up', 0, 'basic', section)
                if included:
                    connect_hold_by_coord(x_per, y_per, section, route_id)

            old_holds = json['old_ids']
            current_connections = get_holds_by_route(route_id)
            for hold in old_holds:
                hold_id = int(hold[0])
                included = hold[1]

                if hold_id in current_connections:
                    if not included:
                        disconnect_hold_by_id(hold_id, route_id)
                else:
                    if included:
                        connect_hold_by_id(hold_id, route_id)
            print('line 543')
            deleted = json['deleted']
            # do the delete stuff
            for hold in deleted:
                delete_hold_by_id(hold)
        else :
            print('grade', grade)
            success = 1
    except Exception as ex:
        print(ex, file=stderr)
        success = 1
    except:
        html = render_template('errorpage.html', err = "Failed to connect to Database. Try again in 5 minutes or contact team.")
        return make_response(html)

    if (success == 0) :
        flash("Route successfully edited!")
    else: flash("Route was NOT edited! Please make sure all fields are correctly filled in.")

    return 'success'

# gives a table of routes displayed from admin side
@app.route('/admin_deleteroutes')
@login_required
def admin_deleteroutes():
    if not_admin():
        return redirect(url_for('index'))

    html = render_template('adminsearch.html', admin_active = 'active',
            action = 'Delete', search = 'adminsearch2')
    response = make_response(html)
    return response

# called for SPA functionality for /admin_deleteroutes page
@app.route('/adminsearch2')
@login_required
def adminsearch2():
    if not_admin():
        return redirect(url_for('index'))

    route_name = request.args.get('route_name')

    # if sortby != 'name' and sortby != 'grade':
    #     sortby = 'name'
    engine, session = create_session()
    try:
        results = search(name=route_name,
                existing_session=session)

        html = '<tbody>'
        html += '<thead class="thead-dark"><tr><th>Route Name</th>'
        html += '<th class = "centered">Action</th>'
        html += '<th>Last Edited</th></tr></thead>'

        pattern = '<tr><td class = "spacetd"><a href= %s>%s</a></td>'
        pattern += '<td><a href= "%s" onclick=\"return confirm(\'Are you sure you want to delete this route?\');\"><button type="button" class="btn btn-danger">Delete</button></a></td>'
        pattern += '<td></td></tr>' #NEED TO ADD date

        # generate each necessary result in table rows
        for result in results :
            href_delete = "/submitdelete?route_id=%d" % result.route_id
            href_route = "/routedetails?route_id=%d" % result.route_id
            html += pattern % (href_route, escape(result.name), href_delete)
        html += '</tbody>'

    # important: always make to close session to prevent database issues
    finally:
        session.close()
        engine.dispose()
    response = make_response(html)
    return response

# conducts the admin delete a given route
@app.route('/submitdelete')
@login_required
def submitdelete():
    if not_admin():
        return redirect(url_for('index'))

    try :
        route_id = request.args.get('route_id')
        delete_route(route_id)
        # delete all the comments
        # delete the holds unique to the route
        # delete holdid <-> routeid associations
        # delete the favorites
        # delete the route-section association
        flash('Route successfully deleted!')
        return redirect(url_for('admin'))

    except Exception as ex:
        print(ex, file = stderr)
        html = render_template('errorpage.html', err = "Route ID not valid.")
        flash('Note: Route was not successfully deleted.')
        return make_response(html)


# page for editing a given route
@app.route('/admin_add')
@login_required
def admin_add():
    if not_admin():
        return redirect(url_for('index'))
    html = render_template('routeadd.html', admin_active = 'active')
    response = make_response(html)
    return response


# Submits the database command for updating, typically after admin
# hits 'Submit Edits' on the admin_edit page
@app.route('/submitadd', methods=['GET', 'POST'])
@login_required
def submitadd():
    if not_admin():
        return redirect(url_for('index'))

    json = request.get_json()
    print(json)

    colors = ['Purple', 'Pink', 'Red', 'Orange', 'Yellow', 'Lime Green',
              'Teal', 'Blue', 'Green', 'Brown', 'Black', 'White']

    route_id = None

    success = 0
    try:
        name = json['name']
        grade = json['grade']
        grade = grade_to_number(grade)
        tape_col = json['tape_col']
        rope = json['rope']
        status = json['status']
        date = json['date']
        date_object = datetime.strptime(date.strip(), '%Y-%m-%d')
        descrip = json['descrip']

        section = json['section']

        if tape_col not in colors:
            tape_col = None

        # if grade is None then is invalid
        if grade is not None :
            success = add_route(name=name, grade=grade, tape_col=tape_col, date_created=date,
            descrip=descrip, status=status, rope=rope)

            route_id = get_routeid_by_name(name)

            if section != 'default':
                assign_section(route_id, section)

                new_holds = json['new_coords']
                for hold in new_holds:
                    x_per = float(hold[0])
                    y_per = float(hold[1])
                    included = hold[2]

                    add_hold(x_per, y_per, 'up', 0, 'basic', section)
                    if included:
                        connect_hold_by_coord(x_per, y_per, section, route_id)

                old_holds = json['old_ids']
                current_connections = get_holds_by_route(route_id)
                for hold in old_holds:
                    hold_id = int(hold[0])
                    included = hold[1]

                    if hold_id in current_connections:
                        if not included:
                            disconnect_hold_by_id(hold_id, route_id)
                    else:
                        if included:
                            connect_hold_by_id(hold_id, route_id)

            deleted = json['deleted']
            # do the delete stuff
            for hold in deleted:
                delete_hold_by_id(hold)

        else:
            success = 1

    except Exception as ex:
        print(ex, file=stderr)
        success = 1


    if (success == 0) :
        flash("Route successfully added!")
        return str(route_id)
    else:
        flash("Route was NOT added! Please make sure all fields are correctly filled in.")
        return 'refresh'

@app.route('/admin_form')
@login_required
def admin_form():
    if not_admin():
        return redirect(url_for('index'))

    try :
        route_id = request.args.get('route_id')
        html = render_template('admin_form.html', route_id=route_id)
        response = make_response(html)
        return response

    except Exception:
        html = render_template('errorpage.html', err = "Route ID not valid.")
        return make_response(html)


@app.route('/save_holds', methods=['GET', 'POST'])
@login_required
def save_holds():
    holds = request.get_json()

    x = 0
    y = 1

    print(holds.keys())

    for hold in holds.values():
        x_per = int(float(hold[x])*10000)
        y_per = int(float(hold[y])*10000)

        add_hold(x_per, y_per, 'up', 0, 'basic', 'left_corner')
        connect_hold_by_coord(x_per, y_per, 'left_corner', 15)

    # ONE TIME DATABASE SET UP:
    # add_hold(x, y, status, size, hold_type, section)
    # connect_hold_by_coord(x, y, section, route_id)

    # add_hold(30*10000, 30*10000, 'up', 0, 'basic', 'left_corner')
    # connect_hold_by_coord(30*10000, 30*10000, 'left_corner', 14)
    # add_hold(30*10000, 70*10000, 'up', 0, 'basic', 'left_corner')
    # connect_hold_by_coord(30*10000, 70*10000, 'left_corner', 15)

    # print(get_holds_by_section('left_corner'))

    # print(get_all_holds())

    print(get_holds_by_route(15))
    print(get_holds_by_route(14))

    return 'success'

@app.route('/adminnewimage', methods=['GET'])
def adminimage():

    section = request.args.get('section')

    # user must choose a valid section
    if (section == 'Choose section'):
        return ''

    section_locs = get_holds_by_section(section)
    section_holds = []
    # # print(len(section_locs))
    for i in range(len(section_locs)):
        section_holds.append(list(section_locs[i]))
    #     section_holds.append((id,x,y))
    #     # print(get_id_by_coord(x,y,section))

    data = {'section': section, 'section_holds': section_holds}
    # print(data)

    json = dumps(data)
    response = make_response(json)
    return response

#----------------------------------------------------------------------------

# Submits the comment
@app.route('/submitcomment', methods=['GET'])
@login_required
def submitcomment():
    success = 0
    try:
        route_id= request.args.get('route_id')
        netid= current_user._netid
        comment= request.args.get('comment')
        public= request.args.get('public')
        public = (public == '0')

        # if grade is None then is invalid
        if comment != "" or comment is not None :
            success = add_comment(route_id, netid, comment, public)
        else:
            success = 1

    except Exception as ex:
        print(ex, file=stderr)
        success = 1

    # if (success == 0) :
    #     flash("Comment added!")
    # else: flash("Unable to add comment.")

    return ''
    # return redirect('routedetails?route_id=' + route_id)


# Submits the comment
@app.route('/deletecomment', methods=['GET','POST'])
@login_required
def deletecomment():
    success = 0
    try:
        route_id = request.args.get('route_id')
        comment_id = request.args.get('comment_id')
        # TODO: validate user, else any user can send GET Request
        success = remove_comment(comment_id)

    except Exception as ex:
        print(ex, file=stderr)
        success = 1

    if (success == 0) :
        flash("Comment deleted!")
    else: flash("Unable to delete comment.")

    return redirect('routedetails?route_id=' + route_id)


# Submits the comment
@app.route('/displaycomments', methods=['GET'])
def displaycomments():
    # comments of all users only displayed if logged in
    if not current_user.is_authenticated:
        return ''
    engine, session = create_session()
    try:
        route_id = request.args.get('route_id')
        mine = request.args.get('mine')
        bool_mine = (mine == '1')

        comments = route_comments(route_id = route_id, net_id = current_user._netid, mine=bool_mine)

        html = ''
        pattern = ''
        pattern += '<div class="media"><div class="media-body">'
        pattern += '<h4 class="media-heading user_name">%s</h4>'
        pattern += '%s'

        # generate each necessary result
        if (len(comments) == 0) :
            message = '<h3>Be the first to comment!</h3>'
            return make_response(message)
        for comment in comments :
            date = comment.timestamp.strftime('%B %d, %Y')
            html += pattern % (comment.netid, escape(comment.comment))

            html += '<p class="pull-right"><small>%s</small></p>' % date
            if comment.netid == current_user._netid :
                if not comment.public:
                    html += '<br><strong class = "badge bg-warning text-dark py-1 ms-1 fs-3">Private</strong>'
                html += '<br>'
                href_string = '/deletecomment?route_id=%s&comment_id=%s' % (route_id, comment.comment_id)
                html += '<small><a href=%s><button type="button" class="btn-sm btn-danger">' % href_string
                html += 'Delete Comment</button></a></small>'
            else :
                html += '<p></p>'
            html += '</div></div>'

    # important: always make to close session to prevent database issues
    finally:
        session.close()
        engine.dispose()

    response = make_response(html)
    return response
