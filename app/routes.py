from flask import Blueprint, request, jsonify, render_template, url_for
from .services import process_portfolio, get_company_details, search_companies
from .utils import calculate_score_color
from flask_limiter import Limiter
from sqlalchemy.orm import sessionmaker
from .database_setup import engine, Endpoint, Company
from authlib.integrations.flask_client import OAuth
from flask_limiter.util import get_remote_address
import plotly.graph_objs as go
import json

main = Blueprint('main', __name__)

Session = sessionmaker(bind=engine)

# Index with company search
@main.route('/', methods=['GET', 'POST'])
def index():
    session = Session()
    try:
        # Join the `endpoints` and `companies` tables to fetch names
        top_companies = (
            session.query(Endpoint.instrumentid, Endpoint.positive_score, Company.name)
            .join(Company, Endpoint.instrumentid == Company.instrumentid)
            .order_by(Endpoint.positive_score.desc())
            .limit(5)
            .all()
        )

        worst_companies = (
            session.query(Endpoint.instrumentid, Endpoint.positive_score, Company.name)
            .join(Company, Endpoint.instrumentid == Company.instrumentid)
            .order_by(Endpoint.positive_score.asc())
            .limit(5)
            .all()
        )

        # Format results for the template
        top_companies = [
            {"instrumentid": c[0], "score": c[1] * 100, "name": c[2]} for c in top_companies
        ]
        worst_companies = [
            {"instrumentid": c[0], "score": c[1] * 100, "name": c[2]} for c in worst_companies
        ]

        return render_template(
            "index.html",
            top_companies=top_companies,
            worst_companies=worst_companies,
        )
    finally:
        session.close()



# Portfolio calculation (new route)
@main.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    """
    Separate route for portfolio calculation.
    """
    if request.method == 'POST':
        # Handle file upload and portfolio processing here
        pass  # Placeholder for future implementation
    return render_template('portfolio.html')


limiter = Limiter(get_remote_address)

company_routes = Blueprint('company', __name__)

@company_routes.route('/company/search', methods=['GET'])
def search():
    """
    Search for companies by query (instrumentid or name).
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        results = search_companies(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#@limiter.limit("5 per minute")  # Allow 5 requests per minute
@main.route('/company/<string:company_id>', methods=['GET'])
def company_details(company_id):
    try:
        details = get_company_details(company_id)

        # Prepare data for the gauge color
        positive_score = details["impact"]["positive_score"] * 100  # Scale score to 0-100
        score_color = calculate_score_color(positive_score)

        # Prepare radar plot data for midpoints
        radar_data = {
            "categories": list(details["midpoints"].keys()),
            "values": list(details["midpoints"].values()),
        }

        return render_template(
            "company_details.html",
            company_name=details["company_name"],
            description=details["description"],
            positive_score=positive_score,
            score_color=score_color,
            endpoints={
                "Marine": details["impact"]["Damage to marine species"],
                "Freshwater": details["impact"]["Damage to freshwater species"],
                "Terrestrial": details["impact"]["Damage to terrestrial species"],
            },
            radar_data=json.dumps(radar_data),
        )
    except ValueError as e:
        return render_template("error.html", error=str(e))
    

