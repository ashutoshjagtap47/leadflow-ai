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