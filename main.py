import json
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import LeadDB

Base.metadata.create_all(bind=engine)

app = FastAPI()

class Lead(BaseModel):
    name: str
    email: EmailStr
    company: str
    job_title: str
    country: str
    industry: str
    company_size: int
    source: str
    campaign: str
    message: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DISPOSABLE_DOMAINS = {"mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com"}

def score_lead(lead: Lead) -> dict:
    score = 0
    reasons = []

    if lead.company_size >= 200:
        score += 20
        reasons.append("Company size is 200 or more")

    title_lower = lead.job_title.lower()
    if "director" in title_lower or "head" in title_lower or "vp" in title_lower:
        score += 15
        reasons.append("Job title indicates decision-making seniority")

    if lead.source == "demo_request":
        score += 15
        reasons.append("Source is demo_request")

    if lead.industry in ("SaaS", "Technology"):
        score += 10
        reasons.append("Industry is SaaS or Technology")

    if lead.campaign == "high_intent":
        score += 10
        reasons.append("Campaign is marked high_intent")

    email_domain = lead.email.split("@")[-1].lower()
    if email_domain in DISPOSABLE_DOMAINS:
        score -= 10
        reasons.append("Email domain appears disposable")

    if score >= 50:
        tier = "high"
    elif score >= 25:
        tier = "medium"
    else:
        tier = "low"

    return {"score": score, "tier": tier, "reasons": reasons}

def lead_to_dict(lead_db: LeadDB) -> dict:
    return {
        "id": lead_db.id,
        "name": lead_db.name,
        "email": lead_db.email,
        "company": lead_db.company,
        "job_title": lead_db.job_title,
        "country": lead_db.country,
        "industry": lead_db.industry,
        "company_size": lead_db.company_size,
        "source": lead_db.source,
        "campaign": lead_db.campaign,
        "message": lead_db.message,
        "score": lead_db.score,
        "tier": lead_db.tier,
        "score_reasons": json.loads(lead_db.score_reasons) if lead_db.score_reasons else None,
    }

@app.get("/")
def read_root():
    return {"message": "LeadFlow AI is running"}

@app.post("/leads")
def create_lead(lead: Lead, db: Session = Depends(get_db)):
    existing = db.query(LeadDB).filter(LeadDB.email == lead.email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A lead with email {lead.email} already exists"
        )

    new_lead = LeadDB(**lead.model_dump())
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return {
        "message": "Lead received successfully",
        "lead": lead_to_dict(new_lead)
    }

@app.get("/leads")
def get_all_leads(db: Session = Depends(get_db)):
    leads = db.query(LeadDB).all()
    return {"count": len(leads), "leads": [lead_to_dict(l) for l in leads]}

@app.get("/leads/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead_db = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead_to_dict(lead_db)

@app.post("/leads/{lead_id}/score")
def score_lead_endpoint(lead_id: int, db: Session = Depends(get_db)):
    lead_db = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead_db:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_obj = Lead(
        name=lead_db.name,
        email=lead_db.email,
        company=lead_db.company,
        job_title=lead_db.job_title,
        country=lead_db.country,
        industry=lead_db.industry,
        company_size=lead_db.company_size,
        source=lead_db.source,
        campaign=lead_db.campaign,
        message=lead_db.message,
    )
    result = score_lead(lead_obj)

    lead_db.score = result["score"]
    lead_db.tier = result["tier"]
    lead_db.score_reasons = json.dumps(result["reasons"])
    db.commit()

    return {
        "message": "Lead scored successfully",
        "lead_id": lead_id,
        "score": result["score"],
        "tier": result["tier"],
        "reasons": result["reasons"]
    }