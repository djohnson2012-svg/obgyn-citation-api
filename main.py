from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="OB/GYN Citation Validator", description="API for validating medical citations against approved sources")

# Approved medical sources for OB/GYN citations
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
    """Request model for citation validation"""
    claim: str
    citation_url: str

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {"message": "OB/GYN Citation Validator API", "version": "1.0.0"}

@app.post("/validate-citation")
def validate_citation(data: CitationRequest):
    """
    Validate a citation URL against approved medical sources.
    Returns approval status, formatted citation, and audit flag.
    """
    url = data.citation_url
    
    # Check if URL is in approved list
    if url not in APPROVED:
        return {
            "is_approved": False,
            "formatted_citation": "Source limitation for this claim",
            "flag_for_audit": True,
            "message": "URL not in approved list"
        }
    
    # Validate that the URL is accessible
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return {
                "is_approved": False,
                "formatted_citation": "Source limitation for this claim",
                "flag_for_audit": True,
                "message": f"HTTP error code: {r.status_code}"
            }
        
        # Check for common error indicators in page content
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
    
    # Citation is valid and accessible
    return {
        "is_approved": True,
        "formatted_citation": f'({url})',
        "flag_for_audit": False,
        "message": "Citation is approved and working"
    }

@app.get("/citations")
def get_citations():
    """
    Citation microservice endpoint.
    Returns list of approved medical citation sources.
    """
    return {
        "approved_sources": list(APPROVED),
        "total_count": len(APPROVED),
        "service": "OB/GYN Citation Microservice",
        "version": "1.0.0"
    }
