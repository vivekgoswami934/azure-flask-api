from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from .models.nex_score import NexScore

class NexScoreSchema(SQLAlchemySchema):
    class Meta:
        model = NexScore
        load_instance = True

    id = auto_field()
    market = auto_field()
    region = auto_field()
    detractor_count = auto_field()
    neutral_count = auto_field()
    influencer_count = auto_field()
    total = auto_field()
    detractor_perc = auto_field()
    neutral_perc = auto_field()
    influencer_perc = auto_field()
    update_date = auto_field()

nex_score_schema = NexScoreSchema(many=True)
