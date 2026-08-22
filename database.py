import os     # built-in python module that allows program to connect with operating system 
import enum   # built-in python module that lets us define a fixed set of allowed values.
from dotenv import load_dotenv  # this comes from python-dotenv package , allows python to read variables from .env file

# SQLAlchemy provides support to interact with PostgreSQL databases using Python. It provides an Object Relational Mapping (ORM) system that maps database tables to Python classes.

from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey
# create_engine is used to create an SQLAlchemy engine which is responsible for establishing and managing communication with the database.
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
# declarative_base creates the base class from which the database models will inherit.
# sessionmaker is used to create database_sessions
# relationship is used by SQLAlchemy to represent relationships between Python models.


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") # Python asks the os for a database url and stores it in the given variable

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# autocommit=False - means database changes aren't automatically committed immediately.
# autoflush=False - tells SQLAlchemy not to automatically flush pending changes to the database before certain operations.
Base = declarative_base()  # creating the base class for the SQLAlchemy models.

# --- DEFINITIONS REQUIRED BY main.py ---

class RoleEnum(str, enum.Enum):
    CAMP_COORDINATOR = "CAMP_COORDINATOR"
    DONOR = "DONOR"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.DONOR)

class ReliefCamp(Base):
    __tablename__ = "relief_camps"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district = Column(String, nullable=False)
    contact_person = Column(String, nullable=False)
    inventories = relationship("ResourceInventory", back_populates="camp")

class ResourceInventory(Base):
    __tablename__ = "resource_inventories"
    id = Column(Integer, primary_key=True, index=True)
    camp_id = Column(Integer, ForeignKey("relief_camps.id"))
    item_name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    required_quantity = Column(Integer, nullable=False)
    fulfilled_quantity = Column(Integer, default=0)
    camp = relationship("ReliefCamp", back_populates="inventories")

# Create tables in PostgreSQL automatically
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
