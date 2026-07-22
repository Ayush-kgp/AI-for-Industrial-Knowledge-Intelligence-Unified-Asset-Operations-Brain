import os
from pydantic import BaseModel, Field
import openai

class Person(BaseModel):
    name: str = Field(description="Name of the person")
    role: str = Field(description="Role of the person, e.g., technician, supervisor, inspector")

class ExtractedEntities(BaseModel):
    document_type: str = Field(description="One of: Document, Procedure, MaintenanceRecord, InspectionFinding")
    equipment_tags: list[str] = Field(default_factory=list, description="Equipment IDs mentioned, e.g., 'C-101'")
    dates: list[str] = Field(default_factory=list, description="Relevant dates or timestamps mentioned")
    personnel: list[Person] = Field(default_factory=list, description="People mentioned and their roles")
    regulatory_clauses: list[str] = Field(default_factory=list, description="Specific regulatory or compliance clauses mentioned")
    referenced_prior_events: list[str] = Field(default_factory=list, description="Prior events or incidents referenced (e.g., 'Q3 pressure trip incident')")
    referenced_documents: list[dict] = Field(default_factory=list, description="Other documents or procedures this text explicitly references as being updated, superseded, or issued in response to something — e.g. 'update the SOP'. Capture as {'title': str, 'relationship': str} where relationship is one of: UPDATES, SUPERSEDES, ISSUED_IN_RESPONSE_TO.")

def extract_entities(text: str) -> ExtractedEntities:
    """
    Uses OpenAI Structured Outputs to extract entities matching our schema.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment!")
    client = openai.Client(api_key=api_key)
    
    prompt = f"""You are an expert industrial data extraction assistant. 
Analyze the following document text and extract the key entities according to the required schema.
- Accurately classify the document_type (default to 'Document' if unsure).
- Extract exact equipment_tags (like 'C-101', 'P-205').
- For referenced_documents, capture ANY mention of another document or procedure being updated, superseded, or issued (e.g. 'Update the SOP' -> title: 'sop_c101.pdf' or 'SOP', relationship: 'UPDATES'). You MUST provide a 'title' for every referenced document.
- If an entity type is not present in the text, return an empty list.

Document Text:
{text}
"""

    response = client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        messages=[{"role": "user", "content": prompt}],
        response_format=ExtractedEntities,
        temperature=0.0,
    )
    
    return response.choices[0].message.parsed
