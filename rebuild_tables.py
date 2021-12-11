from src.models import Base
from app import engine
"""
Run this script to rebuild the tables in the database. If the model has changed.
Beware that this will delete all data in the database.
"""
print("Droping all tables")
Base.metadata.drop_all(engine)
print("Creating all tables")
Base.metadata.create_all(engine)
