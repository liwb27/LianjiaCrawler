import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'just a secret key by liwb'
    MONGODB_URI = 'mongodb://localhost:27017'# mongodb
