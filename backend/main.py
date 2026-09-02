import sys
from pathlib import Path

from indexing.index_repository import index_repository
from graph.code_graph import CodeGraph
from retrieval.engine import RetrievalEngine
from evidence.manager import EvidenceManager
from agent import run_agent


def main():
    print("==================================================")
    print("AI Codebase Mentor — Backend Engine Demo")
    print("==================================================")

    repo_dir = Path("repositories/flask")

    if repo_dir.exists():
        print(f"\n1. Indexing repository at: {repo_dir}")
        chunks = index_repository(repo_dir)
        print(f"Indexing complete. Processed {len(chunks)} chunks.")

        print("\n2. Querying Codebase Graph...")
        graph = CodeGraph()
        ws_calls = graph.get_outgoing_calls("wsgi_app")
        print(f"Found {len(ws_calls)} outgoing call relationships for 'wsgi_app':")
        for call in ws_calls[:3]:
            print(f"  - wsgi_app calls -> {call.get('callee')} (in {call.get('file')}:{call.get('line')})")

        print("\n3. Testing Unified Retrieval Engine...")
        retrieval = RetrievalEngine(repo_path=str(repo_dir))
        results = retrieval.search(
            query="How does Flask process incoming request in wsgi_app?",
            symbol_name="wsgi_app",
            limit=5
        )
        print(f"Retrieved {len(results)} top evidence items:")
        for res in results[:3]:
            print(f"  [{res['source_type'].upper()}] {res['file']} (Score: {res['rank_score']})")

        print("\n4. Testing Evidence Manager Context Formatting...")
        em = EvidenceManager()
        em.add_items(results)
        formatted_context = em.format_for_llm(max_items=3)
        print("Formatted LLM Context snippet:")
        print(formatted_context[:400] + "...\n")

    else:
        print(f"\nRepository '{repo_dir}' not found locally.")
        print("Run tools.clone_repository('https://github.com/pallets/flask') to clone it.")

    print("\nBackend engine initialization complete.")


if __name__ == "__main__":
    main()
