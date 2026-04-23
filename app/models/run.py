import uuid
from datetime import datetime, timezone
from app.extensions import db

class PipelineRun(db.Model):
    __tablename__ = 'pipeline_runs'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_uuid = db.Column(db.String(36), db.ForeignKey('business_profiles.uuid'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    queries_discovered = db.Column(db.Integer, default=0)
    queries_scored = db.Column(db.Integer, default=0)
    tokens_used = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    queries = db.relationship('DiscoveredQuery', backref='run', lazy=True)
