import json
from pathlib import Path
from indexing.index_repository import index_repository
from agent import run_agent

REPO_PATH = Path("repositories/universal-rag-chatbot").resolve()

def main():
    print(f"Indexing repository at {REPO_PATH}...")
    index_repository(REPO_PATH)
    print("Indexing complete!\n")

    questions = [
        "How does this RAG application process an uploaded PDF from ingestion to retrieval?",
        "How are document chunks converted into embeddings and stored?",
        "How does the application load the existing vector database during retrieval?"
    ]

    for idx, q in enumerate(questions, 1):
        print(f"==================================================")
        print(f"TEST {idx}: {q}")
        print(f"==================================================")
        res = run_agent(q, repo_path=str(REPO_PATH))

        print(f"Status: {res.get('status')}")
        print(f"Warning: {res.get('warning')}")
        print(f"State Summary: {json.dumps(res.get('state', {}), indent=2)}")
        print("\n--- ANSWER ---")
        answer = res.get("answer")
        print(answer[:1500] if answer else "NONE")

        print("\n--- EVIDENCE (Line metadata check) ---")
        evidence = res.get("evidence", [])
        for e in evidence[:5]:
            print(f"- {e.get('file')} (Lines {e.get('start_line')}-{e.get('end_line')}) [{e.get('symbol')}]")
        print("\n")

if __name__ == "__main__":
    main()
