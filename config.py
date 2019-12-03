import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
username = 'andycousineau'
host = 'localhost'
port = 5432
database = 'fyyur'

SQLALCHEMY_DATABASE_URI = f'postgresql://{username}@{host}:{port}/{database}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
