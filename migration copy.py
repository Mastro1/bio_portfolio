import pandas as pd
import sqlite3
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database URLs
LOCAL_DB_URL = "sqlite:///data/database.db"
AWS_RDS_URL = os.getenv("DATABASE_URL")  # Make sure this is in your .env file

# Create SQLAlchemy engines
local_engine = create_engine(LOCAL_DB_URL)
aws_engine = create_engine(AWS_RDS_URL)


def migrate_table(table_name):
    """
    Migrate a single table from SQLite to PostgreSQL.
    
    Args:
        table_name (str): Name of the table to migrate.
    """
    with sqlite3.connect("data/database.db") as conn:
        # Read the table from SQLite
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        # Write the data to AWS RDS
        df.to_sql(table_name, aws_engine, if_exists="replace", index=False)
        print(f"Table '{table_name}' migrated successfully.")


def rename_midpoints_columns():
    """
    Rename columns in the 'midpoints' table to use snake_case for consistency.
    """
    rename_queries = [
        'ALTER TABLE midpoints RENAME COLUMN "Water use" TO water_use;',
        'ALTER TABLE midpoints RENAME COLUMN "Climate change" TO climate_change;',
        'ALTER TABLE midpoints RENAME COLUMN "Land Use Transformation" TO land_use_transformation;',
        'ALTER TABLE midpoints RENAME COLUMN "Terrestial ecotoxicity" TO terrestrial_ecotoxicity;',
        'ALTER TABLE midpoints RENAME COLUMN "Trop. Ozone Formation (eco)" TO tropical_ozone_formation;',
        'ALTER TABLE midpoints RENAME COLUMN "Freshwater ecotoxicity" TO freshwater_ecotoxicity;',
        'ALTER TABLE midpoints RENAME COLUMN "Terrestrial acidification" TO terrestrial_acidification;',
        'ALTER TABLE midpoints RENAME COLUMN "Marine ecotoxicity" TO marine_ecotoxicity;',
        'ALTER TABLE midpoints RENAME COLUMN "Freshwater eutrophication" TO freshwater_eutrophication;',
        'ALTER TABLE midpoints RENAME COLUMN "Marine eutrophication" TO marine_eutrophication;',
    ]
    
    with aws_engine.connect() as connection:
        for query in rename_queries:
            try:
                connection.execute(query)
                print(f"Executed: {query}")
            except Exception as e:
                print(f"Error executing query '{query}': {e}")



def migrate_csv_to_rds():
    """
    Migrate data from CSV files to PostgreSQL.
    """
    # Companies Table
    companies_df = pd.read_csv("data/companies.csv")
    companies_df.to_sql("companies", aws_engine, if_exists="replace", index=False)
    print("Table 'companies' migrated successfully from CSV.")

    # Midpoints Table
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

    midpoints_df.to_sql("midpoints", aws_engine, if_exists="replace", index=False)

    print("Table 'midpoints' migrated successfully from CSV.")


def migrate_excel_to_rds():
    """
    Migrate data from Excel files to PostgreSQL.
    """
    # Pathways file with three sheets
    path_pathways = "data/norm_pathways_all_companies.xlsx"
    df_mar = pd.read_excel(path_pathways, sheet_name="marine", index_col=0)
    df_fre = pd.read_excel(path_pathways, sheet_name="freshwater", index_col=0)
    df_ter = pd.read_excel(path_pathways, sheet_name="terrestrial", index_col=0)

    # Combine into a single DataFrame
    endpoints_df = pd.DataFrame({
        "instrumentid": df_mar.index,
        "damage_to_marine_species": df_mar["Relative Score"],
        "damage_to_freshwater_species": df_fre["Relative Score"],
        "damage_to_terrestrial_species": df_ter["Relative Score"]
    }).reset_index(drop=True)

    # Calculating avg and positive score (to display)
    endpoints_df["avg_score"] = endpoints_df[['damage_to_marine_species', 
                                              'damage_to_freshwater_species', 
                                              'damage_to_terrestrial_species']].mean(axis=1)
    
    endpoints_df["positive_score"] = 1 - endpoints_df["avg_score"]

    # Write the data to AWS RDS
    endpoints_df.to_sql("endpoints", aws_engine, if_exists="replace", index=False)
    print("Table 'endpoints' migrated successfully from Excel.")


def validate_migration():
    """
    Validate the migration by checking the tables and their contents on AWS RDS.
    """
    inspector = inspect(aws_engine)

    # List all tables in the AWS RDS database
    tables = inspector.get_table_names()
    print("\nTables in the AWS RDS database:")
    print(tables)

    # Check contents of each table
    for table in tables:
        query = f"SELECT COUNT(*) AS count FROM {table}"
        count = pd.read_sql_query(query, aws_engine)["count"].iloc[0]
        print(f"Table '{table}' contains {count} records.")

        # Optionally, print a preview of the data
        print(f"Preview of '{table}':")
        preview = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", aws_engine)
        print(preview)
        print()


def main():
    """
    Main migration script to transfer all data from local sources to AWS RDS.
    """
    print("Starting migration...")

    # Migrate tables from SQLite database
    tables = ["companies", "midpoints", "endpoints"]  # Add any other tables as needed
    for table in tables:
        migrate_table(table)

    # Migrate CSV files to RDS
    migrate_csv_to_rds()

    # Migrate Excel files to RDS
    migrate_excel_to_rds()

    print("Migration completed successfully!")

    # Validate the migration
    print("\nValidating the migration...")
    validate_migration()


if __name__ == "__main__":
    main()
