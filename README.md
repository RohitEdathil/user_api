# user_api

An api for managing users created as a part of IKS Internship selection process.
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MySQL](https://img.shields.io/badge/mysql-%2300000f.svg?style=for-the-badge&logo=mysql&logoColor=white)

# Installation

- ### Install dependencies using

```
pip install -r requirements.txt
```

- ### Set up environment variables
  - `SQL_HOST` : hostname of the database
  - `SQL_USER` : username of the database
  - `SQL_PASSWORD` : password of the database
  - `SQL_DATABASE` : name of the database
  - `SALT` : salt for password hashing

# Usage

All the scripts use the environment variables to connect to the database. So make sure to set them up before running the scripts.

- ### app&#46;py
  Contains all the main functions of the api.

Run the app using (In development mode)

```
uvicorn app:app --reload
```

For deployment, refer [here.](https://fastapi.tiangolo.com/deployment/)

- ### data_cleanup&#46;py
  Runs a script to automatically clean up the expired data in the database. Keep it running along with the app.

Run the script using

```
python data_cleanup.py
```

- ### rebuld_tables.py
  Runs a script to automatically rebuild the tables in the database. **It will drop all the tables and creates them agin**.
  This script should only be run when the model is updated.

Run the script using

```
python rebuild_tables.py
```

# Routes

- ## **/docs** or **/**

Swagger UI for the api. A simple way to get started with the api. Documentation provided as per openapi specification.

- ## **/invite**

  Creates an invitation for a new user.

  - ### Parameters:

    - `name`: Name of the user (Required, Max Length: 100)
    - `phone`: Phone number of the user (Required, Max Length: 20)
    - `email`: Email of the user (Required, Max Length: 100)
    - `alternate_email`: Alternate email of the user (Optional, Max Length: 100)
    - `organizations`: [

      { \
       `name`: Name of the organization (Required, Max Length: 100) \
       `role`: Role of the user in the organization (Required, Max Length: 100) \
       `valid_till`: Date when the user will be valid till (Optional) \
       } \
       . \
       . \
       ] (Must be inside a List, Optional)

  - ### Returns:
    - `invite_id`: Unique code to be for signing up
    - `expires_at`: Date and time when the invitation expires

- ## **/create**

  Signs up a user with an invitation code.

  - ### Parameters:

    - `invite_code`: Invitation code (Required, Max Length: 10)
    - `password`: Password of the user (Required, Max Length: 100)

  - ### Returns:
    - `message`: Success message if the user is signed up successfully

- ## **/login**

  Logs in a user.

  - ### Parameters:

    - `email`: Email of the user (Required, Max Length: 100)
    - `password`: Password of the user (Required, Max Length: 100)

  - ### Returns:
    - `token`: Token to be used for verifying the user
    - `expires_at`: Date and time when the token expires

- ## **/logout**

  Logs out a user.

  - ### Parameters:

    - `token`: Token to be used for verifying the user (Required, Max Length: 100)

  - ### Returns:
    - `message`: Success message if the user is logged out successfully

- ## **/edit**

  Edits the info of the currently logged in user.

  - ### Parameters:

    - `token` : A valid token obtained at the time of login
    - `name`: Name of the user (Optional, Max Length: 100)
    - `phone`: Phone number of the user (Optional, Max Length: 20)
    - `email`: Email of the user (Optional, Max Length: 100)
    - `alternate_email`: Alternate email of the user (Optional, Max Length: 100)
    - `profile_pic`: URL to the profile picture of the user (Optional, Max Length: 200)
    - `organizations`: [

      { \
       - `name`: Name of the organization (Required, Max Length: 100) \
       - `role`: Role of the user in the organization (Required, Max Length: 100) \
       - `valid_till`: Date when the user will be valid till (Optional) \
       } \
       . \
       . \

      ] (Must be inside a List, Optional, If provided all the existing roles of the user will be overwritten)

  - ### Returns:
    - `message`: Success message if editted successfully
