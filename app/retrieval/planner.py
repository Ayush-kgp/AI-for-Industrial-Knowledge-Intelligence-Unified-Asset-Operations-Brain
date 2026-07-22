import os
import json
import openai
from .graph_tools import get_equipment_history, find_related_documents
from .vector_tools import semantic_search_chunks
from .metadata_tools import get_document_status

# Define the tools available to the OpenAI planner
planner_tools_map = {
    "get_equipment_history": get_equipment_history,
    "find_related_documents": find_related_documents,
    "semantic_search_chunks": semantic_search_chunks,
    "get_document_status": get_document_status
}

openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_equipment_history",
            "description": "Retrieves the history of events, documents, and personnel related to a specific equipment tag. Returns a JSON string representing the timeline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "equipment_tag": {"type": "string", "description": "The equipment tag (e.g. C-101)"}
                },
                "required": ["equipment_tag"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_related_documents",
            "description": "Finds documents related to a given document ID or title/name (such as preceding incidents or subsequent actions). You must provide either document_id or title. For whichever one you don't use, pass an empty string \"\". Use title for partial case-insensitive matches (e.g. 'compressor trip').",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string"},
                    "title": {"type": "string"}
                },
                "required": ["document_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "semantic_search_chunks",
            "description": "Performs a semantic search over document chunks in Qdrant to find relevant text. Returns a JSON string containing the matched chunks, their document IDs, and associated Neo4j node IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_document_status",
            "description": "Retrieves the current metadata status of a document from Postgres.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string"}
                },
                "required": ["document_id"]
            }
        }
    }
]

SYSTEM_INSTRUCTION = """
You are an expert Industrial Safety and Maintenance Copilot.
Your job is to answer complex questions about industrial equipment, maintenance records, and regulatory compliance.

You have access to tools that query a Knowledge Graph (Neo4j) and a Semantic Vector Database (Qdrant).
Often, you will need to use these tools in multiple steps. For example:
1. Search the graph to find out when an event occurred or what equipment is involved.
2. Use the document IDs or equipment tags from the graph to search the vector database for specific procedures or text chunks.

CRITICAL TRUST REQUIREMENTS - You MUST adhere to these in your final response:
1. Your final output MUST be a valid JSON object matching this schema:
{
    "answer": "Your detailed answer to the user's question.",
    "confidence": "High" | "Medium" | "Low",
    "citations": [
        {
            "document_id": "ID of the document you sourced this from",
            "snippet": "A direct quote or highly specific summary of the text chunk you relied on."
        }
    ]
}

2. ANTI-HALLUCINATION RULE (STRICT): You are EXPLICITLY FORBIDDEN from stating any fact, name, date, or status that isn't directly returned by a tool call. 
3. If a tool call errors, returns incomplete data, or says "Document not found", the answer MUST explicitly state "status unavailable" or "not found in records". 
4. DO NOT invent plausible-sounding details to fill gaps. 
5. COMPREHENSIVE CITATIONS: EVERY SINGLE factual claim (including names like Alan Walker, statuses, regulations, etc.) MUST have a corresponding citation in the `citations` array. If you discuss 3 documents, you MUST have at least 3 citations. Do not omit citations for ANY claim.

Do not include markdown blocks like ```json in the final response. Just output raw JSON.
"""

def create_planner():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment!")
    client = openai.Client(api_key=api_key)
    return client

def ask_planner(query: str):
    """
    Executes the agentic planner for a given user query.
    Returns the JSON string containing the final answer, confidence, and citations.
    """
    client = create_planner()
    
    print(f"\n[Planner] User Query: {query}")
    
    # We maintain the conversation history manually to cap iterations
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": query}
    ]
    
    MAX_STEPS = 5
    for step in range(MAX_STEPS):
        print(f"\n--- Planner Step {step + 1}/{MAX_STEPS} ---")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=openai_tools,
            temperature=0.0
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            # We must append the assistant's message with tool calls to history
            messages.append(message)
            
            for tool_call in message.tool_calls:
                print(f"[MODEL] FUNCTION CALL: {tool_call.function.name}")
                args = json.loads(tool_call.function.arguments)
                print(f"  Args: {args}")
                
                # Execute the tool
                result_str = ""
                tool_func = planner_tools_map.get(tool_call.function.name)
                
                if tool_func:
                    print(f"  [EXECUTION] Running {tool_call.function.name}...")
                    try:
                        result_str = tool_func(**args)
                    except Exception as e:
                        print(f"  [ERROR] {e}")
                        result_str = json.dumps({"error": str(e)})
                else:
                    result_str = json.dumps({"error": f"Tool {tool_call.function.name} not found"})
                
                print(f"  [RESULT] {result_str[:200]}...")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": result_str
                })
            
        else:
            # No more function calls, we have our final text answer
            # We must append it to history as well to be technically correct, but we return it
            print(f"[MODEL] TEXT:\n{message.content}\n")
            return message.content
            
    print(f"\n[Planner] Hard cap of {MAX_STEPS} steps reached. Aborting to save quota.")
    return '{"error": "Max iterations reached without a final answer."}'

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_query = "What maintenance followed the Q3 pressure trip on C-101?"
    print(ask_planner(test_query))
