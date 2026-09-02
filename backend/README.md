# AI Codebase Mentor — Backend Engine

The backend engine for **AI Codebase Mentor**, a software engineering assistant designed to investigate GitHub repositories and answer technical questions using actual repository code, symbols, relationships, and evidence.

---

## Backend Architecture & Pipeline

```
GitHub Repository
       ↓
    [Clone]
       ↓
    [Index]
  ├── Chunks (AST-based function/method/class slicing)
  ├── Symbols (Class, function, method metadata)
  ├── Relationships (Caller-callee call-graph resolution)
  └── Repository Manifest (Languages, entry points, stats)
       ↓
 [Vectorstore (ChromaDB) + Local Embeddings (bge-small-en-v1.5)]
       ↓
 [Retrieval Engine]
  ├── Semantic Search (Vector similarity)
  ├── Symbol Search (Exact name matching)
  ├── Literal Search (File keyword search)
  └── Relationship Search (Call-graph traversal)
       ↓
    [Ranking] (Deterministic composite scoring)
       ↓
[Evidence Manager] (Deduplication, line range merging, context budgeting)
       ↓
 [Agent Controller] (Iteration & tool-call limits, duplicate prevention)
       ↓
     [LLM] (Gemini 2.5 Flash / Evidence-grounded response)
       ↓
Evidence-Grounded Technical Explanation
```

---

## Core Components

### 1. Indexing & Manifest (`indexing/`)
- `chunking.py`: AST-based chunking of Python files into standalone functions, classes, and methods.
- `symbols.py`: Extracts symbol definitions (name, type, class, line range, file path).
- `relationships.py`: Extracts and resolves caller-callee call-graph relationships.
- `manifest.py`: Generates deterministic repository metadata (`repository_manifest.json`) capturing repository name, language breakdown, entry points, configuration files, source/test directories, and symbol/relationship statistics.
- `index_repository.py`: Orchestrates full repo indexing.

### 2. Codebase Graph (`graph/code_graph.py`)
Provides clean graph queries on top of symbol and relationship indexes:
- Outgoing calls (`get_outgoing_calls`)
- Incoming callers (`get_incoming_callers`)
- Class methods (`get_class_methods`)
- File symbols (`get_file_symbols`)
- Multi-hop call-chain traversal (`get_call_chain`)

### 3. Retrieval Engine & Ranking (`retrieval/`)
- `engine.py`: Unified `RetrievalEngine` orchestrating semantic, symbol, literal, and relationship retrieval into normalized `EvidenceItem` structures.
- `ranking.py`: Deterministic score calculator combining semantic similarity, symbol exact matches, keyword density, source vs. test file weighting, and relationship factors.

### 4. Evidence Manager (`evidence/manager.py`)
- Normalizes and deduplicates search outputs.
- Merges overlapping or adjacent line ranges within the same file to prevent code snippet fragmentation.
- Enforces context character limits (`max_context_chars`).
- Formats evidence for LLM prompt context with line numbers and file paths.

### 5. Agent Controller & State (`agent/`)
- `controller.py`: Manages the agent investigation loop with strict limits:
  - `MAX_ITERATIONS` (default: 10)
  - `MAX_TOOL_CALLS` (default: 15)
  - `MAX_EVIDENCE_ITEMS` (default: 20)
  - `MAX_CONTEXT_SIZE` (default: 12000 chars)
  - Gracefully handles Gemini `429 RESOURCE_EXHAUSTED` quota errors without retrying.
- `state.py`: Tracks question context, tools used with argument hashing to prevent duplicate tool calls, discovered files, symbols, relationships, and iteration progress.

### 6. Caching & Error Handling (`utils/`)
- `caching.py`: In-memory `SimpleCache` for repository structure, symbols, relationships, and retrieval results.
- `errors.py`: Custom exception hierarchy (`LLMQuotaExhaustedError`, `RepositoryError`, `InvalidFileRangeError`, `IndexingError`).

---

## Tool Suite (`tools/`)

Existing tools preserved and enhanced:
- `clone_repository`: Shallow git clone of target repository.
- `get_repository_structure`: Tree representation of project structure (cached).
- `read_file`: Reads source files or line ranges with line numbers and error bounds.
- `search_code`: Literal string/keyword search.
- `find_symbol`: Exact symbol location lookup in symbol index.
- `semantic_code_search`: Conceptual similarity search via ChromaDB vectorstore.
- `find_relationships`: Incoming and outgoing relationship search.
- `get_repository_manifest`: Queries repository metadata and statistics.

---

## Testing

The backend includes a 100% deterministic test suite in `tests/` that runs without consuming Gemini API quota.

Run the test suite:
```bash
.\.venv\Scripts\python.exe -m pytest tests/
```

### Test Coverage:
- `test_chunking.py`: AST chunking logic.
- `test_indexing.py`: Indexing pipeline and JSON file outputs.
- `test_embeddings.py`: Local embeddings output shapes and dimensions.
- `test_retrieval.py`: Retrieval engine multi-strategy aggregation.
- `test_ranking.py`: Deterministic scoring rules and penalties.
- `test_symbols.py`: Symbol extraction and exact search.
- `test_relationships.py`: Caller-callee extraction and resolution.
- `test_evidence.py`: Evidence manager deduplication, range merging, and LLM formatting.
- `test_agent.py`: Agent controller limits, state tracking, duplicate call prevention, and 429 quota error handling (using mocks).
- `test_manifest.py`: Manifest generation and entry point detection.
- `test_graph.py`: Codebase graph call chain traversal.
- `test_caching.py`: In-memory cache hit, miss, and expiration behavior.
- `test_tools.py`: Tool execution and boundary error handling.

---

## Running the Backend Engine Demo

To run the backend demonstration script:
```bash
.\.venv\Scripts\python.exe main.py
```
