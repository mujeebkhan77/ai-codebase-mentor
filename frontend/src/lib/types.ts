export interface Manifest {
  repository_name: string;
  total_files: number;
  languages: Record<string, number>;
  source_directories: string[];
  test_directories: string[];
  config_files: string[];
  entry_points: string[];
  symbols_summary: {
    total_symbols: number;
    classes_count: number;
    functions_count: number;
    methods_count: number;
  };
  relationships_summary: {
    total_relationships: number;
    top_called_symbols: Array<{ symbol: string; call_count: number }>;
  };
}

export interface RepoInfo {
  repo_id: string;
  repo_path: string;
  manifest: Manifest | null;
}

export interface DeleteRepoResponse {
  repo_id: string;
  message: string;
}

export interface FileContentResponse {
  repo_id: string;
  path: string;
  content: string;
}

export interface SearchResultItem {
  source_type: "semantic" | "symbol" | "literal" | "relationship";
  file: string;
  start_line: number;
  end_line: number;
  symbol: string | null;
  content: string;
  rank_score: number;
  score_breakdown?: {
    semantic_similarity: number;
    symbol_exact_match: number;
    keyword_density: number;
    source_code_factor: number;
    relationship_factor: number;
  };
  metadata?: Record<string, any>;
}

export interface SearchResponse {
  repo_id: string;
  query: string;
  total_results: number;
  results: SearchResultItem[];
}

export interface SymbolItem {
  name: string;
  type: "class" | "function" | "method";
  class: string | null;
  file: string;
  start_line: number;
  end_line: number;
}

export interface SymbolResponse {
  repo_id: string;
  symbol_name: string;
  total_matches: number;
  symbols: SymbolItem[];
}

export interface RelationshipItem {
  caller: string;
  callee: string;
  file: string;
  line: number;
  target_file?: string;
  target_class?: string;
  target_type?: string;
  target_start_line?: number;
  target_end_line?: number;
}

export interface RelationshipResponse {
  repo_id: string;
  symbol_name: string;
  direction: "outgoing" | "incoming" | "both";
  outgoing: RelationshipItem[];
  incoming: RelationshipItem[];
}

export interface AskResponse {
  repo_id: string;
  question: string;
  status: "completed" | "quota_exhausted" | "limit_reached" | "error";
  answer: string | null;
  warning?: string | null;
  error?: string | null;
  state: {
    question: string;
    repo_path: string;
    iterations: number;
    tool_calls: number;
    discovered_files_count: number;
    discovered_symbols_count: number;
    discovered_relationships_count: number;
    total_evidence_items: number;
  };
  evidence: SearchResultItem[];
}
