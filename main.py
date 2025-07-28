from fastapi import FastAPI, Query
from pydantic import BaseModel
import requests
from typing import Optional, List

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

# Citations dictionary keyed by topic
CITATIONS = {
    "pcos": [
        {
            "title": "Polycystic Ovary Syndrome: Diagnosis and Management",
            "authors": "ACOG Committee on Gynecologic Practice",
            "source": "American College of Obstetricians and Gynecologists",
            "year": 2024,
            "url": "https://www.acog.org/clinical/clinical-guidance/clinical-practice-update",
            "doi": "10.1097/AOG.0000000000005434",
            "abstract": "Clinical practice update on diagnosis and management of PCOS including metabolic considerations."
        },
        {
            "title": "PCOS Metabolic Management Guidelines",
            "authors": "Society for Maternal-Fetal Medicine",
            "source": "SMFM Clinical Guidance",
            "year": 2023,
            "url": "https://www.smfm.org/clinical-guidance",
            "doi": "10.1016/j.ajog.2023.05.021",
            "abstract": "Evidence-based guidelines for metabolic management of women with PCOS."
        },
        {
            "title": "Fertility Treatment in PCOS Patients",
            "authors": "American Society for Reproductive Medicine",
            "source": "ASRM Practice Committee",
            "year": 2023,
            "url": "https://www.asrm.org/practice-guidance/practice-committee-documents/",
            "doi": "10.1016/j.fertnstert.2023.03.018",
            "abstract": "Comprehensive review of fertility treatment options for women with PCOS."
        }
    ],
    "endometriosis": [
        {
            "title": "Endometriosis: Diagnosis and Management",
            "authors": "ACOG Committee on Gynecologic Practice",
            "source": "American College of Obstetricians and Gynecologists",
            "year": 2024,
            "url": "https://www.acog.org/clinical/clinical-guidance/clinical-practice-update",
            "doi": "10.1097/AOG.0000000000005567",
            "abstract": "Updated guidelines for diagnosis and treatment of endometriosis."
        }
    ],
    "preeclampsia": [
        {
            "title": "Preeclampsia Prevention and Management",
            "authors": "Society for Maternal-Fetal Medicine",
            "source": "SMFM Clinical Guidance",
            "year": 2024,
            "url": "https://www.smfm.org/clinical-guidance",
            "doi": "10.1016/j.ajog.2024.02.018",
            "abstract": "Evidence-based approach to preeclampsia prevention and management."
        }
    ]
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
def get_citations(topic: Optional[str] = Query(None, description="Filter citations by topic (e.g., pcos, endometriosis, preeclampsia)")):
    """
    Citation microservice endpoint.
    Returns list of citations, optionally filtered by topic.
    Supports GET /citations?topic=pcos to return citations for specific topics.
    """
    if topic:
        topic_lower = topic.lower()
        if topic_lower in CITATIONS:
            return {
                "topic": topic_lower,
                "citations": CITATIONS[topic_lower],
                "count": len(CITATIONS[topic_lower]),
                "service": "OB/GYN Citation Microservice",
                "version": "1.0.0"
            }
        else:
            return {
                "topic": topic_lower,
                "citations": [],
                "count": 0,
                "message": f"No citations found for topic '{topic_lower}'",
                "available_topics": list(CITATIONS.keys()),
                "service": "OB/GYN Citation Microservice",
                "version": "1.0.0"
            }
    else:
        # Return all citations when no topic is specified
        all_citations = []
        for topic_name, citations in CITATIONS.items():
            all_citations.extend(citations)
        
        return {
            "citations": all_citations,
            "count": len(all_citations),
            "available_topics": list(CITATIONS.keys()),
            "approved_sources": list(APPROVED),
            "service": "OB/GYN Citation Microservice",
            "version": "1.0.0"
        }
