from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
import uuid

# Import SQLAlchemy components for database models
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from core import Base


class Feedback(Base):
    """
    Store user feedback submissions from the beta tester feedback form.
    
    This model persists feedback data in PostgreSQL, ensuring submissions
    are retained across deployments (unlike file-based storage).
    """
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Contact Information
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    
    # Rating fields (1-5 scale)
    ease_of_use = Column(Integer, nullable=True)
    interface_clarity = Column(Integer, nullable=True)
    performance_speed = Column(Integer, nullable=True)
    documentation_clarity = Column(Integer, nullable=True)
    data_usefulness = Column(Integer, nullable=True)
    data_accuracy = Column(Integer, nullable=True)
    herc_integration = Column(Integer, nullable=True)
    report_usefulness = Column(Integer, nullable=True)
    likelihood_of_use = Column(Integer, nullable=True)
    recommendation_likelihood = Column(Integer, nullable=True)
    
    # Open-ended text responses
    strengths = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)
    missing_features = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    additional_comments = Column(Text, nullable=True)
    
    # Metadata
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback {self.id} from {self.name or "Anonymous"} at {self.submitted_at}>'
    
    def to_dict(self):
        """Convert feedback to dictionary for templates and API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'organization': self.organization,
            'role': self.role,
            'ease_of_use': self.ease_of_use,
            'interface_clarity': self.interface_clarity,
            'performance_speed': self.performance_speed,
            'documentation_clarity': self.documentation_clarity,
            'data_usefulness': self.data_usefulness,
            'data_accuracy': self.data_accuracy,
            'herc_integration': self.herc_integration,
            'report_usefulness': self.report_usefulness,
            'likelihood_of_use': self.likelihood_of_use,
            'recommendation_likelihood': self.recommendation_likelihood,
            'strengths': self.strengths,
            'challenges': self.challenges,
            'missing_features': self.missing_features,
            'suggestions': self.suggestions,
            'additional_comments': self.additional_comments,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None
        }
    
    @property
    def average_rating(self):
        """Calculate average rating across all rating fields."""
        ratings = [
            self.ease_of_use, self.interface_clarity, self.performance_speed,
            self.documentation_clarity, self.data_usefulness, self.data_accuracy,
            self.herc_integration, self.report_usefulness, self.likelihood_of_use,
            self.recommendation_likelihood
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if not valid_ratings:
            return None
        return round(sum(valid_ratings) / len(valid_ratings), 1)

@dataclass
class RiskAssessment:
    location: str
    natural_hazards: Dict[str, float]
    infectious_disease_risk: float
    active_shooter_risk: float
    total_risk_score: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskAssessment':
        return cls(
            location=data['location'],
            natural_hazards=data['natural_hazards'],
            infectious_disease_risk=data.get('infectious_disease_risk', 0.0),
            active_shooter_risk=data.get('active_shooter_risk', 0.0),
            total_risk_score=data['total_risk_score']
        )


class HERCRiskCache(Base):
    """
    Cache pre-computed HERC regional risk data.
    
    This model stores pre-calculated risk aggregations for HERC regions,
    enabling instant dashboard loading without triggering external API calls.
    Data is refreshed periodically by a background scheduler job.
    """
    __tablename__ = 'herc_risk_cache'
    
    herc_id = Column(String(10), primary_key=True)  # e.g., "1", "2", etc.
    name = Column(String(100), nullable=False)  # e.g., "HERC Region 1 - Western"
    risk_data = Column(JSON, nullable=False)  # Full risk data structure
    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_valid = Column(Boolean, nullable=False, default=True)
    calculation_duration_seconds = Column(Float, nullable=True)  # Track performance
    jurisdiction_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f'<HERCRiskCache {self.herc_id} - {self.name}>'
    
    @property
    def age_minutes(self):
        """Calculate how old the cached data is in minutes."""
        if not self.calculated_at:
            return None
        return (datetime.utcnow() - self.calculated_at).total_seconds() / 60
    
    @property
    def is_fresh(self):
        """Check if cache is fresh (less than 4 hours old)."""
        age = self.age_minutes
        if age is None:
            return False
        return age < 240  # 4 hours
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'herc_id': self.herc_id,
            'name': self.name,
            'risk_data': self.risk_data,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'is_valid': self.is_valid,
            'age_minutes': self.age_minutes,
            'is_fresh': self.is_fresh,
            'jurisdiction_count': self.jurisdiction_count
        }


class ExportJob(Base):
    """
    Track asynchronous GIS export jobs with real-time progress updates.
    
    This model enables background processing of comprehensive risk data exports
    while preserving data accuracy and avoiding web request timeouts.
    """
    __tablename__ = 'export_jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String(20), nullable=False, default='queued')  # queued, running, completed, failed, canceled
    export_type = Column(String(50), nullable=False, default='all_jurisdictions')  # all_jurisdictions, single_jurisdiction
    
    # Progress tracking
    total_count = Column(Integer, nullable=False, default=0)
    completed_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    
    # Results and metadata
    result_files = Column(JSON, nullable=True)  # {"csv": "path/to/file.csv", "geojson": "path/to/file.geojson"}
    error_message = Column(Text, nullable=True)
    params = Column(JSON, nullable=True)  # Export parameters (jurisdiction_id for single exports, etc.)
    
    # Cache and data freshness
    cache_freshness_minutes = Column(Integer, nullable=False, default=30)  # How fresh the data should be
    data_sources_used = Column(JSON, nullable=True)  # Track which data sources were fresh vs cached
    
    def __repr__(self):
        return f'<ExportJob {self.id} - {self.status}>'
    
    @property
    def progress_percent(self):
        """Calculate completion percentage."""
        if self.total_count == 0:
            return 0
        return int((self.completed_count / self.total_count) * 100)
    
    @property
    def estimated_remaining_seconds(self):
        """Estimate remaining time based on current progress."""
        if self.status != 'running' or self.completed_count == 0:
            return None
        
        if not self.started_at:
            return None
            
        elapsed_seconds = (datetime.utcnow() - self.started_at).total_seconds()
        if elapsed_seconds <= 0:
            return None
            
        avg_seconds_per_item = elapsed_seconds / self.completed_count
        remaining_items = self.total_count - self.completed_count
        
        return int(avg_seconds_per_item * remaining_items)
    
    def to_dict(self):
        """Convert job to dictionary for API responses."""
        return {
            'id': str(self.id),
            'status': self.status,
            'export_type': self.export_type,
            'progress': {
                'total_count': self.total_count,
                'completed_count': self.completed_count,
                'error_count': self.error_count,
                'percent': self.progress_percent
            },
            'timestamps': {
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'finished_at': self.finished_at.isoformat() if self.finished_at else None
            },
            'estimated_remaining_seconds': self.estimated_remaining_seconds,
            'result_files': self.result_files,
            'error_message': self.error_message,
            'params': self.params,
            'data_freshness': {
                'cache_freshness_minutes': self.cache_freshness_minutes,
                'data_sources_used': self.data_sources_used
            }
        }


class DataSourceCache(Base):
    """
    Cache external API data by source and jurisdiction for reliable offline access.
    
    This model enables the pre-cached data architecture where:
    - Scheduled jobs refresh data at appropriate cadences (annual, weekly, daily)
    - User requests read from cache only - never hitting external APIs
    - Data freshness is tracked and displayed to users
    
    Refresh Cadences:
    - Annual: CDC SVI, FEMA NRI (updated yearly)
    - Weekly: DHS Health Metrics, NWS Forecasts
    - Daily: EPA Air Quality
    """
    __tablename__ = 'data_source_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    source_type = Column(String(50), nullable=False, index=True)
    jurisdiction_id = Column(String(20), nullable=True, index=True)
    county_name = Column(String(100), nullable=True, index=True)
    
    data = Column(JSON, nullable=False)
    
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, nullable=False, default=True)
    
    fetch_duration_seconds = Column(Float, nullable=True)
    api_source = Column(String(200), nullable=True)
    used_fallback = Column(Boolean, nullable=False, default=False)
    fallback_reason = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('ix_data_source_cache_lookup', 'source_type', 'jurisdiction_id', 'county_name'),
    )
    
    def __repr__(self):
        return f'<DataSourceCache {self.source_type} - {self.jurisdiction_id or self.county_name}>'
    
    @property
    def age_hours(self):
        """Calculate how old the cached data is in hours."""
        if not self.fetched_at:
            return None
        return (datetime.utcnow() - self.fetched_at).total_seconds() / 3600
    
    @property
    def is_expired(self):
        """Check if the cache has expired."""
        if not self.expires_at:
            return True
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_fresh(self):
        """Check if data is valid and not expired."""
        return self.is_valid and not self.is_expired
    
    @property
    def freshness_status(self):
        """Return a human-readable freshness status."""
        if not self.is_valid:
            return 'invalid'
        if self.is_expired:
            return 'stale'
        if self.used_fallback:
            return 'fallback'
        return 'fresh'
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'source_type': self.source_type,
            'jurisdiction_id': self.jurisdiction_id,
            'county_name': self.county_name,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'age_hours': round(self.age_hours, 1) if self.age_hours else None,
            'is_fresh': self.is_fresh,
            'freshness_status': self.freshness_status,
            'used_fallback': self.used_fallback,
            'fallback_reason': self.fallback_reason
        }


class DataQualityEvent(Base):
    """
    Track data quality events for monitoring and alerting.
    
    Records when:
    - API calls fail and fallbacks are used
    - Data becomes stale
    - Circuit breakers trip
    """
    __tablename__ = 'data_quality_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    event_type = Column(String(50), nullable=False)
    source_type = Column(String(50), nullable=False)
    jurisdiction_id = Column(String(20), nullable=True)
    county_name = Column(String(100), nullable=True)
    
    severity = Column(String(20), nullable=False, default='warning')
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    is_resolved = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f'<DataQualityEvent {self.event_type} - {self.source_type}>'
