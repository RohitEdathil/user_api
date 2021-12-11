from datetime import datetime
from sqlalchemy import Column, Table, Boolean, ForeignKey, String, MetaData, Sequence, Integer
from sqlalchemy.sql.sqltypes import DateTime
from app import engine

metadata = MetaData()

# Handles user data
users = Table(
    'users', metadata,
    Column('id', Integer(), Sequence('user_id'), primary_key=True),
    Column('name', String(100), nullable=False),
    Column('phone_number', String(20), nullable=False, unique=True),
    Column('email', String(100), nullable=False, unique=True),
    Column('alternate_email', String(100)),

    Column('activated', Boolean(), default=False),
    Column('password', String(100)),
    Column('invite_code', String(100), nullable=False),
    Column('invited_at', DateTime(), default=datetime.now()),
)

# Handles Organization data
organizations = Table(
    'organizations', metadata,
    Column('id', Integer(), Sequence('organization_id'), primary_key=True),
    Column('user', ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('name', String(100), nullable=False),
    Column('role', String(100), nullable=False),
    Column('valid_till', DateTime()),
)

# Handles login data
sessions = Table(
    'sessions', metadata,
    Column('user', ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('token', String(100), nullable=False, unique=True),
    Column('created_at', DateTime(), default=datetime.now()),
)
