import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:3229@localhost:5432/fyuur_app'
SQLALCHEMY_TRACK_MODIFICATION = False

SECRET_KEY = b'\xfd\xd2\x83\x810W{P&L\x8c \xd6#\xec\xde\x10\x12eU\xfbbH\xd04\xf3\xce\xc6.>\xf5%'