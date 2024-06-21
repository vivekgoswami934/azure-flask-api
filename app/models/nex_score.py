from .. import db

class NexScore(db.Model):
    __tablename__ = 'nex_score'

    id = db.Column(db.Integer, primary_key=True)
    market = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    detractor_count = db.Column(db.Integer, nullable=False)
    neutral_count = db.Column(db.Integer, nullable=False)
    influencer_count = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    detractor_perc = db.Column(db.Float, nullable=False)
    neutral_perc = db.Column(db.Float, nullable=False)
    influencer_perc = db.Column(db.Float, nullable=False)
    update_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<NexScore {self.market} - {self.region} - {self.update_date}>'