from sqlalchemy import Column,  Boolean, ForeignKey, String, Sequence, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer(), Sequence('user_id'), primary_key=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    alternate_email = Column(String(100))
    profile_pic = Column(String(200))

    activated = Column(Boolean(), default=False)
    password = Column(String(100))
    invite_code = Column(String(10), nullable=False)
    invited_at = Column(DateTime(), nullable=False)


class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer(), Sequence('organization_id'), primary_key=True)
    user = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    valid_till = Column(DateTime())


class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer(), Sequence('session_id'), primary_key=True)
    user = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(), nullable=False)
