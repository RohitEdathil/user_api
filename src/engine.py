from os import environ
from sqlalchemy.orm.session import sessionmaker, Session as sess
from sqlalchemy import create_engine


# Reads database connection settings from environment variables
try:
    SQL_USER = environ['SQL_USER']
    SQL_PASSWORD = environ['SQL_PASSWORD']
    SQL_HOST = environ['SQL_HOST']
    SQL_DATABASE = environ['SQL_DATABASE']
except KeyError:
    print("Please set the environment variables SQL_USER, SQL_PASSWORD, SQL_HOST, SQL_DATABASE")
    exit(1)

# Creates the database engine
engine = create_engine(
    f"mysql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}/{SQL_DATABASE}", echo=True)
# Connects to the database
try:
    _sess = sessionmaker()
    _sess.configure(bind=engine)
    db: sess = _sess()
    print("Connected to Database")
except Exception as e:
    print(e)
    exit(1)
