from flask import Blueprint, jsonify, request, send_file
from ..models.nex_score import NexScore, db
from flasgger import swag_from # type: ignore
from ..schemas import nex_score_schema
from ..utils import organize_data_by_region
from sqlalchemy import func, and_
from flask import request
import pandas as pd # type: ignore
from io import BytesIO

bp = Blueprint('nex_score', __name__, url_prefix='/nex-score')

@bp.route('/', methods=['GET'])
@swag_from({
    'summary': 'Get the latest nex score',
    'parameters': [
        {
            'name': 'type',
            'in': 'query',
            'type': 'string',
            'enum': ['influencer', 'detractor', 'neutral'],
            'required': False,
            'default': 'influencer',
            'description': 'The type of data to retrieve. Options are influencer, detractor, and neutral.'
        },
        {
            'name': 'region',
            'in': 'query',
            'type': 'string',
            'enum': ['CENTRAL', 'WEST', 'SOUTH', 'NORTHEAST'],
            'required': False,
            'description': 'The type of data to retrieve. Options are CENTRAL, WEST, NORTHEAST, and SOUTH.'
        }
    ],
    'responses': {
        200: {
            'description': 'A list of market data',
            'examples': {
                'application/json': {
                    'data': [
                        {
                            'label': 'market1',
                            'value': 62.84,
                            'region': 'region1',
                            'update_date': 'YYYY-MM-DD',
                            'count': 133251
                        }
                    ],
                    'type': 'influencer'
                }
            }
        },
        500: {
            'description': 'Internal Server Error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Internal Server Error'
                    }
                }
            }
        }
    }
})
def get_nex_score():
    try:
        # Get the 'type' parameter from the query string
        type_param = request.args.get('type') or 'influencer'
        region = request.args.get('region')

        print(region,type_param)

        subquery = (
            db.session.query(
                NexScore.market,
                NexScore.region,
                func.max(NexScore.update_date).label('latest_update')
            )
            .group_by(NexScore.market, NexScore.region)
            .subquery()
        )

        # Define the fields to be selected based on the value of the 'type' parameter
        fields = [
            NexScore.market,
            NexScore.region,
            NexScore.update_date
        ]

        if type_param and type_param.lower() == 'influencer':
            fields.extend([
                NexScore.influencer_count,
                NexScore.influencer_perc
            ])
        if type_param and type_param.lower() == 'detractor':
            fields.extend([
                NexScore.detractor_count,
                NexScore.detractor_perc
            ])
        if type_param and type_param.lower() == 'neutral':
            fields.extend([
                NexScore.neutral_count,
                NexScore.neutral_perc
            ])

        # Join subquery with the main table
        query = db.session.query(*fields).join(
            subquery,
            and_(
                NexScore.market == subquery.c.market,
                NexScore.region == subquery.c.region,
                NexScore.update_date == subquery.c.latest_update
            )
        )

        if region and region != 'ALL REGIONS':
            query = query.filter(NexScore.region == region)

        # Execute the query
        result = query.all()

        data = []
        # for row in result:
        #     entry = {
        #         'label': row.market,
        #         'value': row.neutral_perc or row.influencer_perc or row.detractor_perc,
        #         'region': row.region,
        #         'update_date': row.update_date.strftime('%Y-%m-%d'),
        #         'percentage': row.percentage
        #     }
        #     data.append(entry)
        for row in result:
            entry = {
                'label': row.market,
                'value': row.neutral_perc if type_param == 'neutral' else row.influencer_perc if type_param == 'influencer' else row.detractor_perc,
                'region': row.region,
                'update_date': row.update_date.strftime('%Y-%m-%d'),
                'count': row.neutral_count if type_param == 'neutral' else row.influencer_count if type_param == 'influencer' else row.detractor_count
            }
            data.append(entry)


        # Serialize the results using the schema
        # data = nex_score_schema.dump(result)
        
        finalData = {}
        dataset = []
        if data:
            distinct_regions = set(entry['region'] for entry in data)
            organized_dataset = organize_data_by_region(distinct_regions, data)
            # obj = {
            #     "label": "national",
            #     "children": organized_dataset
            # }
            # finalData = obj
            dataset = organized_dataset

        return jsonify({
            # 'data': finalData
            'data': dataset,
            'type' : type_param
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/trends', methods=['GET'])
@swag_from({
    'summary': 'Get trend data for influencer, detractor, and neutral percentages',
    'parameters': [
        {
            'name': 'region',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Region name to filter the data (optional)'
        },
        {
            'name': 'market',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Market name to filter the data (optional)'
        },
        {
            'name': 'timeframe',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Timeframe for the trend data (monthly, quarterly, yearly). Defaults to "monthly" if not provided',
            'enum': ['monthly', 'quarterly', 'yearly']
        }
    ],
    'responses': {
        '200': {
            'description': 'Trend data for the specified region and market',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'timeframe': {
                                    'type': 'string',
                                    'description': 'Time period for the trend data'
                                },
                                'influencer_perc': {
                                    'type': 'number',
                                    'format': 'float',
                                    'description': 'Average influencer percentage'
                                },
                                'detractor_perc': {
                                    'type': 'number',
                                    'format': 'float',
                                    'description': 'Average detractor percentage'
                                },
                                'neutral_perc': {
                                    'type': 'number',
                                    'format': 'float',
                                    'description': 'Average neutral percentage'
                                }
                            }
                        }
                    }
                }
            }
        },
        '400': {
            'description': 'Invalid period parameter'
        },
        '404': {
            'description': 'No data found'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def get_trend():
    region = request.args.get('region')
    market = request.args.get('market')
    timeframe = request.args.get('timeframe', 'monthly')  # Default to 'monthly' if not provided
    
    try:
        query = NexScore.query
        
        if region:
            query = query.filter(NexScore.region == region)
        if market:
            query = query.filter(NexScore.market == market)
        
        records = query.order_by(NexScore.update_date.asc()).all()
        
        if not records:
            return jsonify({'message': 'No data found'}), 404
        
        data = nex_score_schema.dump(records)
        
       # Convert the 'update_date' column to a datetime object
        df = pd.DataFrame(data)

        if df.empty:
            return jsonify({'message': 'No data found'}), 404
        
        df['update_date'] = pd.to_datetime(df['update_date'])

        if timeframe == 'monthly':
            df['timeframe'] = df['update_date'].dt.to_period('M').dt.to_timestamp()
        elif timeframe == 'quarterly':
            df['timeframe'] = df['update_date'].dt.to_period('Q').dt.to_timestamp()
        elif timeframe == 'yearly':
            df['timeframe'] = df['update_date'].dt.to_period('Y').dt.to_timestamp()
        else:
            return jsonify({'error': 'Invalid period parameter'}), 400

        # 2 decimal places
        trend_data = df.groupby('timeframe').agg({
            'influencer_perc': lambda x: round(x.mean(), 1),
            'detractor_perc': lambda x: round(x.mean(), 1),
            'neutral_perc': lambda x: round(x.mean(), 1)
        }).reset_index()

        # Sort the data by 'timeframe' in ascending order
        trend_data = trend_data.sort_values(by='timeframe', ascending=True)

        if timeframe == 'monthly':
            trend_data['label'] = trend_data['timeframe'].dt.strftime("%b'%y").str.upper()
        elif timeframe == 'quarterly':
            trend_data['label'] = trend_data['timeframe'].dt.to_period('Q').dt.strftime('Q%q\'%y')
        elif timeframe == 'yearly':
            trend_data['label'] = trend_data['timeframe'].dt.strftime('%Y')

        # Convert the DataFrame to a dictionary
        trend_dict = trend_data.to_dict(orient='records')

        # Return the JSON response with the data
        return jsonify({'data': trend_dict})

        # return jsonify({'data': trend_data.to_dict(orient='records')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/percentage', methods=['GET'])
@swag_from({
    'summary': 'Get average influencer, detractor, and neutral percentages for the latest update date.',
    'parameters': [
        {
            'name': 'region',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Region name to filter the data (optional)'
        }
    ],
    'responses': {
        '200': {
            'description': 'Average percentages for influencer, detractor, and neutral categories for the latest update date.',
            'schema': {
                'type': 'object',
                'properties': {
                    'influencer_perc': {
                        'type': 'number',
                        'format': 'float',
                        'description': 'Average influencer percentage'
                    },
                    'detractor_perc': {
                        'type': 'number',
                        'format': 'float',
                        'description': 'Average detractor percentage'
                    },
                    'neutral_perc': {
                        'type': 'number',
                        'format': 'float',
                        'description': 'Average neutral percentage'
                    },
                    'update_date': {
                        'type': 'string',
                        'format': 'date',
                        'description': 'The latest update date in YYYY-MM-DD format'
                    }
                }
            }
        },
        '400': {
            'description': 'Bad Request'
        },
        '404': {
            'description': 'No data found'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def get_perc():
    region = request.args.get('region')

    try:
        query = NexScore.query

        if region:
            query = query.filter(NexScore.region == region)
        
        latest_update_date = db.session.query(db.func.max(NexScore.update_date)).scalar()
        if not latest_update_date:
            return jsonify({'message': 'No data found'}), 404

        latest_records = query.filter(NexScore.update_date == latest_update_date).all()
        
        if not latest_records:
            return jsonify({'message': 'No data found'}), 404
        
        data = nex_score_schema.dump(latest_records)
        
        df = pd.DataFrame(data)
        influencer_perc = round(df['influencer_perc'].mean(), 1)
        detractor_perc = round(df['detractor_perc'].mean(), 1)
        neutral_perc = round(df['neutral_perc'].mean(), 1)
        
        return jsonify({
            'influencer_perc': influencer_perc,
            'detractor_perc': detractor_perc,
            'neutral_perc': neutral_perc,
            'update_date': latest_update_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.route('/score-comparison', methods=['GET'])
@swag_from({
    'summary': 'Get score for a specific region, market, and month.',
    'parameters': [
        {
            'name': 'region',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Region name (e.g., CENTRAL)'
        },
        {
            'name': 'market',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Market name (e.g., ARKANSAS)'
        },
        {
            'name': 'month',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Month in "MMM\'YY" format (e.g., APR\'24)'
        }
    ],
    'responses': {
        '200': {
            'description': 'A JSON object containing the score data and differences.',
            'schema': {
                'type': 'object',
                'properties': {
                    'data': {
                        'type': 'object',
                        'properties': {
                            'current_month': {
                                'type': 'object',
                                'description': 'Data for the current month'
                            },
                            'differences': {
                                'type': 'object',
                                'description': 'Differences between the current and previous month',
                                'properties': {
                                    'timeframe': {
                                        'type': 'string',
                                        'description': 'Timeframe of the current month'
                                    },
                                    'influencer_perc_diff': {
                                        'type': 'number',
                                        'format': 'float',
                                        'description': 'Difference in influencer percentage'
                                    },
                                    'detractor_perc_diff': {
                                        'type': 'number',
                                        'format': 'float',
                                        'description': 'Difference in detractor percentage'
                                    },
                                    'neutral_perc_diff': {
                                        'type': 'number',
                                        'format': 'float',
                                        'description': 'Difference in neutral percentage'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '400': {
            # 'description': 'Missing required parameters'
            'description': 'Region/Market/Month is required'
        },
        '404': {
            'description': 'No data found'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def get_score():

    region = request.args.get('region')   # CENTRAL
    market = request.args.get('market')   # ARKANSAS
    month_query = request.args.get('month')     # "APR'24"

    # Check for mandatory parameters
    if not region:
        return jsonify({'error': 'Region is required'}), 400
    if not market:
        return jsonify({'error': 'Market is required'}), 400
    if not month_query:
        return jsonify({'error': 'Month is required'}), 400

    try:
        # Start building the query
        query = NexScore.query

        # Filter based on region and market
        query = query.filter(NexScore.region == region, NexScore.market == market)

        records = query.all()
        
        if not records:
            return jsonify({'message': 'No data found'}), 404
        
        data = nex_score_schema.dump(records)
        
        # Convert the 'update_date' column to a datetime object and extract the month
        df = pd.DataFrame(data)
        df['update_date'] = pd.to_datetime(df['update_date'])
        df['timeframe'] = df['update_date'].dt.to_period('M').dt.to_timestamp().dt.strftime("%b'%y").str.upper()

        avg_data = df.groupby('timeframe').agg({
            'influencer_perc': lambda x: round(x.mean(), 1),
            'detractor_perc': lambda x: round(x.mean(), 1),
            'neutral_perc': lambda x: round(x.mean(), 1),

            'influencer_count': lambda x: round(x.mean()),
            'detractor_count': lambda x: round(x.mean()),
            'neutral_count': lambda x: round(x.mean())
        }).reset_index()

        # Find the index of the specified month
        if month_query in avg_data['timeframe'].values:
            month_index = avg_data.index[avg_data['timeframe'] == month_query].tolist()[0]

            # Check if there is a next row
            if month_index + 1 < len(avg_data):
                next_month_index = month_index + 1

                # Get the data for the specified month and the next month
                current_month = avg_data.iloc[month_index]
                prev_month = avg_data.iloc[next_month_index]

                # Calculate the differences
                differences = {
                    'timeframe': current_month['timeframe'],
                    'influencer_perc_diff': round(current_month['influencer_perc'] - prev_month['influencer_perc'], 2),
                    'detractor_perc_diff': round(current_month['detractor_perc'] - prev_month['detractor_perc'], 2),
                    'neutral_perc_diff': round(current_month['neutral_perc'] - prev_month['neutral_perc'], 2)
                }

                result = {
                    'current_month': current_month.to_dict(),
                    # 'prev_month': prev_month.to_dict(),
                    'differences': differences
                }
            else:
                # No next month data available
                result = {
                    'current_month': avg_data.iloc[month_index].to_dict(),
                    # 'prev_month': None,
                    'differences': None
                }
        else:
            return jsonify({'message': 'Month not found in data'}), 404

        return jsonify({'data': result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@bp.route('/excel', methods=['GET'])
@swag_from({
    'summary': 'Get json data for NexScore data that is converted into an excel',
    'parameters': [
        {
            'name': 'region',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Region name to filter the data (optional)'
        },
        {
            'name': 'market',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Market name to filter the data (optional)'
        },
    ],
    'responses': {
        '200': {
            
        },
        '404': {
            'description': 'No data found'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def get_excel():
    region = request.args.get('region')
    market = request.args.get('market')

    try:
        query = NexScore.query
    
        if region:
            query = query.filter(NexScore.region == region)
        if market:
            query = query.filter(NexScore.market == market)
        
        records = query.all()
        
        if not records:
            return jsonify({'message': 'No data found'}), 404
        
        data = nex_score_schema.dump(records)
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
