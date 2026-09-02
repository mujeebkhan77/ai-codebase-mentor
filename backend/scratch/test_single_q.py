import sys
sys.path.insert(0, ".")
from agent import run_agent

def main():
    q = "How does this RAG application process an uploaded PDF from ingestion to retrieval?"
    repo = "C:/Users/User/Desktop/ai-codebase-mentor/backend/repositories/universal-rag-chatbot"
    res = run_agent(q, repo_path=repo)
    print("STATUS:", res.get("status"))
    print("WARNING:", res.get("warning"))
    print("\nANSWER:\n", res.get("answer"))
    print("\nEVIDENCE:")
    for e in res.get("evidence", [])[:5]:
        print(f"- {e.get('file')} (Lines {e.get('start_line')}-{e.get('end_line')}) [{e.get('symbol')}]")

if __name__ == "__main__":
    main()
