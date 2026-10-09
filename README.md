# LeadFlow AI

An AI-assisted lead intake, scoring, routing, and follow-up system built with FastAPI, SQLite, and the Gemini API. It demonstrates how AI can assist a business workflow without removing human control — every AI-generated action requires explicit human approval before it's considered final.

## Problem

Sales and marketing teams receive leads from multiple sources and need to validate them, prioritize them, route them to the right owner, and follow up quickly — consistently and with a clear audit trail. This project automates that pipeline while keeping a human in the loop for anything AI-generated.

## What it does

1. **Validates and stores leads** — rejects invalid data and duplicate emails
2. **Scores leads** using transparent, explainable rules (not a black-box model) — each score comes with the exact reasons behind it
3. **Routes leads** to an owner based on tier and country, again with a stated reason
4. **Generates an AI-assisted summary and follow-up email draft** using Google's Gemini API, grounded only in the lead's actual data
5. **Requires human approval** before a follow-up draft is considered usable — the system never sends anything automatically
6. **Logs every action** (created, scored, routed, AI summary generated, approved/rejected) in an audit trail per lead

## Why rule-based scoring and routing instead of machine learning

Explainability matters more than sophistication here. A sales team needs to know *why* a lead got a particular score or was routed to a particular owner. Rule-based logic makes that reasoning fully transparent and auditable, which is also why I separated deterministic business logic (scoring, routing) from probabilistic AI output (summary, email draft) — they serve different needs and carry different risks.

## Tech stack

- **Python** / **FastAPI** — backend API
- **SQLAlchemy** + **SQLite** — persistent storage
- **Pydantic** — request validation
- **Google Gemini API** — LLM-generated summaries and follow-up drafts
- **Pytest** — automated test suite

## Architecture

```
Client (Swagger UI / curl)
        │
        ▼
   FastAPI app (main.py)
        │
   ┌────┼─────────────┬──────────────┐
   ▼    ▼             ▼              ▼
Validation  Scoring   Routing    LLM Service
(Pydantic)  (rules)   (rules)   (Gemini API)
   │          │          │           │
   └──────────┴──────────┴───────────┘
                   │
                   ▼
          SQLite (leads + workflow_events)
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/leads` | Create a new lead (validated, duplicate-checked) |
| GET | `/leads` | List all leads |
| GET | `/leads/{id}` | Get a single lead |
| POST | `/leads/{id}/score` | Score a lead with explainable rules |
| POST | `/leads/{id}/route` | Route a lead to an owner (requires scoring first) |
| POST | `/leads/{id}/ai-summary` | Generate an AI summary and follow-up draft |
| POST | `/leads/{id}/approve-followup` | Approve a draft (requires a draft to exist) |
| POST | `/leads/{id}/reject-followup` | Reject a draft |
| GET | `/leads/{id}/history` | View the full audit trail for a lead |

## Example: scoring response

```json
{
  "score": 70,
  "tier": "high",
  "reasons": [
    "Company size is 200 or more",
    "Job title indicates decision-making seniority",
    "Source is demo_request",
    "Industry is SaaS or Technology",
    "Campaign is marked high_intent"
  ]
}
```

## How to run it locally

```bash
git clone https://github.com/ashutoshjagtap47/leadflow-ai.git
cd leadflow-ai
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file with:
```
GEMINI_API_KEY=your_key_here
```

Then run:
```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Running tests

```bash
pytest
```

## Data note

All data used during development is synthetic (fictional names, companies, and emails). No real or client data was used anywhere in this project.

## Limitations and possible next steps

- In-memory rate limiting / retry handling for the Gemini API is not implemented (the free tier occasionally returns 503 errors under high demand)
- No authentication/authorization layer yet — all endpoints are open, which would need to change before any real deployment
- No frontend UI — interaction is currently via the FastAPI Swagger docs or direct API calls
- Could be extended with a real CRM integration (e.g. HubSpot) instead of manually created leads
- Could add a frontend dashboard to visualize scoring and routing trends