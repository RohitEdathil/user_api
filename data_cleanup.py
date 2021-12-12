from datetime import datetime, timedelta
from time import sleep
from src.models import Session, User
from src.engine import db

"""
Run this script to clean up expired sessions and user Invites.
"""

SESSION_LIFE = timedelta(days=7)  # Time a session is valid
INVITE_LIFE = timedelta(days=2)  # Time an invite is valid

INTERVAL = 10  # Time between each run

if __name__ == "__main__":

    while True:
        # Cleans up expired sessions
        print("Cleaning up expired sessions started at {}".format(datetime.now()))
        map(db.delete, db.query(Session).filter(
            Session.created_at < datetime.now() - SESSION_LIFE).all())
        map(db.delete, db.query(User).filter(
            User.invited_at < datetime.now() - INVITE_LIFE).all())
        print("Next cleanup at {}".format(
            datetime.now() + timedelta(minutes=INTERVAL)))
        sleep(60 * INTERVAL)
