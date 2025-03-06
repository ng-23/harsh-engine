import os
from harsh_engine.app import database
from flask import Flask, render_template
from dotenv import load_dotenv

'''
When you import the harsh_engine.app subpackage,
all code in this module will be run automatically.
'''

# load environment variables, which we'll use to configure the app
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY') # see https://stackoverflow.com/questions/63189783/the-session-is-unavailable-because-no-secret-key-was-set
    app.config['DATABASE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.getenv('DATABASE_SCHEMA'))
    app.config['N_DUMMY_USERS'] = int(os.getenv('N_DUMMY_USERS'))
    app.config['SEED'] = int(os.getenv('SEED'))

    with app.app_context():
        database.init_db(
            os.getenv('DATABASE_SCHEMA')
        )  # this creates the database according to the provided schema and saves it to the provided location

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about/')
    def about():
        return render_template('about.html')
    
    from .routes import auth
    app.register_blueprint(auth.bp)

    @app.route('/home')
    @auth.login_required
    def home():
        return render_template('home.html')

    return app