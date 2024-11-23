from sqlalchemy.orm import sessionmaker
from .database_setup import engine, Company, Endpoint, Midpoint
from .functions import compute_asset_impact, compute_asset_midpoint, compute_portfolio_impact
from .utils import generate_company_description
import pandas as pd
import os

# Initialize the SQLAlchemy session
Session = sessionmaker(bind=engine)


def process_portfolio(file):
    """
    Process the uploaded portfolio file and compute impacts.

    Args:
        file (FileStorage): The uploaded file object.

    Returns:
        list[dict]: List of assets with their respective impacts.
    """
    # Save the uploaded file temporarily
    upload_folder = os.getenv("UPLOAD_FOLDER", "data/uploads")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Read the portfolio into a DataFrame
    portfolio_df = pd.read_excel(file_path)

    # Calculate portfolio impacts
    results = compute_portfolio_impact(portfolio_df, column="allocation")
    return results


def search_companies(query, limit=10, exact_match=False):
    """
    Search for companies by instrumentid or name.

    Args:
        query (str): Search query (instrumentid or name).
        limit (int): Maximum number of results to return.
        exact_match (bool): Whether to match the query exactly.

    Returns:
        list[dict]: List of matching companies.
    """
    session = Session()
    try:
        query = query.lower()

        if exact_match:
            # Exact match by name or instrumentid
            matches = session.query(Company).filter(
                (Company.name.ilike(query)) |
                (Company.instrumentid.ilike(query))
            ).limit(limit).all()
        else:
            # Partial match
            matches = session.query(Company).filter(
                (Company.name.ilike(f"%{query}%")) |
                (Company.instrumentid.ilike(f"%{query}%"))
            ).limit(limit).all()

        # Convert to list of dictionaries
        return [
            {
                "instrumentid": match.instrumentid,
                "name": match.name,
                "description": match.description
            }
            for match in matches
        ]
    finally:
        session.close()


def get_company_details(company_id):
    """
    Get details for a specific company by instrumentid.

    Args:
        company_id (str): The instrumentid of the company.

    Returns:
        dict: Company details including impacts, midpoints, and description.
    """
    session = Session()
    try:
        # Query the company
        company = session.query(Company).filter_by(instrumentid=company_id).first()
        if not company:
            raise ValueError(f"Company with ID {company_id} not found.")

        # Check if description exists
        if not company.description or company.description.strip() == "":
            # Generate a new description
            description = generate_company_description(company.name)
            company.description = description  # Update the description in the database
            session.commit()  # Save changes
        else:
            description = company.description

        # Compute the impact for a single company
        impact = compute_asset_impact(company_id, 100)  # Assume 100% allocation

        # Compute midpoints for a single company
        midpoints = compute_asset_midpoint(company_id)

        return {
            "company_id": company_id,
            "company_name": company.name,
            "impact": impact,
            "midpoints": midpoints,
            "description": description,
        }
    finally:
        session.close()
