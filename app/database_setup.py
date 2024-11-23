from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy Engine and Base
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Table Definitions
class Company(Base):
    __tablename__ = "companies"
    instrumentid = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

class Midpoint(Base):
    __tablename__ = "midpoints"
    instrumentid = Column(String, primary_key=True)
    water_use = Column(Float, key="Water use")  # Maps to "Water use"
    climate_change = Column(Float, key="Climate change")  # Maps to "Climate change"
    land_use_transformation = Column(Float, key="Land Use Transformation")  # Maps to "Land Use Transformation"
    terrestrial_ecotoxicity = Column(Float, key="Terrestial ecotoxicity")  # Maps to "Terrestial ecotoxicity"
    tropical_ozone_formation = Column(Float, key="Trop. Ozone Formation (eco)")  # Maps to "Trop. Ozone Formation (eco)"
    freshwater_ecotoxicity = Column(Float, key="Freshwater ecotoxicity")  # Maps to "Freshwater ecotoxicity"
    terrestrial_acidification = Column(Float, key="Terrestrial acidification")  # Maps to "Terrestrial acidification"
    marine_ecotoxicity = Column(Float, key="Marine ecotoxicity")  # Maps to "Marine ecotoxicity"
    freshwater_eutrophication = Column(Float, key="Freshwater eutrophication")  # Maps to "Freshwater eutrophication"
    marine_eutrophication = Column(Float, key="Marine eutrophication")  # Maps to "Marine eutrophication"

class Endpoint(Base):
    __tablename__ = "endpoints"
    instrumentid = Column(String, primary_key=True)
    damage_to_marine_species = Column(Float, nullable=True)
    damage_to_freshwater_species = Column(Float, nullable=True)
    damage_to_terrestrial_species = Column(Float, nullable=True)
    avg_score = Column(Float, nullable=True)
    positive_score = Column(Float, nullable=True)


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Hashed password
    active = Column(Boolean, default=True)