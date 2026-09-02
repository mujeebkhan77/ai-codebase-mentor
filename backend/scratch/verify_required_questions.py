import sys
import json
from pathlib import Path

sys.path.insert(0, ".")
from agent.controller import run_agent

RAG_REPO_PATH = str(Path("repositories/universal-rag-chatbot").resolve())

def test_question(q_num, question):
    print(f"==================================================")
    print(f"QUESTION {q_num}: {question}")
    print(f"==================================================")
    
    res = run_agent(question, repo_path=RAG_REPO_PATH)
    
    status = res.get("status")
    state = res.get("state", {})
    iterations = state.get("iterations", 0)
    tool_calls = state.get("tool_calls", 0)
    evidence = res.get("evidence", [])
    
    evidence_files = [e.get("file") for e in evidence]
    flask_evidence_found = any("flask" in str(f).lower() and "universal-rag-chatbot" not in str(f).lower() for ffile in evidence_files for f in [ffile] if f)
    
    print(f"Status: {status}")
    print(f"Iterations: {iterations}")
    print(f"Tool Calls: {tool_calls}")
    print(f"Evidence Files Count: {len(evidence)}")
    print(f"Flask Evidence Returned: {flask_evidence_found}")
    print("\nEvidence Files:")
    for f in set(evidence_files):
        print(f"  - {f}")
        
    print("\nAnswer Preview:")
    print(res.get("answer", "")[:1200])
    print("\n")
    return {
        "q_num": q_num,
        "status": status,
        "iterations": iterations,
        "tool_calls": tool_calls,
        "evidence_files": list(set(evidence_files)),
        "flask_evidence_returned": flask_evidence_found
    }

def main():
    q1 = "How does this RAG application process a PDF from upload to storing its embeddings in ChromaDB?"
    q2 = "What happens when a user uploads a document to this application? Explain the complete ingestion pipeline, including loaders, splitting, embeddings, and vector storage."
    
    r1 = test_question(1, q1)
    r2 = test_question(2, q2)

if __name__ == "__main__":
    main()
