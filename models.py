from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class LeadDB(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    company = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    country = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    company_size = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    campaign = Column(String, nullable=False)
    message = Column(String, nullable=True)
    score = Column(Integer, nullable=True)
    tier = Column(String, nullable=True)
    score_reasons = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    routing_reason = Column(String, nullable=True)
    followup_status = Column(String, nullable=True, default="none")
    followup_draft = Column(String, nullable=True)

class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    details = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())