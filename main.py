from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

APPROVED = {
    "https://www.acog.org/clinical/clinical-guidance/clinical-practice-update",
    "https://www.smfm.org/clinical-guidance",
    "https://onlinelibrary.wiley.com/journal/29979684",
    "https://www.sgo.org/practice-management/statements-and-recommendations/",
    "https://www.asrm.org/practice-guidance/practice-committee-documents/",
    "https://www.ncbi.nlm.nih.gov/books/NBK430685/",
    "https://radiopaedia.org/",
    "https://perinatology.com/",
    "https://www.cdc.gov/reproductivehealth/index.html",
    "https://www.ncbi.nlm.nih.gov/pmc/",
    "https://www.exxcellence.org/list-of-monographs/",
    "https://www.obgproject.com/",
    "https://www.creogsovercoffee.com/"
}

class CitationRequest(BaseModel):
    claim: str
    citation_url: str

@app.post("/validate-citation")
def validate_citation(data: CitationRequest):
    url = data.citation_url
    if url not in APPROVED:
        return {
            "is_approved": False,
            "formatted_citation": "Source limitation for this claim",
            "flag_for_audit": True,
            "message": "URL not in approved list"
        }
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return {
                "is_approved": False,
                "formatted_citation": "Source limitation for this claim",
                "flag_for_audit": True,
                "message": f"HTTP error code: {r.status_code}"
            }
        page = r.text.lower()
        bad_phrases = ["page not found", "has moved", "redirect", "not available", "error"]
        if any(bp in page for bp in bad_phrases):
            return {
                "is_approved": False,
                "formatted_citation": "Source limitation for this claim",
                "flag_for_audit": True,
                "message": "Page loads but is broken/moved"
            }
    except Exception as e:
        return {
            "is_approved": False,
            "formatted_citation": "Source limitation for this claim",
            "flag_for_audit": True,
            "message": f"Fetch error: {str(e)}"
        }
    return {
        "is_approved": True,
        "formatted_citation": f'({url})',
        "flag_for_audit": False,
        "message": "Citation is approved and working"
    }
