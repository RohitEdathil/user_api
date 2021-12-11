from datetime import datetime, timedelta
from time import sleep
from src.models import Session, User
from app import db

"""
Run this script to clean up expired sessions and user Invites.
"""

SESSION_LIFE = timedelta(days=7)
INVITE_LIFE = timedelta(days=2)

while True:
    # Clean up expired sessions
    print("Cleaning up expired sessions started at {}".format(datetime.now()))
    map(db.delete, db.query(Session).filter(
        Session.created_at < datetime.now() - SESSION_LIFE).all())
    map(db.delete, db.query(User).filter(
        User.invited_at < datetime.now() - INVITE_LIFE).all())
    print("Next cleanup at {}".format(datetime.now() + timedelta(minutes=10)))
    sleep(600)
