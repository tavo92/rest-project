""" This module handles request to the database. """

import sqlite3
import bcrypt
from server import APP
from flask import g

def connect_db():
    """Connects to the specific database."""
    database = sqlite3.connect(APP.config['DATABASE'])
    database.row_factory = sqlite3.Row
    return database

def get_db():
    """Opens a new database connection if there is none yet for the
    current APPlication context. """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@APP.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    """Erase and creates a new database."""
    with APP.app_context():
        database = get_db()
        with APP.open_resource('schema.sql', mode='r') as squema:
            database.cursor().executescript(squema.read())
        database.commit()

def user_exists(user):
    """Returns True if the user already exists in the database."""
    database = get_db()
    cur = database.execute('SELECT id from users where user = ?', [user])
    if cur.fetchall():
        return True
    return False

def create_user(user, passw):
    """Return True if the user is created successfully."""
    database = get_db()
    passw = passw.encode('utf-8')
    hashed = bcrypt.hashpw(passw, bcrypt.gensalt())
    database.execute('INSERT INTO users (user, password) \
                      VALUES (?, ?)', (user, hashed))
    database.commit()
    return True

def login_user(user, passw):
    """Return True if the username and password are correct."""
    database = get_db()
    cur = database.execute('SELECT password FROM users WHERE user = ?', [user])
    passw = passw.encode('utf-8')
    hashed = cur.fetchone()
    if hashed is None:
        return False

    if bcrypt.hashpw(passw, hashed['password'].encode('utf-8')) \
       == hashed['password']:
        return True
    return False

def get_userid(user):
    """Returns the user id."""
    database = get_db()
    cur = database.execute('SELECT id from users where user = ?', [user])

    userid = cur.fetchone()
    if userid is None:
        return -1
    return userid['id']

def add_entrie(name, cityname, gmt, userid):
    """Adds an entrie"""
    database = get_db()
    cur = database.cursor()
    cur.execute("INSERT INTO entries (name, cityName, gmt, userid) VALUES \
                (?, ?, ?, ?)", (name, cityname, gmt, userid))
    database.commit()
    return cur.lastrowid

def del_entrie(entrieid, userid):
    """Deletes an entrie."""
    database = get_db()
    database.execute("DELETE FROM entries WHERE id = ? and \
                     userid = ?", (entrieid, userid))
    database.commit()
    return True

def modify_entrie(entrieid, name, cityname, gmt, userid):
    """Modifes the entrie that has the entrieID id."""
    database = get_db()
    database.execute("UPDATE entries SET name = ?, cityName = ?, \
                      gmt = ? WHERE userid = ? and id = ?", \
                      (name, cityname, str(gmt), str(userid), str(entrieid)))
    database.commit()

def get_entries(userid, namefilter):
    """Returns all the entries from a user, filtered by namefilter."""
    database = get_db()
    cur = database.cursor()
    if namefilter is None or namefilter == 'undefined':
        cur = cur.execute("SELECT id, name, cityname, gmt FROM entries \
                           WHERE userid = ?", (str(userid)))
    else:
        cur = cur.execute("SELECT id, name, cityname, gmt FROM entries \
                           WHERE userid = ? AND name LIKE ?", \
                           (str(userid), namefilter+'%'))
    return cur.fetchall()
