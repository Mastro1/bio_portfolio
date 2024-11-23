import pandas as pd
import sqlite3
from sqlalchemy import create_engine, Column, String, Float, MetaData, Table
from sqlalchemy.orm import declarative_base, sessionmaker

# Initialize SQLAlchemy
DATABASE_URL = "sqlite:///data/database.db"  # For local development
engine = create_engine(DATABASE_URL)
Base = declarative_base()
metadata = MetaData()

# Define Models
class Company(Base):
    __tablename__ = 'companies'
    instrumentid = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)

class Midpoint(Base):
    __tablename__ = 'midpoints'
    instrumentid = Column(String, primary_key=True)
    water_use = Column(Float)
    climate_change = Column(Float)
    land_use_transformation = Column(Float)
    terrestrial_ecotoxicity = Column(Float)
    tropical_ozone_formation = Column(Float)
    freshwater_ecotoxicity = Column(Float)
    terrestrial_acidification = Column(Float)
    marine_ecotoxicity = Column(Float)
    freshwater_eutrophication = Column(Float)
    marine_eutrophication = Column(Float)

class Endpoint(Base):
    __tablename__ = 'endpoints'
    instrumentid = Column(String, primary_key=True)
    damage_to_marine_species = Column(Float)
    damage_to_freshwater_species = Column(Float)
    damage_to_terrestrial_species = Column(Float)

# Create Tables
def create_tables():
    Base.metadata.create_all(engine)

# Load Data into Database
def transform_csv_to_sql():
    # Initialize Database Session
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Companies Table
    companies_df = pd.read_csv("data/companies.csv")
    companies = [
        Company(
            instrumentid=row['instrumentid'],
            name=row['name'],
            description=row.get('description', '')
        )
        for _, row in companies_df.iterrows()
    ]
    session.bulk_save_objects(companies)

    # 2. Midpoints Table
    midpoints_df = pd.read_csv("data/midpoints.csv")
    midpoints = [
        Midpoint(
            instrumentid=row['instrumentid'],
            water_use=row['Water use'],
            climate_change=row['Climate change'],
            land_use_transformation=row['Land Use Transformation'],
            terrestrial_ecotoxicity=row['Terrestial ecotoxicity'],
            tropical_ozone_formation=row['Trop. Ozone Formation (eco)'],
            freshwater_ecotoxicity=row['Freshwater ecotoxicity'],
            terrestrial_acidification=row['Terrestrial acidification'],
            marine_ecotoxicity=row['Marine ecotoxicity'],
            freshwater_eutrophication=row['Freshwater eutrophication'],
            marine_eutrophication=row['Marine eutrophication']
        )
        for _, row in midpoints_df.iterrows()
    ]
    session.bulk_save_objects(midpoints)

    # 3. Endpoints Table
    path_pathways = "data/norm_pathways_all_companies.xlsx"
    df_mar = pd.read_excel(path_pathways, sheet_name="marine", index_col=0)
    df_fre = pd.read_excel(path_pathways, sheet_name="freshwater", index_col=0)
    df_ter = pd.read_excel(path_pathways, sheet_name="terrestrial", index_col=0)

    # Merge all endpoint data into a single DataFrame
    endpoints_df = pd.DataFrame({
        'instrumentid': df_mar.index,
        'damage_to_marine_species': df_mar['Relative Score'],
        'damage_to_freshwater_species': df_fre['Relative Score'],
        'damage_to_terrestrial_species': df_ter['Relative Score']
    }).reset_index(drop=True)

    endpoints = [
        Endpoint(
            instrumentid=row['instrumentid'],
            damage_to_marine_species=row['damage_to_marine_species'],
            damage_to_freshwater_species=row['damage_to_freshwater_species'],
            damage_to_terrestrial_species=row['damage_to_terrestrial_species']
        )
        for _, row in endpoints_df.iterrows()
    ]
    session.bulk_save_objects(endpoints)

    # Commit and close the session
    session.commit()
    session.close()

if __name__ == "__main__":
    # Create tables and populate them
    create_tables()
    transform_csv_to_sql()
