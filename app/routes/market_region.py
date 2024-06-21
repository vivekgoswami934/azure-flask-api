

from flask import Blueprint, jsonify
from ..models.nex_score import NexScore, db
from ..schemas import nex_score_schema
from ..utils import organize_data_by_region
from sqlalchemy import func, and_
from flask import request
from ..controller.market_region_controller import get_dropdown_val


bp = Blueprint('market_region', __name__, url_prefix='/market-region')


# @bp.route('/', methods=['GET'])
# def get_dropdown_values():
#     """
#     Get distinct markets and regions
#     ---
#     responses:
#       200:
#         description: A list of markets and regions
#         schema:
#           type: object
#           properties:
#             data:
#               type: array
#               items:
#                 type: object
#                 properties:
#                   region:
#                     type: string
#                     example: "region1"
#                   market:
#                     type: string
#                     example: "market1"
#       500:
#         description: Internal Server Error
#     """
#     try:
#         # Query distinct market and region values
#         distinct_values = NexScore.query.with_entities(NexScore.market, NexScore.region).distinct().all()
        
#         # Create a list to store the data
#         data = [{'region': region, 'market': market} for market, region in distinct_values]
        
#         # Construct the response object
#         response = {'data': data}

#         return jsonify(response)
#     except Exception as e:
#         # If an exception occurs, return an error response
#         return jsonify({"error": str(e)}), 500



@bp.route('/', methods=['GET'])
def get_dropdown_values():
    """
    Get distinct markets and regions
    ---
    responses:
      200:
        description: A list of markets and regions
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  region:
                    type: string
                    example: "region1"
                  market:
                    type: string
                    example: "market1"
      500:
        description: Internal Server Error
    """
    return get_dropdown_val()