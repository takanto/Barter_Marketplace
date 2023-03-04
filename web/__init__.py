from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from oauthlib.oauth2 import WebApplicationClient
import requests
from web.config.config import ProdConfig
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
GOOGLE_CLIENT_ID = os.getenv("SSO_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("SSO_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    """
    Connects to the Google OpenID Connect discovery endpoint to get the
    information we need to authorize users.

    Output:
        A dictionary containing the Google OpenID Connect discovery document
    """
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def create_app(config_class = ProdConfig()):
    """
    Creates the app and initializes the database and login manager

    Input:
        config_class: The configuration class to use
    
    Output:
        The app
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    from web import routes
    return app