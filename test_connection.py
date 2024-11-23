from sqlalchemy.orm import sessionmaker
from app.database_setup import engine, Company, Midpoint, Endpoint

# Create a session
Session = sessionmaker(bind=engine)

def test_connection():
    """
    Test the database connection and fetch basic records from each table.
    """
    try:
        # Test database connection
        connection = engine.connect()
        print("Connected to the database successfully!")
        connection.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return

    # Test queries
    session = Session()
    try:
        # Test Company table
        print("\nTesting 'Company' table...")
        companies = session.query(Company).limit(5).all()
        if companies:
            for company in companies:
                print(f"InstrumentID: {company.instrumentid}, Name: {company.name}, Description: {company.description}")
        else:
            print("No records found in 'Company' table.")

        # Test Midpoint table
        print("\nTesting 'Midpoint' table...")
        midpoints = session.query(Midpoint).limit(5).all()
        if midpoints:
            for midpoint in midpoints:
                print(f"InstrumentID: {midpoint.instrumentid}, Water Use: {midpoint.water_use}, Climate Change: {midpoint.climate_change}")
        else:
            print("No records found in 'Midpoint' table.")

        # Test Endpoint table
        print("\nTesting 'Endpoint' table...")
        endpoints = session.query(Endpoint).limit(5).all()
        if endpoints:
            for endpoint in endpoints:
                print(f"InstrumentID: {endpoint.instrumentid}, Avg Score: {endpoint.avg_score}, Positive Score: {endpoint.positive_score}")
        else:
            print("No records found in 'Endpoint' table.")

    except Exception as e:
        print(f"Error querying the database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_connection()
