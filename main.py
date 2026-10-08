from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

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

# Temporary in-memory storage
leads_db: list[dict] = []
next_id = 1

@app.get("/")
def read_root():
    return {"message": "LeadFlow AI is running"}

@app.post("/leads")
def create_lead(lead: Lead):
    global next_id

    for existing_lead in leads_db:
        if existing_lead["email"] == lead.email:
            raise HTTPException(
                status_code=409,
                detail=f"A lead with email {lead.email} already exists"
            )

    new_lead = lead.model_dump()
    new_lead["id"] = next_id
    leads_db.append(new_lead)
    next_id += 1

    return {
        "message": "Lead received successfully",
        "lead": new_lead
    }

@app.get("/leads")
def get_all_leads():
    return {"count": len(leads_db), "leads": leads_db}

@app.get("/leads/{lead_id}")
def get_lead(lead_id: int):
    for lead in leads_db:
        if lead["id"] == lead_id:
            return lead
    raise HTTPException(status_code=404, detail="Lead not found")

@app.post("/leads/{lead_id}/score")
def score_lead_endpoint(lead_id: int):
    for stored_lead in leads_db:
        if stored_lead["id"] == lead_id:
            lead_obj = Lead(**stored_lead)
            result = score_lead(lead_obj)
            stored_lead["score"] = result["score"]
            stored_lead["tier"] = result["tier"]
            stored_lead["score_reasons"] = result["reasons"]
            return {
                "message": "Lead scored successfully",
                "lead_id": lead_id,
                "score": result["score"],
                "tier": result["tier"],
                "reasons": result["reasons"]
            }
    raise HTTPException(status_code=404, detail="Lead not found")