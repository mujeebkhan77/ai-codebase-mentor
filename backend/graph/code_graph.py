import json
from pathlib import Path
from typing import Dict, List, Any, Optional


from retrieval.code_search import is_file_in_repo


class CodeGraph:
    """
    Codebase Graph providing clean graph operations on top of the existing
    symbol_index.json and relationship_index.json files.
    """

    def __init__(
        self,
        symbol_index_path: str | Path = "symbol_index.json",
        relationship_index_path: str | Path = "relationship_index.json",
        repo_path: Optional[str] = None
    ):
        self.symbol_index_path = Path(symbol_index_path)
        self.relationship_index_path = Path(relationship_index_path)
        self.repo_path = repo_path

        raw_symbols = self._load_json(self.symbol_index_path)
        raw_relationships = self._load_json(self.relationship_index_path)

        if self.repo_path:
            self.symbols = [
                s for s in raw_symbols
                if is_file_in_repo(s.get("file", ""), self.repo_path)
            ]
            self.relationships = [
                r for r in raw_relationships
                if is_file_in_repo(r.get("file") or r.get("target_file") or "", self.repo_path)
            ]
        else:
            self.symbols = raw_symbols
            self.relationships = raw_relationships

    def _load_json(self, path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def reload(self) -> None:
        """Reload symbols and relationships from index files."""
        raw_symbols = self._load_json(self.symbol_index_path)
        raw_relationships = self._load_json(self.relationship_index_path)
        if self.repo_path:
            self.symbols = [
                s for s in raw_symbols
                if is_file_in_repo(s.get("file", ""), self.repo_path)
            ]
            self.relationships = [
                r for r in raw_relationships
                if is_file_in_repo(r.get("file") or r.get("target_file") or "", self.repo_path)
            ]
        else:
            self.symbols = raw_symbols
            self.relationships = raw_relationships

    def get_outgoing_calls(self, symbol_name: str) -> List[Dict[str, Any]]:
        """Find symbols called by symbol_name (callees)."""
        symbol_name = symbol_name.strip()
        results = []
        for rel in self.relationships:
            caller = rel.get("caller")
            if caller == symbol_name or (caller and caller.split(".")[-1] == symbol_name):
                results.append(rel)
        return results

    def get_incoming_callers(self, symbol_name: str) -> List[Dict[str, Any]]:
        """Find symbols that call symbol_name (callers)."""
        symbol_name = symbol_name.strip()
        results = []
        for rel in self.relationships:
            callee = rel.get("callee")
            if callee == symbol_name or (callee and callee.split(".")[-1] == symbol_name):
                results.append(rel)
        return results

    def get_class_methods(self, class_name: str) -> List[Dict[str, Any]]:
        """Find all methods belonging to a specific class."""
        class_name = class_name.strip()
        return [
            sym for sym in self.symbols
            if sym.get("type") == "method" and sym.get("class") == class_name
        ]

    def get_file_symbols(self, file_path: str) -> List[Dict[str, Any]]:
        """Find all symbols defined within a specific file."""
        norm_path = file_path.replace("\\", "/")
        results = []
        for sym in self.symbols:
            sf = str(sym.get("file", "")).replace("\\", "/")
            if sf == norm_path or sf.endswith(norm_path):
                results.append(sym)
        return results

    def get_symbol_file(self, symbol_name: str) -> List[Dict[str, Any]]:
        """Locate file(s) and line numbers defining symbol_name."""
        symbol_name = symbol_name.strip()
        results = []
        for sym in self.symbols:
            if sym.get("name") == symbol_name:
                results.append({
                    "name": sym.get("name"),
                    "type": sym.get("type"),
                    "class": sym.get("class"),
                    "file": str(sym.get("file", "")).replace("\\", "/"),
                    "start_line": sym.get("start_line"),
                    "end_line": sym.get("end_line"),
                })
        return results

    def get_call_chain(
        self,
        start_symbol: str,
        max_depth: int = 3,
        direction: str = "outgoing"
    ) -> List[Dict[str, Any]]:
        """
        Traverse multi-hop relationships starting from start_symbol.
        
        direction:
        - 'outgoing': trace what start_symbol calls
        - 'incoming': trace what calls start_symbol
        """
        visited = set()
        chain = []

        def trace(current: str, depth: int, path: List[str]):
            if depth > max_depth or current in visited:
                return
            visited.add(current)

            if direction == "outgoing":
                rels = self.get_outgoing_calls(current)
                next_key = "callee"
            else:
                rels = self.get_incoming_callers(current)
                next_key = "caller"

            for rel in rels:
                target = rel.get(next_key)
                if not target:
                    continue
                node = {
                    "from": current,
                    "to": target,
                    "depth": depth,
                    "file": rel.get("file"),
                    "line": rel.get("line"),
                    "target_file": rel.get("target_file"),
                    "target_class": rel.get("target_class"),
                    "path": path + [target]
                }
                chain.append(node)
                trace(target, depth + 1, path + [target])

        trace(start_symbol, 1, [start_symbol])
        return chain
