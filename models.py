from sqlalchemy import Column, Integer, String
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