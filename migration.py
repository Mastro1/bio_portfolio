from sqlalchemy import create_engine
import pandas as pd
from app.database_setup import Base
import os

def migrate_to_local_db():
    """
    Migrate data from CSV and Excel files to the local SQLite database.
    """
    # Local database setup
    local_engine = create_engine("sqlite:///data/local_database.db")
    Base.metadata.create_all(local_engine)

    # Migrate Companies Table
    try:
        companies_df = pd.read_csv("data/companies.csv")
        companies_df.to_sql("companies", local_engine, if_exists="replace", index=False)
        print("Table 'companies' migrated successfully to local database.")
    except Exception as e:
        print(f"Error migrating 'companies' table to local database: {e}")

    # Migrate Midpoints Table
    try:
        midpoints_df = pd.read_csv("data/midpoints.csv")
        midpoints_df.rename(
            columns={
                "Water use": "water_use",
                "Climate change": "climate_change",
                "Land Use Transformation": "land_use_transformation",
                "Terrestial ecotoxicity": "terrestrial_ecotoxicity",
                "Trop. Ozone Formation (eco)": "tropical_ozone_formation",
                "Freshwater ecotoxicity": "freshwater_ecotoxicity",
                "Terrestrial acidification": "terrestrial_acidification",
                "Marine ecotoxicity": "marine_ecotoxicity",
                "Freshwater eutrophication": "freshwater_eutrophication",
                "Marine eutrophication": "marine_eutrophication",
            },
            inplace=True,
        )
        midpoints_df.to_sql("midpoints", local_engine, if_exists="replace", index=False)
        print("Table 'midpoints' migrated successfully to local database.")
    except Exception as e:
        print(f"Error migrating 'midpoints' table to local database: {e}")

    # Migrate Endpoints Table from Excel
    try:
        path_pathways = "data/norm_pathways_all_companies.xlsx"
        df_mar = pd.read_excel(path_pathways, sheet_name="marine", index_col=0)
        df_fre = pd.read_excel(path_pathways, sheet_name="freshwater", index_col=0)
        df_ter = pd.read_excel(path_pathways, sheet_name="terrestrial", index_col=0)

        endpoints_df = pd.DataFrame({
            "instrumentid": df_mar.index,
            "damage_to_marine_species": df_mar["Relative Score"],
            "damage_to_freshwater_species": df_fre["Relative Score"],
            "damage_to_terrestrial_species": df_ter["Relative Score"]
        }).reset_index(drop=True)

        endpoints_df["avg_score"] = endpoints_df[
            ['damage_to_freshwater_species', 'damage_to_marine_species', 'damage_to_terrestrial_species']
        ].mean(axis=1)
        endpoints_df["positive_score"] = 1 - endpoints_df["avg_score"]

        endpoints_df.to_sql("endpoints", local_engine, if_exists="replace", index=False)
        print("Table 'endpoints' migrated successfully to local database.")
    except Exception as e:
        print(f"Error migrating 'endpoints' table to local database: {e}")

        # Create Users Table
    try:
        print("Ensuring 'users' table exists in local database...")
        Base.metadata.create_all(local_engine)  # Create tables based on the User model
        print("Table 'users' created successfully in local database.")
    except Exception as e:
        print(f"Error creating 'users' table in local database: {e}")


def migrate_local_to_aws():
    """
    Migrate data from the local SQLite database to AWS RDS.
    """
    # Local database connection
    local_engine = create_engine("sqlite:///data/local_database.db")

    # AWS database connection
    aws_engine = create_engine(os.getenv("DATABASE_URL"))

    # Transfer each table
    try:
        tables = ["companies", "midpoints", "endpoints", "users"]
        for table in tables:
            df = pd.read_sql_table(table, local_engine)
            df.to_sql(table, aws_engine, if_exists="replace", index=False)
            print(f"Table '{table}' migrated successfully to AWS.")
    except Exception as e:
        print(f"Error migrating tables to AWS: {e}")


def main():
    """
    Perform the full migration: CSV/Excel -> Local DB -> AWS RDS.
    """
    print("Step 1: Migrating CSV and Excel files to local database...")
    migrate_to_local_db()

    print("\nStep 2: Migrating local database to AWS RDS...")
    migrate_local_to_aws()

    print("\nMigration completed successfully!")

if __name__ == "__main__":
    main()
