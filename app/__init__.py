from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from config import get_config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()

def create_app(config_name=None):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(get_config(config_name))

    # Initialize database connection
    db.init_app(app)

    # Initialize OAuth
    oauth.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to this view if user is not logged in
    login_manager.login_message = 'Please log in to access this page.'  # Custom login message

    # Initialize OAuth
    oauth.init_app(app)

    # Register blueprints
    from .routes import main, company_routes
    from .auth.routes import auth  # Import the auth blueprint
    app.register_blueprint(main)
    app.register_blueprint(company_routes)
    app.register_blueprint(auth, url_prefix="/auth")  # All auth routes prefixed with /auth

    # Define user loader for Flask-Login
    from .database_setup import User, Session

    @login_manager.user_loader
    def load_user(user_id):
        session = Session()
        user = session.query(User).get(int(user_id))
        session.close()
        return user

    return app
