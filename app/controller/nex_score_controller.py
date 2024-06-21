from sqlalchemy import func, and_
from ..models.nex_score import NexScore, db
from ..utils import organize_data_by_region
import pandas as pd # type: ignore
from ..schemas import nex_score_schema




def get_nex_score_data(type_param, region):
    subquery = (
        db.session.query(
            NexScore.market,
            NexScore.region,
            func.max(NexScore.update_date).label('latest_update')
        )
        .group_by(NexScore.market, NexScore.region)
        .subquery()
    )

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

    result = query.all()

    data = []
    for row in result:
        entry = {
            'label': row.market,
            'value': row.neutral_perc if type_param == 'neutral' else row.influencer_perc if type_param == 'influencer' else row.detractor_perc,
            'region': row.region,
            'update_date': row.update_date.strftime('%Y-%m-%d'),
            'count': row.neutral_count if type_param == 'neutral' else row.influencer_count if type_param == 'influencer' else row.detractor_count
        }
        data.append(entry)

    dataset = []
    if data:
        distinct_regions = set(entry['region'] for entry in data)
        organized_dataset = organize_data_by_region(distinct_regions, data)
        dataset = organized_dataset

    return dataset, type_param

def get_trend_data(region, market, timeframe):
    query = NexScore.query
    
    if region:
        query = query.filter(NexScore.region == region)
    if market:
        query = query.filter(NexScore.market == market)
    
    records = query.order_by(NexScore.update_date.asc()).all()
    
    if not records:
        return {'message': 'No data found', 'status': 404}
    
    data = nex_score_schema.dump(records)
    df = pd.DataFrame(data)

    if df.empty:
        return {'message': 'No data found', 'status': 404}
    
    df['update_date'] = pd.to_datetime(df['update_date'])

    period_map = {
        'monthly': 'M',
        'quarterly': 'Q',
        'yearly': 'Y'
    }

    if timeframe not in period_map:
        return {'error': 'Invalid period parameter', 'status': 400}

    df['timeframe'] = df['update_date'].dt.to_period(period_map[timeframe]).dt.to_timestamp()

    trend_data = df.groupby('timeframe').agg({
        'influencer_perc': lambda x: round(x.mean(), 1),
        'detractor_perc': lambda x: round(x.mean(), 1),
        'neutral_perc': lambda x: round(x.mean(), 1)
    }).reset_index()

    trend_data = trend_data.sort_values(by='timeframe', ascending=True)

    if timeframe == 'monthly':
        trend_data['label'] = trend_data['timeframe'].dt.strftime("%b'%y").str.upper()
    elif timeframe == 'quarterly':
        trend_data['label'] = trend_data['timeframe'].dt.to_period('Q').dt.strftime('Q%q\'%y')
    elif timeframe == 'yearly':
        trend_data['label'] = trend_data['timeframe'].dt.strftime('%Y')

    trend_dict = trend_data.to_dict(orient='records')
    return {'data': trend_dict, 'status': 200}
