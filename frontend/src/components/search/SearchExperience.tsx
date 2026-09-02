import React, { useState } from "react";
import { Search, Filter, FileCode, ArrowUpRight, Loader2, AlertCircle } from "lucide-react";
import { searchCodebase } from "../../lib/api";
import { SearchResultItem } from "../../lib/types";

interface SearchExperienceProps {
  repoId: string;
  onNavigateToCode: (filePath: string, startLine: number, endLine: number) => void;
}

export function SearchExperience({ repoId, onNavigateToCode }: SearchExperienceProps) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState<string>("all");

  const strategies = [
    { id: "all", label: "All Strategies" },
    { id: "semantic", label: "Semantic Search" },
    { id: "symbol", label: "Symbol Search" },
    { id: "literal", label: "Literal Keyword" },
    { id: "relationship", label: "Call Graph" }
  ];

  const handleSearch = async (q: string) => {
    if (!q.trim() || !repoId) return;
    setLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const activeStrategies = selectedStrategy === "all" ? undefined : [selectedStrategy];
      const res = await searchCodebase(repoId, q, undefined, 10, activeStrategies);
      setResults(res.results || []);
    } catch (err: any) {
      setError(err.message || "Search request failed.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Search Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
            <Search className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Multi-Strategy Code Search</h1>
            <p className="text-xs text-slate-500">
              Querying <code className="font-mono text-slate-800 bg-slate-100 px-1 py-0.5 rounded">{repoId}</code> using vector semantic similarity, exact symbol matching, keyword search, and call-graph relationships.
            </p>
          </div>
        </div>

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch(query);
          }}
          className="relative"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search keywords, classes, methods, or concepts..."
            className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-4 pr-24 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2 top-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white px-4 py-1.5 rounded-md font-medium text-xs flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            <span>Search</span>
          </button>
        </form>

        {/* Strategy Filter Pills */}
        <div className="flex items-center space-x-2 pt-1">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="text-xs text-slate-500 font-medium">Strategy:</span>
          <div className="flex flex-wrap gap-1.5">
            {strategies.map((s) => (
              <button
                key={s.id}
                onClick={() => {
                  setSelectedStrategy(s.id);
                  if (query.trim()) handleSearch(query);
                }}
                className={`text-xs px-2.5 py-1 rounded-md font-medium transition-colors cursor-pointer ${
                  selectedStrategy === s.id
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Empty result state */}
      {hasSearched && !loading && !error && results.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-xs text-slate-500">
          No code matches found for &quot;{query}&quot; in {repoId}. Try adjusting strategy or query terms.
        </div>
      )}

      {/* Results List */}
      {results.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span>Found {results.length} ranked results for &quot;{query}&quot;</span>
          </div>

          <div className="space-y-3">
            {results.map((item, idx) => (
              <div key={idx} className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs font-mono">
                    <FileCode className="w-4 h-4 text-indigo-600 shrink-0" />
                    <span className="font-semibold text-slate-800">{item.file}</span>
                    <span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[11px]">
                      L{item.start_line}-{item.end_line}
                    </span>
                    <span className="bg-slate-200 text-slate-700 uppercase font-bold text-[9px] px-1.5 py-0.5 rounded">
                      {item.source_type}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-xs font-mono font-bold text-slate-700 bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">
                      Score: {item.rank_score}
                    </span>
                    <button
                      onClick={() => onNavigateToCode(item.file, item.start_line, item.end_line)}
                      className="flex items-center space-x-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 px-2 py-1 rounded transition-colors cursor-pointer"
                    >
                      <span>Jump</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <pre className="bg-slate-900 text-slate-100 p-3 rounded-lg font-mono text-xs overflow-x-auto leading-relaxed">
                  {item.content}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
