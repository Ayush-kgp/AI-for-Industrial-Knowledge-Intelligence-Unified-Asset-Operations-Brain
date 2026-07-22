import os
from dotenv import load_dotenv

def run_test():
    load_dotenv()
    
    print("=== Testing Agentic Planner ===")
    
    from app.retrieval.planner import ask_planner
    
    queries = [
        "What maintenance followed the Q3 pressure trip incident on C-101?",
        "Who is the supervisor for the C-101 maintenance?",
        "What regulations govern the maintenance on C-101?"
    ]
    
    import time
    for q in queries:
        print("\n" + "="*50)
        print(f"QUERY: {q}")
        print("="*50)
        result = ask_planner(q)
        print(f"\nPLANNER RESULT:\n{result}\n")
        print("Sleeping for 15s to avoid free tier rate limits...")
        time.sleep(15)

if __name__ == "__main__":
    run_test()
