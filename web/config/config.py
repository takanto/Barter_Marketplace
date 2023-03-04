import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {'messageDB': os.getenv('MESSAGE_STORAGE_URL')}
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://'+os.getenv('POSTGRES_USER')+':'+os.getenv('POSTGRES_PW')+'@'+os.getenv('POSTGRES_URL')+'/'+os.getenv('POSTGRES_DB')
    DEBUG = False
    TESTING = False
    

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('MIGRATION_DB')
    
class TestConfig(Config):
    TESTING = True
    DEBUG = True
    WTF_CSRF_METHODS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    
class ProdConfig(Config):
    pass