"""Handles request to the server."""

from flask import Flask, session, request, render_template, jsonify
import os
import database
from datetime import datetime

APP = Flask(__name__)

@APP.route('/')
def index():
    """Renders the index page."""
    return render_template('index.html')

@APP.route('/apiTest')
def api_test():
    """Renders the api test page."""
    return render_template('apiTest.html')

@APP.route('/login', methods=['POST'])
def login():
    """Logs in the user."""
    if 'username' in session:
        return jsonify(ok=0, msg='You are already log in')
    user = request.form['user']
    passw = request.form['pass']
    if database.login_user(user, passw):
        session['username'] = user
        session['userid'] = database.get_userid(user)
        session['password'] = passw
        return jsonify(ok=1, msg='User is log in now')
    return jsonify(ok=0, msg='User could not be log in')

@APP.route('/createUser', methods=['POST'])
def create_user():
    """Creates a new user."""
    if 'username' in session:
        return jsonify(ok=0, msg='First logout before creating a new user')
    user = request.form['user']
    passw = request.form['pass']
    if database.user_exists(user):
        return jsonify(ok=0, msg='User already exists')

    if database.create_user(user, passw):
        session['username'] = user
        session['userid'] = database.get_userid(user)
        session['password'] = passw
        return jsonify(ok=1, msg='User created!')
    return jsonify(ok=0, msg='User could not be created')

@APP.route('/logout', methods=['POST', 'GET'])
def logout():
    """Clears the session data."""
    session.pop('username', None)
    session.pop('userid', None)
    session.pop('password', None)
    return jsonify(ok=1, msg='User has just loged out!')

@APP.route('/isLoggedIn', methods=['GET'])
def is_logged_in():
    """Checks if user is logged in or not."""
    if 'username' in session and 'password' in session:
        if database.login_user(session['username'], session['password']):
            return jsonify(ok=1, user=session['username'])
    return jsonify(ok=0)

@APP.route('/entries/add', methods=['PUT'])
def add_entrie():
    """Adds a new entrie."""
    if not 'username' in session or \
       not 'password' in session or \
       not database.login_user(session['username'], session['password']):
        return jsonify(ok=0, msg='User is not log in')
    name = request.form['name']
    cityname = request.form['cityName']
    gmt = int(request.form['gmt'])
    entrieid = int(request.form['id'])

    if name == "" or cityname == "" or gmt < -20 or gmt > 20:
        return jsonify(ok=0, msg='Entrie is invalid')
    userid = session['userid']
    if entrieid == -1:
        entrieid = database.add_entrie(name, cityname, gmt, userid)
    else:
        database.modify_entrie(entrieid, name, cityname, gmt, userid)
    if entrieid is not None:
        return jsonify(ok=1, entrieID=entrieid)
    return jsonify(ok=0, msg='Entrie could not be added')

@APP.route('/entries/del', methods=['DELETE'])
def del_entrie():
    """Deletes the entrie entrieID."""
    if not 'username' in session or \
       not 'password' in session or \
       not database.login_user(session['username'], session['password']):
        return jsonify(ok=0, msg='User is not log in')

    entrieid = request.form['entrieID']

    if database.del_entrie(entrieid, session['userid']):
        return jsonify(ok=1)
    return jsonify(ok=0, msg='Entrie could not be deleted')

@APP.route('/entries', methods=['GET'])
def get_entries():
    """Returns all the entries from a user, filtered by namefilter."""
    if not 'username' in session or \
       not 'password' in session or \
       not database.login_user(session['username'], session['password']):
        return jsonify(ok=0, msg='User is not log in')

    namefilter = request.args.get('nameFilter', None)
    entries = database.get_entries(session['userid'], namefilter)
    data = "["
    addcomma = False
    for entrie in entries:
        if addcomma:
            data += ", "
        else:
            addcomma = True

        data += '{"name": "' + entrie['name'] + '", "cityName": "' + \
                entrie['cityName'] + '", "gmt": ' + str(entrie['gmt']) + \
                ', "id": '+ str(entrie['id']) +'}'
    data += "]"
    return jsonify(ok=1, entries=data)

@APP.route('/time')
def get_time():
    """Returns the current time of the server in GMT."""
    hour = datetime.utcnow().strftime('%H')
    minute = datetime.utcnow().strftime('%M')
    second = datetime.utcnow().strftime('%S')
    return jsonify(ok=1, time='{"hour":"' + hour + '", "minute":"' +minute+ \
                              '", "second":"'+ second +'"}')

# set the secret key
APP.secret_key = 'ap!K\x8e\xf2\xc2\x95\x01\xc6\x9c\xd0' + \
                 '\x11;\xad\xffk)\xa2\x99f&\xa9b'

APP.config.update(dict(
    DATABASE=os.path.join(APP.root_path, 'database.db'),
    DEBUG=True,
))
APP.config.from_envvar('FLASKR_SETTINGS', silent=True)


if __name__ == '__main__':
    APP.run()
