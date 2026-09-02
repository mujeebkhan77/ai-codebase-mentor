import re
from typing import Dict, List, Any


def calculate_source_factor(file_path: str) -> float:
    """
    Returns 1.0 for main source code files, 0.2 for test files.
    """
    path_lower = file_path.replace("\\", "/").lower()
    if "/test/" in path_lower or "/tests/" in path_lower or "test_" in path_lower or "_test.py" in path_lower:
        return 0.2
    return 1.0


def calculate_keyword_density(text: str, keywords: List[str]) -> float:
    """
    Returns the proportion of query keywords present in text (0.0 to 1.0).
    """
    if not text or not keywords:
        return 0.0

    text_lower = text.lower()
    matches = sum(1 for kw in keywords if kw.lower() in text_lower)
    return matches / len(keywords)


def rank_evidence_items(
    items: List[Dict[str, Any]],
    query: str,
    keywords: List[str] = None,
    symbol_name: str = None
) -> List[Dict[str, Any]]:
    """
    Deterministically ranks evidence items using a normalized composite score (0.0 to 1.0).

    Scoring formula:
        composite_score = (
            0.40 * semantic_similarity +
            0.25 * symbol_exact_match +
            0.15 * keyword_match_density +
            0.10 * source_code_factor +
            0.10 * relationship_factor
        )

    Component Definitions:
    - semantic_similarity (0.0-1.0): Vector similarity or direct relevance score.
    - symbol_exact_match (0.0 or 1.0): 1.0 if item symbol matches query symbol_name.
    - keyword_match_density (0.0-1.0): Fraction of target query keywords found in content.
    - source_code_factor (0.2 or 1.0): 1.0 for source files, 0.2 penalty for test files.
    - relationship_factor (0.5 or 1.0): 1.0 if item comes from call-graph index.
    """
    if keywords is None:
        # Extract word tokens from query if keywords not specified
        keywords = [w for w in re.findall(r"\w+", query) if len(w) > 2]

    scored_items = []

    for item in items:
        # 1. Semantic similarity score (default to 0.5 if not provided)
        semantic_sim = item.get("semantic_score", 0.5)
        semantic_sim = max(0.0, min(1.0, float(semantic_sim)))

        # 2. Exact symbol match
        item_symbol = item.get("symbol") or item.get("name") or item.get("class")
        symbol_exact = 0.0
        if symbol_name and item_symbol:
            if item_symbol.lower() == symbol_name.lower():
                symbol_exact = 1.0
            elif symbol_name.lower() in item_symbol.lower():
                symbol_exact = 0.5

        # 3. Keyword match density
        content = item.get("content") or item.get("snippet") or ""
        file_path = item.get("file") or item.get("file_path") or ""
        combined_text = f"{file_path} {item_symbol or ''} {content}"
        kw_density = calculate_keyword_density(combined_text, keywords)

        # 4. Source vs Test factor
        source_factor = calculate_source_factor(file_path)

        # 5. Relationship factor
        is_relationship = item.get("source_type") == "relationship" or "caller" in item
        rel_factor = 1.0 if is_relationship else 0.5

        # Composite Score Calculation
        composite_score = (
            0.40 * semantic_sim +
            0.25 * symbol_exact +
            0.15 * kw_density +
            0.10 * source_factor +
            0.10 * rel_factor
        )

        item_copy = dict(item)
        item_copy["rank_score"] = round(composite_score, 4)
        item_copy["score_breakdown"] = {
            "semantic_similarity": round(semantic_sim, 2),
            "symbol_exact_match": symbol_exact,
            "keyword_density": round(kw_density, 2),
            "source_code_factor": source_factor,
            "relationship_factor": rel_factor,
        }
        scored_items.append(item_copy)

    # Sort descending by composite rank score
    scored_items.sort(key=lambda x: x["rank_score"], reverse=True)
    return scored_items
