from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import OperationalError, IntegrityError
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
               - `valid_till`: Date when the user will be valid till (Optional, Max Length: 100) \\
            } \\
            . \\
            . \\
        ]
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

# TODO: Remove this endpoint in production


@app.post("/query")
def query(data: dict):
    """
    Execute SQL queries.
    """
    return engine.execute(data['query']).fetchall().__str__()
