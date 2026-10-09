import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_lead_summary(lead: dict) -> dict:
    prompt = f"""You are a sales assistant. Based ONLY on the lead information below, 
do not invent any facts. Respond with valid JSON only, no extra text, matching this exact structure:

{{
  "summary": "a short factual summary of the lead, 1-2 sentences",
  "buying_intent": "high, medium, low, or unknown",
  "recommended_next_step": "a short actionable suggestion",
  "email_draft": "a short, professional follow-up email draft, 3-4 sentences"
}}

Lead information:
Name: {lead['name']}
Company: {lead['company']}
Job title: {lead['job_title']}
Country: {lead['country']}
Industry: {lead['industry']}
Company size: {lead['company_size']}
Source: {lead['source']}
Campaign: {lead['campaign']}
Message from lead: {lead['message'] or 'No message provided'}
Score tier: {lead['tier'] or 'Not yet scored'}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "error": "Model did not return valid JSON",
            "raw_response": raw_text
        }

    return parsed