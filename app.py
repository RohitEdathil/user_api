from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import OperationalError, IntegrityError
from datetime import datetime
from data_cleanup import INVITE_LIFE, SESSION_LIFE
from src.models import *
from src.utils import *
from src.engine import db, engine
app = FastAPI()


@app.get("/", tags=["General"])
def home():
    """
    Redirects to Swagger UI
    """
    return RedirectResponse(url="/docs")


@app.post("/invite", tags=["Invite"])
async def invite(data: dict):
    """
    Creates an invitation for a new user. 

    - ## Parameters:
        - `name`: Name of the user (Required, Max Length: 100)
        - `phone`: Phone number of the user (Required, Max Length: 20)
        - `email`: Email of the user (Required, Max Length: 100)
        - `alternate_email`: Alternate email of the user (Optional, Max Length: 100)
        - `organizations`: [

            { \\
               - `name`: Name of the organization (Required, Max Length: 100) \\
               - `role`: Role of the user in the organization (Required, Max Length: 100) \\
               - `valid_till`: Date when the user will be valid till (Optional) \\
            } \\
            . \\
            . \\
        ] (Must be inside a List, Optional)
    - ## Returns:
        - `invite_id`: Unique code to be for signing up
        - `expires_at`: Date and time when the invitation expires
    """

    # Validates email and phone number
    if not is_phone_number(data.get("phone_number", '')):
        return {"message": "Invalid phone number"}
    if not is_email(data.get("email", '')):
        return {"message": "Invalid email"}
    if data.get("alternate_email", '') and not is_email(data.get("alternate_email", '')):
        return {"message": "Invalid alternate email"}

    # Issues an invite code and time of invitation
    invite_code = generate_invite_code()
    invited_at = datetime.now()

    # Extracts organizations from the data
    organizations = data.pop("organizations", False)

    # Creates the user object
    user = User(**data, invite_code=invite_code, invited_at=invited_at)

    try:
        # Adds the user to the database
        db.add(user)
        db.flush()

        # Adds the organizations to the database
        if organizations:
            for organization in organizations:
                org = Organization(**organization)
                org.user = user.id
                db.add(org)
        # Commits the changes to the database
        db.commit()
    except TypeError:
        db.rollback()
        return {"error": "Bad formatting (Organizations must be inside a list)"}
    except OperationalError as e:
        # Detects missing values and returns error message
        db.rollback()
        return {"error": e.orig.args[1]}
    except IntegrityError as e:
        # Detects duplicate values and returns error message
        db.rollback()
        return {"error": e.orig.args[1]}

    # Returns the invite code and expiration date
    return {"invite_code": invite_code, "expires_at": invited_at + INVITE_LIFE}


@app.post("/create", tags=["Create"])
async def create(data: dict):
    """
    Signs up a user with an invitation code.

    - ## Parameters:
        - `invite_code`: Invitation code (Required, Max Length: 10)
        - `password`: Password of the user (Required, Max Length: 100)

    - ## Returns:
        - `message`: Success message if the user is signed up successfully
    """
    # Fetches the user from the database
    user = db.query(User).filter(
        User.invite_code == data.get("invite_code", '')).first()

    # Returns error message if the user is not found
    if not user:
        return {"error": "Invalid invite code"}

    # Reads password from the data
    password = data.get("password", False)
    # Returns error message if the password is not provided
    if not password:
        return {"error": "Password is required"}

    # Checks if the invite code expired
    if user.invited_at + INVITE_LIFE < datetime.now():
        db.delete(user)
        db.commit()
        return {"error": "Invite code expired"}
    # Sets the password , sets user as active and removes the invite code
    user.activated = True
    user.invite_code = ''
    user.password = hash_password(password)

    # Commits the changes to the database
    try:
        db.commit()
    except OperationalError as e:
        db.rollback()
        return {"error": e.orig.args[1]}

    # Returns success message
    return {"message": "User created successfully"}


@app.post("/login", tags=["Login"])
async def login(data: dict):
    """
    Logs in a user.

    - ## Parameters:
        - `email`: Email of the user (Required, Max Length: 100)
        - `password`: Password of the user (Required, Max Length: 100)

    - ## Returns:
        - `token`: Token to be used for verifying the user
        - `expires_at`: Date and time when the token expires
    """
    # Fetches the user from the database
    user = db.query(User).filter(
        User.email == data.get("email", '')).first()

    # Returns error message if the user is not found
    if not user:
        return {"error": "Invalid email or password"}

    # Reads password from the data
    password = data.get("password", False)

    # Returns error message if the password is not provided
    if not password:
        return {"error": "Password is required"}

    # Checks if the password is correct
    if not check_password(password, user.password):
        return {"error": "Invalid email or password"}

    # Issues a token and time of login
    token = generate_token()
    created_at = datetime.now()

    # Adds the session to the database
    db.add(Session(user=user.id, created_at=created_at, token=token))
    db.commit()

    # Returns success message
    return {"token": token, "expires_at": created_at + SESSION_LIFE}


@app.post("/logout", tags=["Logout"])
async def logout(data: dict):
    """
    Logs out a user.

    - ## Parameters:
        - `token`: Token to be used for verifying the user (Required, Max Length: 100)

    - ## Returns:
        - `message`: Success message if the user is logged out successfully
    """
    # Reads token from data
    token = data.get("token", False)

    # Checks if token is present
    if not token:
        return {"error": "Token missing"}
    # Fetches the session from the database
    session = db.query(Session).filter(
        Session.token == token).first()

    # Returns error message if the session is not found
    if not session:
        return {"error": "Invalid token"}

    # Checks if the token is expired
    if session.created_at + SESSION_LIFE < datetime.now():
        db.delete(session)
        db.commit()
        return {"error": "Token already expired"}

    # Removes the session from the database
    db.delete(session)
    db.commit()

    # Returns success message
    return {"message": "User logged out successfully"}


@app.post("/edit", tags=["Edit"])
def edit(data: dict):
    """
    Edits the info of the currently logged in user.

    - ## Parameters:
        - `token` : A valid token obtained at the time of login
        - `name`: Name of the user (Optional, Max Length: 100)
        - `phone`: Phone number of the user (Optional, Max Length: 20)
        - `email`: Email of the user (Optional, Max Length: 100)
        - `alternate_email`: Alternate email of the user (Optional, Max Length: 100)
        - `profile_pic`: URL to the profile picture of the user (Optional, Max Length: 200)
        - `organizations`: [

            { \\
               - `name`: Name of the organization (Required, Max Length: 100) \\
               - `role`: Role of the user in the organization (Required, Max Length: 100) \\
               - `valid_till`: Date when the user will be valid till (Optional) \\
            } \\
            . \\
            . \\
        ] (Must be inside a List, Optional, If provided all the existing roles of the user will be overwritten)
    - ## Returns:
        - `message`: Success message if editted successfully
    """
    # Reads token from data
    token = data.get("token", False)

    # Checks if token is present
    if not token:
        return {"error": "Token missing"}

    # Fetches the session from the database
    session = db.query(Session).filter(
        Session.token == token).first()

    # Returns error message if the session is not found
    if not session:
        return {"error": "Invalid token"}

    # Checks if the token is expired
    if session.created_at + SESSION_LIFE < datetime.now():
        db.delete(session)
        db.commit()
        return {"error": "Token already expired"}

    # Fetches user of correspnding session
    user = db.query(User).filter(User.id == session.user).first()

    # Modify the fields
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.alternate_email = data.get("alternate_email", user.alternate_email)
    user.profile_pic = data.get("profile_pic", user.profile_pic)

    # Extracts organizations from the data
    organizations = data.pop("organizations", False)

    # Saves changes
    try:
        # Removes all previous organizations
        prev_orgs = db.query(Organization).filter(
            Organization.user == user.id).all()
        for org in prev_orgs:
            db.delete(org)

        # Adds the organizations to the database
        if organizations:
            for organization in organizations:
                org = Organization(**organization)
                org.user = user.id
                db.add(org)
        # Commits the changes to the database
        db.commit()
    except TypeError:
        db.rollback()
        return {"error": "Bad formatting (Organizations must be inside a list)"}
    except OperationalError as e:
        # Detects missing values and returns error message
        db.rollback()
        return {"error": e.orig.args[1]}
    except IntegrityError as e:
        # Detects duplicate values and returns error message
        db.rollback()
        return {"error": e.orig.args[1]}

    return {"message": "Changes saved"}
