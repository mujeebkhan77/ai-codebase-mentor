import hashlib
import json
from typing import Dict, List, Set, Any, Optional
from evidence.manager import EvidenceManager


class InvestigationState:
    """
    Lightweight state tracker for an active repository investigation session.
    Tracks user question, repo path, tools called with argument hashes to prevent duplicate calls,
    discovered files, symbols, relationships, evidence collected, and iteration counts.
    """

    def __init__(self, question: str, repo_path: Optional[str] = None):
        self.question = question
        self.repo_path = repo_path
        self.iteration_count = 0
        self.tool_call_count = 0

        # Argument hash tracking to prevent identical tool calls
        self._executed_tool_hashes: Set[str] = set()

        # Discovered items tracking
        self.discovered_files: Set[str] = set()
        self.discovered_symbols: Set[str] = set()
        self.discovered_relationships: List[Dict[str, Any]] = []

        # Tools history
        self.tools_used: List[Dict[str, Any]] = []

        # Evidence Manager instance
        self.evidence_manager = EvidenceManager(repo_path=repo_path)

    def _hash_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Create a deterministic hash string for a tool call."""
        canonical_args = json.dumps(tool_args, sort_keys=True, default=str)
        raw_key = f"{tool_name}:{canonical_args}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def is_duplicate_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> bool:
        """Check if this tool call with these arguments has already been executed."""
        tool_hash = self._hash_tool_call(tool_name, tool_args)
        return tool_hash in self._executed_tool_hashes

    def record_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        result: Any,
        status: str = "success"
    ) -> None:
        """Record executed tool call and track discovered entities."""
        tool_hash = self._hash_tool_call(tool_name, tool_args)
        self._executed_tool_hashes.add(tool_hash)
        self.tool_call_count += 1

        record = {
            "index": self.tool_call_count,
            "tool_name": tool_name,
            "args": tool_args,
            "status": status,
        }
        self.tools_used.append(record)

        # Automatically extract discovered entities from tool results
        self._extract_discovered_entities(tool_name, tool_args, result)

    def _extract_discovered_entities(self, tool_name: str, tool_args: Dict[str, Any], result: Any) -> None:
        """Extract files, symbols, and relationships from tool outputs."""
        if not result:
            return

        # Special handling for read_file
        if tool_name == "read_file" and isinstance(result, str) and not result.startswith("Error"):
            file_path = tool_args.get("file_path") or tool_args.get("file")
            if file_path:
                clean_path = str(file_path).replace("\\", "/")
                self.discovered_files.add(clean_path)
                s_line = tool_args.get("start_line") or 1
                e_line = tool_args.get("end_line") or (s_line + max(1, len(result.splitlines())) - 1)
                self.evidence_manager.add_item({
                    "source_type": "read_file",
                    "file": clean_path,
                    "start_line": s_line,
                    "end_line": e_line,
                    "content": result,
                    "rank_score": 0.95
                })
            return

        # Deserialise JSON string if returned by tools like find_symbol
        parsed_result = result
        if isinstance(result, str):
            if result.startswith("Error") or result.startswith("File "):
                return
            try:
                parsed_result = json.loads(result)
            except Exception:
                pass

        # Unpack relationship dictionary if returned by find_relationships
        if isinstance(parsed_result, dict) and ("outgoing" in parsed_result or "incoming" in parsed_result):
            rel_items = (parsed_result.get("outgoing") or []) + (parsed_result.get("incoming") or [])
            for rel in rel_items:
                if isinstance(rel, dict):
                    self.discovered_relationships.append(rel)
                    rel_file = rel.get("file") or rel.get("target_file")
                    if rel_file:
                        self.discovered_files.add(str(rel_file).replace("\\", "/"))
                    self.evidence_manager.add_item({
                        "source_type": "relationship",
                        "file": rel.get("file") or rel.get("target_file", ""),
                        "start_line": rel.get("line") or rel.get("target_start_line") or 1,
                        "end_line": rel.get("target_end_line") or rel.get("line") or 1,
                        "symbol": f"{rel.get('caller')} -> {rel.get('callee')}",
                        "content": f"{rel.get('caller')} calls {rel.get('callee')} at {rel.get('file')}:{rel.get('line')}",
                        "rank_score": 0.85
                    })
            return

        # Handle list of items or single item
        items = parsed_result if isinstance(parsed_result, list) else [parsed_result]

        for item in items:
            if isinstance(item, dict):
                metadata = item.get("metadata") or {}
                # Discovered files
                file_path = item.get("file") or item.get("file_path") or item.get("target_file") or metadata.get("file")
                if file_path:
                    self.discovered_files.add(str(file_path).replace("\\", "/"))

                # Discovered symbols
                sym = item.get("symbol") or item.get("name") or item.get("class") or metadata.get("name")
                if sym:
                    self.discovered_symbols.add(str(sym))

                # Discovered relationships
                if "caller" in item and "callee" in item:
                    self.discovered_relationships.append(item)

                # Add to evidence manager if it looks like code/evidence
                if "file" in item or "content" in item or "snippet" in item or metadata.get("file") or "page_content" in item:
                    self.evidence_manager.add_item(item)

    def increment_iteration(self) -> int:
        self.iteration_count += 1
        return self.iteration_count

    def get_summary(self) -> Dict[str, Any]:
        """Return a structured summary of the investigation state."""
        return {
            "question": self.question,
            "repo_path": self.repo_path,
            "iterations": self.iteration_count,
            "tool_calls": self.tool_call_count,
            "discovered_files_count": len(self.discovered_files),
            "discovered_symbols_count": len(self.discovered_symbols),
            "discovered_relationships_count": len(self.discovered_relationships),
            "total_evidence_items": len(self.evidence_manager.evidence_items),
        }
