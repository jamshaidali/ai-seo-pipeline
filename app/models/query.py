import uuid
from datetime import datetime, timezone
from app.extensions import db

class DiscoveredQuery(db.Model):
    __tablename__ = 'discovered_queries'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_uuid = db.Column(db.String(36), db.ForeignKey('business_profiles.uuid'), nullable=False)
    run_uuid = db.Column(db.String(36), db.ForeignKey('pipeline_runs.uuid'), nullable=False)
    
    query_text = db.Column(db.String(500), nullable=False)
    estimated_search_volume = db.Column(db.Integer, nullable=True)
    competitive_difficulty = db.Column(db.Integer, nullable=True)
    opportunity_score = db.Column(db.Float, nullable=True)
    domain_visible = db.Column(db.Boolean, nullable=True)
    visibility_position = db.Column(db.Integer, nullable=True)
    
    discovered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    recommendations = db.relationship('ContentRecommendation', backref='query_rel', lazy=True)

    def to_dict(self):
        return {
            "query_uuid": self.uuid,
            "query_text": self.query_text,
            "estimated_search_volume": self.estimated_search_volume,
            "competitive_difficulty": self.competitive_difficulty,
            "opportunity_score": self.opportunity_score,
            "domain_visible": self.domain_visible,
            "visibility_position": self.visibility_position,
            "discovered_at": self.discovered_at.isoformat() + "Z" if self.discovered_at else None
        }
