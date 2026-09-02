from pathlib import Path
from typing import Dict, List, Any, Optional


class EvidenceManager:
    """
    Evidence Manager responsible for collecting, normalizing, deduplicating,
    merging overlapping line ranges, context budgeting, and formatting evidence
    for the LLM.
    """

    def __init__(self, max_context_chars: int = 12000, repo_path: Optional[str] = None):
        self.max_context_chars = max_context_chars
        self.repo_path = repo_path
        self.evidence_items: List[Dict[str, Any]] = []

    def _normalize(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure item has normalized fields."""
        metadata = item.get("metadata") or {}

        file_path = str(
            item.get("file") or
            item.get("file_path") or
            item.get("target_file") or
            metadata.get("file") or
            metadata.get("file_path") or
            ""
        ).replace("\\", "/")

        start_line = int(
            item.get("start_line") or
            item.get("line") or
            item.get("target_start_line") or
            metadata.get("start_line") or
            metadata.get("line") or
            1
        )

        end_line = int(
            item.get("end_line") or
            item.get("target_end_line") or
            metadata.get("end_line") or
            start_line
        )

        symbol = (
            item.get("symbol") or
            item.get("name") or
            item.get("class") or
            metadata.get("name") or
            metadata.get("symbol") or
            metadata.get("class") or
            None
        )

        content = item.get("content") or item.get("snippet") or ""

        return {
            "source_type": item.get("source_type", "unknown"),
            "file": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "symbol": symbol,
            "content": content,
            "rank_score": float(item.get("rank_score", 0.5)),
            "metadata": metadata,
            "raw": item
        }

    def add_item(self, item: Dict[str, Any]) -> None:
        """Add a single evidence item."""
        normalized = self._normalize(item)
        if self.repo_path and normalized.get("file"):
            from retrieval.code_search import is_file_in_repo
            if not is_file_in_repo(normalized["file"], self.repo_path):
                return
        self.evidence_items.append(normalized)

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        """Add multiple evidence items."""
        for item in items:
            self.add_item(item)

    def deduplicate(self) -> None:
        """Remove exact duplicate evidence items."""
        seen = set()
        unique = []
        for item in self.evidence_items:
            key = (
                item["file"],
                item["start_line"],
                item["end_line"],
                item["symbol"],
                item["content"].strip()
            )
            if key not in seen:
                seen.add(key)
                unique.append(item)
        self.evidence_items = unique

    def merge_overlapping_ranges(self) -> None:
        """
        Merge overlapping or contiguous line ranges from the same file.
        Prevents fragmented snippets for the same code region.
        """
        if not self.evidence_items:
            return

        self.deduplicate()

        # Group items by file path
        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for item in self.evidence_items:
            file_key = item["file"]
            by_file.setdefault(file_key, []).append(item)

        merged_items: List[Dict[str, Any]] = []

        for file_path, items in by_file.items():
            if not file_path:
                merged_items.extend(items)
                continue

            # Sort items by start_line
            items.sort(key=lambda x: x["start_line"])
            current = items[0]

            for next_item in items[1:]:
                # If ranges overlap or touch (e.g. end_line >= next.start_line - 1)
                if current["end_line"] >= next_item["start_line"] - 1:
                    # Merge line range
                    current["end_line"] = max(current["end_line"], next_item["end_line"])
                    # Combine content if different
                    if next_item["content"] and next_item["content"] not in current["content"]:
                        current["content"] = f"{current['content']}\n...\n{next_item['content']}"
                    # Combine symbols if present
                    if next_item["symbol"] and next_item["symbol"] != current["symbol"]:
                        if current["symbol"]:
                            current["symbol"] = f"{current['symbol']}, {next_item['symbol']}"
                        else:
                            current["symbol"] = next_item["symbol"]
                    # Take higher rank score
                    current["rank_score"] = max(current["rank_score"], next_item["rank_score"])
                else:
                    merged_items.append(current)
                    current = next_item

            merged_items.append(current)

        self.evidence_items = merged_items

    def get_prioritized_evidence(
        self,
        max_items: int = 15,
        max_chars: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate, merge ranges, sort by rank_score, and return evidence
        fitting within the context character budget.
        """
        self.merge_overlapping_ranges()

        # Sort descending by rank_score
        sorted_items = sorted(
            self.evidence_items,
            key=lambda x: x["rank_score"],
            reverse=True
        )

        char_limit = max_chars or self.max_context_chars
        result = []
        accumulated_chars = 0

        for item in sorted_items[:max_items]:
            item_chars = len(item.get("content", "")) + len(item.get("file", "")) + 100
            if accumulated_chars + item_chars > char_limit and result:
                break
            result.append(item)
            accumulated_chars += item_chars

        return result

    def format_for_llm(
        self,
        max_items: int = 15,
        max_chars: Optional[int] = None
    ) -> str:
        """
        Format prioritized evidence into a structured markdown block for LLM prompt context.
        """
        prioritized = self.get_prioritized_evidence(max_items, max_chars)
        if not prioritized:
            return "No repository evidence collected yet."

        formatted_blocks = []
        for idx, item in enumerate(prioritized, 1):
            symbol_info = f" (Symbol: `{item['symbol']}`)" if item.get("symbol") else ""
            header = f"### Evidence {idx}: {item['file']} (Lines {item['start_line']}-{item['end_line']}){symbol_info}"
            content = item.get("content", "").strip()
            if not content:
                content = "[File location referenced, content not read yet]"

            block = f"{header}\n```\n{content}\n```"
            formatted_blocks.append(block)

        return "\n\n".join(formatted_blocks)

    def clear() -> None:
        self.evidence_items.clear()
