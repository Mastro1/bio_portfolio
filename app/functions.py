from sqlalchemy.orm import sessionmaker
from .database_setup import engine, Company, Midpoint, Endpoint

Session = sessionmaker(bind=engine)

def compute_asset_impact(asset, perc):
    """
    Calculate the impact of an asset across endpoints.

    Args:
        asset (str): Asset identifier (instrumentid).
        perc (float): Percentage allocation of the asset.

    Returns:
        dict: Dictionary of endpoint impacts.
    """
    session = Session()
    try:
        endpoint = session.query(Endpoint).filter_by(instrumentid=asset).first()
        if not endpoint:
            raise ValueError(f"Endpoints for asset {asset} not found.")
        return {
            "Damage to marine species": endpoint.damage_to_marine_species * perc,
            "Damage to freshwater species": endpoint.damage_to_freshwater_species * perc,
            "Damage to terrestrial species": endpoint.damage_to_terrestrial_species * perc,
            "positive_score": endpoint.positive_score
        }
    finally:
        session.close()

def compute_asset_midpoint(asset):
    """
    Get midpoints for a specific company.

    Args:
        asset (str): Asset identifier (instrumentid).

    Returns:
        dict: Midpoints for the specified asset.
    """
    session = Session()
    try:
        midpoint = session.query(Midpoint).filter_by(instrumentid=asset).first()
        if not midpoint:
            raise ValueError(f"Midpoints for asset {asset} not found.")
        return {
            "Water use": midpoint.water_use,
            "Climate change": midpoint.climate_change,
            "Land Use Transformation": midpoint.land_use_transformation,
            "Terrestrial ecotoxicity": midpoint.terrestrial_ecotoxicity,
            "Trop. Ozone Formation (eco)": midpoint.tropical_ozone_formation,
            "Freshwater ecotoxicity": midpoint.freshwater_ecotoxicity,
            "Terrestrial acidification": midpoint.terrestrial_acidification,
            "Marine ecotoxicity": midpoint.marine_ecotoxicity,
            "Freshwater eutrophication": midpoint.freshwater_eutrophication,
            "Marine eutrophication": midpoint.marine_eutrophication,
        }
    finally:
        session.close()

def compute_portfolio_impact(portfolio, column="allocation"):
    """
    Calculate the total impact of a portfolio.

    Args:
        portfolio (DataFrame): Portfolio as a DataFrame with 'instrumentid' and allocation column.
        column (str): The column containing the allocation percentages.

    Returns:
        list[dict]: List of assets with their respective impacts.
    """
    session = Session()
    results = []
    try:
        for _, row in portfolio.iterrows():
            asset = row['instrumentid']
            perc = row[column]
            endpoint = session.query(Endpoint).filter_by(instrumentid=asset).first()
            if not endpoint:
                continue
            impacts = {
                "Damage to marine species": endpoint.damage_to_marine_species * perc,
                "Damage to freshwater species": endpoint.damage_to_freshwater_species * perc,
                "Damage to terrestrial species": endpoint.damage_to_terrestrial_species * perc,
            }
            results.append({
                "instrumentid": asset,
                "name": row.get("name", "Unknown"),
                "allocation": perc,
                **impacts,
            })
        return results
    finally:
        session.close()
