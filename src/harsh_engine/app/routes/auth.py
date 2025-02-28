from flask import Blueprint, request, flash, render_template, url_for, g, redirect
from harsh_engine.app import database
from harsh_engine.app.model import entities, data_mappers
import hashlib

bp = Blueprint('auth', __name__, url_prefix='/auth')

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
        users = res.data
        
        if len(users) == 0:
            flash('Invalid username/password')
            return redirect('/')

        flash([user.to_json() for user in users])

    return render_template('home.html')