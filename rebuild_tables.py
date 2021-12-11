from src.models import metadata
from app import engine
"""
Run this script to rebuild the tables in the database. If the model has changed.
Beware that this will delete all data in the database.
"""
print("Droping all tables")
metadata.drop_all(engine)
print("Creating all tables")
metadata.create_all(engine)
