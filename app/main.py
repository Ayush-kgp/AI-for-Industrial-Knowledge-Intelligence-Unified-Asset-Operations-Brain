from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from .retrieval.planner import ask_planner
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Industrial Safety Copilot API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Live Demo Cache for Fallback
DEMO_CACHE = {
    "what maintenance followed the q3 pressure trip on c-101?": {
        "answer": "Following the Q3 pressure trip on compressor C-101, a revised Standard Operating Procedure (SOP) was issued (doc-sop-200) updating the restart protocol. Subsequently, an inspection (doc-inspection-300) was performed which cleared the equipment for operation.",
        "confidence": "High",
        "citations": [
            {
                "document_id": "doc-incident-100",
                "snippet": "Q3 pressure trip incident involving C-101."
            },
            {
                "document_id": "doc-sop-200",
                "snippet": "SOP issued in response to Q3 pressure trip incident."
            },
            {
                "document_id": "doc-inspection-300",
                "snippet": "Inspection performed post-trip, equipment cleared."
            }
        ]
    },
    "what is the history of equipment c-101?": {
        "answer": "Equipment C-101 experienced a Q3 pressure trip incident (doc-incident-100). Following this, a revised SOP (doc-sop-200) was issued, and an inspection (doc-inspection-300) was completed.",
        "confidence": "High",
        "citations": [
            {
                "document_id": "doc-incident-100",
                "snippet": "Q3 pressure trip incident involving C-101."
            }
        ]
    }
}

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    # Normalize query for cache lookup
    normalized_query = req.query.strip().lower()
    
    # Check cache first (Safety Net)
    if normalized_query in DEMO_CACHE:
        print(f"[CACHE HIT] Returning cached response for: '{req.query}'")
        return DEMO_CACHE[normalized_query]

    print(f"[CACHE MISS] Hitting live planner API for: '{req.query}'")
    
    # Call the live planner
    result_str = ask_planner(req.query)
    
    # Parse and return
    try:
        result_json = json.loads(result_str)
        return result_json
    except json.JSONDecodeError:
        # If it failed to parse, wrap it
        return {"answer": result_str, "confidence": "Unknown", "citations": []}
