import React, { useState } from "react";
import { Boxes, Search, FileCode, ArrowUpRight, Loader2, AlertCircle } from "lucide-react";
import { getSymbolInfo } from "../../lib/api";
import { SymbolItem } from "../../lib/types";

interface SymbolExplorerProps {
  repoId: string;
  onNavigateToCode: (filePath: string, startLine: number, endLine: number) => void;
}

export function SymbolExplorer({ repoId, onNavigateToCode }: SymbolExplorerProps) {
  const [symbolQuery, setSymbolQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [symbols, setSymbols] = useState<SymbolItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (name: string) => {
    if (!name.trim() || !repoId) return;
    setLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const res = await getSymbolInfo(repoId, name.trim());
      setSymbols(res.symbols || []);
    } catch (err: any) {
      setError(err.message || "Symbol lookup failed.");
      setSymbols([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Search Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
            <Boxes className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Symbol Explorer</h1>
            <p className="text-xs text-slate-500">
              Lookup exact class, function, and method definitions in <code className="font-mono text-slate-800 bg-slate-100 px-1 py-0.5 rounded">{repoId}</code>.
            </p>
          </div>
        </div>

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch(symbolQuery);
          }}
          className="relative"
        >
          <input
            type="text"
            value={symbolQuery}
            onChange={(e) => setSymbolQuery(e.target.value)}
            placeholder="Enter symbol name (e.g. RequestContext, wsgi_app, Flask)..."
            className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-4 pr-24 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all font-mono"
          />
          <button
            type="submit"
            disabled={loading || !symbolQuery.trim()}
            className="absolute right-2 top-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white px-4 py-1.5 rounded-md font-medium text-xs flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            <span>Lookup</span>
          </button>
        </form>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Empty state */}
      {hasSearched && !loading && !error && symbols.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-xs text-slate-500">
          No symbol definitions found matching &quot;{symbolQuery}&quot; in {repoId}.
        </div>
      )}

      {/* Symbol Results */}
      {symbols.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-1">
            Found {symbols.length} symbol definitions
          </h2>

          <div className="space-y-3">
            {symbols.map((sym, idx) => (
              <div key={idx} className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex items-center justify-between">
                <div className="space-y-1 font-mono text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="text-base font-bold text-slate-900">{sym.name}</span>
                    <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded font-sans text-[11px] font-semibold uppercase">
                      {sym.type}
                    </span>
                    {sym.class && (
                      <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-[11px]">
                        Class: {sym.class}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-2 text-slate-500 pt-1">
                    <FileCode className="w-3.5 h-3.5 text-slate-400" />
                    <span>{sym.file}</span>
                    <span className="bg-slate-100 px-1.5 py-0.5 rounded text-[10px]">
                      Lines {sym.start_line} - {sym.end_line}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => onNavigateToCode(sym.file, sym.start_line, sym.end_line)}
                  className="flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-800 text-white px-3 py-2 rounded-lg font-medium text-xs transition-colors shadow-xs cursor-pointer"
                >
                  <span>View Source</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
