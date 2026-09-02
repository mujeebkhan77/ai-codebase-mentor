from pathlib import Path
from typing import Dict, List, Any, Optional

from retrieval.symbol_search import find_symbol
from retrieval.relationship_search import find_relationships
from retrieval.ranking import rank_evidence_items
from tools.search_code import search_code
from utils.caching import global_cache


class RetrievalEngine:
    """
    Unified Retrieval Engine orchestrating existing search tools:
    - Semantic search (Chroma vectorstore)
    - Symbol search (symbol_index.json)
    - Literal code search (file grep)
    - Relationship search (relationship_index.json)

    Outputs normalized evidence dictionaries ranked by deterministic criteria.
    """

    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path

    def _normalize_item(
        self,
        raw_item: Dict[str, Any],
        source_type: str
    ) -> Dict[str, Any]:
        """Normalize different tool outputs into a standard EvidenceItem dictionary."""
        file_path = (
            raw_item.get("file") or
            raw_item.get("file_path") or
            raw_item.get("target_file") or
            ""
        ).replace("\\", "/")

        start_line = (
            raw_item.get("start_line") or
            raw_item.get("line") or
            raw_item.get("target_start_line") or
            1
        )

        end_line = (
            raw_item.get("end_line") or
            raw_item.get("target_end_line") or
            start_line
        )

        symbol_name = (
            raw_item.get("name") or
            raw_item.get("symbol") or
            raw_item.get("caller") or
            raw_item.get("callee") or
            None
        )

        content = (
            raw_item.get("content") or
            raw_item.get("snippet") or
            ""
        )

        return {
            "source_type": source_type,
            "file": file_path,
            "start_line": int(start_line),
            "end_line": int(end_line),
            "symbol": symbol_name,
            "content": content,
            "metadata": raw_item.get("metadata", {}),
            "raw": raw_item
        }

    def search(
        self,
        query: str,
        symbol_name: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        repo_path: Optional[str] = None,
        limit: int = 10,
        strategies: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multi-strategy retrieval and return normalized, ranked evidence.

        strategies: list of strategy names to run, default: ['semantic', 'symbol', 'literal', 'relationship']
        """
        target_repo = repo_path or self.repo_path
        if strategies is None:
            strategies = ["semantic", "symbol", "literal", "relationship"]

        # Check in-memory cache
        cache_key = f"{query}:{symbol_name}:{keywords}:{target_repo}:{strategies}"
        cached_result = global_cache.get("retrieval", cache_key)
        if cached_result is not None:
            return cached_result[:limit]

        normalized_items: List[Dict[str, Any]] = []

        # 1. Semantic Search
        if "semantic" in strategies and query:
            try:
                from tools.semantic_search import semantic_code_search
                sem_results = semantic_code_search(query, repo_path=target_repo, k=limit)
                for item in sem_results:
                    norm = self._normalize_item(item, "semantic")
                    norm["semantic_score"] = 0.8
                    normalized_items.append(norm)
            except Exception:
                pass

        # 2. Symbol Search
        if "symbol" in strategies and (symbol_name or query):
            sym_target = symbol_name or query.strip()
            try:
                sym_results = find_symbol(sym_target, repo_path=target_repo)
                for item in sym_results:
                    norm = self._normalize_item(item, "symbol")
                    norm["semantic_score"] = 0.9
                    normalized_items.append(norm)
            except Exception:
                pass

        # 3. Literal Search
        if "literal" in strategies and target_repo and (keywords or query):
            search_term = keywords[0] if keywords else query.strip()
            try:
                lit_results = search_code(search_term, str(target_repo))
                for item in lit_results:
                    norm = self._normalize_item(item, "literal")
                    norm["semantic_score"] = 0.6
                    normalized_items.append(norm)
            except Exception:
                pass

        # 4. Relationship Search
        if "relationship" in strategies and (symbol_name or query):
            rel_target = symbol_name or query.strip()
            try:
                rel_data = find_relationships(rel_target, direction="both", repo_path=target_repo)
                all_rels = rel_data.get("outgoing", []) + rel_data.get("incoming", [])
                for rel in all_rels:
                    norm = self._normalize_item(rel, "relationship")
                    norm["semantic_score"] = 0.7
                    normalized_items.append(norm)
            except Exception:
                pass

        # Filter strictly by target_repo if specified
        if target_repo:
            from retrieval.code_search import is_file_in_repo
            normalized_items = [
                item for item in normalized_items
                if is_file_in_repo(item.get("file", ""), target_repo)
            ]

        # Rank items using deterministic ranker
        ranked_items = rank_evidence_items(
            normalized_items,
            query=query,
            keywords=keywords,
            symbol_name=symbol_name
        )

        global_cache.set("retrieval", cache_key, ranked_items)
        return ranked_items[:limit]
