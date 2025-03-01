from flask import Blueprint, request, flash, g, redirect, session, url_for
from harsh_engine.app import database
from harsh_engine.app.model import entities, data_mappers
import hashlib
import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        database.get_db()
        user_mapper = data_mappers.UserMapper()
        user_mapper.db = g.db

        res = user_mapper.read_by_id(user_id)

        if res.valid:
            g.user = res.data[0].to_json()
        else:
            # TODO: proper error handling
            session.clear()
            g.user = None

def login_required(view):
    @functools.wraps(view) # see https://stackoverflow.com/questions/308999/what-does-functools-wraps-do
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('You must be logged in to view this page')
            return redirect('/')

        return view(**kwargs)

    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        try:
            user = entities.User(username, password, password_is_hashed=False)
        except Exception as e:
            error = str(e)

        res = None
        if error is None:
            database.get_db()
            user_mapper = data_mappers.UserMapper()
            user_mapper.db = g.db
            res = user_mapper.create(user)

        if res is not None and not res.valid:
            error = res.message

        flash(error if error is not None else res.message)

    return redirect('/')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        database.get_db()
        user_mapper = data_mappers.UserMapper()
        user_mapper.db = g.db

        res = user_mapper.read_by_credentials(username, hashlib.md5(password.encode('utf-8')).hexdigest())

        if res.valid:
            users = res.data
            if len(users) == 0:
                flash('Invalid username/password')
                return redirect('/')
            
            session.clear()
            session['user_id'] = users[0].id

            return redirect(url_for('home'))
        else:
            flash(res.message) # there was an error of some sort
        
        return redirect('/')
    
    return redirect(url_for('home'))

@bp.route('/logout', methods=('POST',))
def logout():
    session.clear()
    return redirect('/')
