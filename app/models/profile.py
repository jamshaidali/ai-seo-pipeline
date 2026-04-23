import uuid
from datetime import datetime, timezone
from app.extensions import db

class BusinessProfile(db.Model):
    __tablename__ = 'business_profiles'

    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    competitors = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='created')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    runs = db.relationship('PipelineRun', backref='profile', lazy=True, cascade="all, delete-orphan")
    queries = db.relationship('DiscoveredQuery', backref='profile', lazy=True, cascade="all, delete-orphan")
    recommendations = db.relationship('ContentRecommendation', backref='profile', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "profile_uuid": self.uuid,
            "name": self.name,
            "domain": self.domain,
            "industry": self.industry,
            "description": self.description,
            "competitors": self.competitors,
            "status": self.status,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None
        }
