from ..models.nex_score import NexScore
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

def get_dropdown_val():
    try:
        # Query distinct market and region values
        distinct_values = NexScore.query.with_entities(NexScore.market, NexScore.region).distinct().all()
        
        # Create a list to store the data
        data = [{'region': region, 'market': market} for market, region in distinct_values]
        
        # Construct the response object
        response = {'data': data}

        return jsonify(response)
    except Exception as e:
        # If an exception occurs, return an error response
        return jsonify({"error": str(e)}), 500
