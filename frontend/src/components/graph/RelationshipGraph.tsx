import React, { useState } from "react";
import { GitFork, ArrowRight, CornerDownRight, Search, Loader2, AlertCircle } from "lucide-react";
import { getRelationships } from "../../lib/api";
import { RelationshipResponse } from "../../lib/types";

interface RelationshipGraphProps {
  repoId: string;
  onNavigateToCode: (filePath: string, startLine: number, endLine: number) => void;
}

export function RelationshipGraph({ repoId, onNavigateToCode }: RelationshipGraphProps) {
  const [symbolName, setSymbolName] = useState("");
  const [queryInput, setQueryInput] = useState("");
  const [data, setData] = useState<RelationshipResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLookup = async (sym: string) => {
    if (!sym.trim() || !repoId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getRelationships(repoId, sym.trim(), "both");
      setData(res);
      setSymbolName(sym.trim());
    } catch (err: any) {
      setError(err.message || "Failed to fetch relationship graph.");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header & Symbol Input */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
            <GitFork className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Call Graph & Relationships</h1>
            <p className="text-xs text-slate-500">
              Inspect static call-graph caller and callee relationships for <code className="font-mono text-slate-800 bg-slate-100 px-1 py-0.5 rounded">{repoId}</code>.
            </p>
          </div>
        </div>

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLookup(queryInput);
          }}
          className="relative"
        >
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Enter target symbol name to inspect relationships (e.g. Flask, render_template)..."
            className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-4 pr-24 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all font-mono"
          />
          <button
            type="submit"
            disabled={loading || !queryInput.trim()}
            className="absolute right-2 top-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white px-4 py-1.5 rounded-md font-medium text-xs flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            <span>Inspect</span>
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

      {/* Visual Call Graph Layout */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Outgoing Callees Panel */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <ArrowRight className="w-4 h-4 text-purple-600" />
                <span>Outgoing Callees (What `{symbolName}` calls)</span>
              </h2>
              <span className="text-[11px] font-mono bg-purple-50 text-purple-700 px-2 py-0.5 rounded border border-purple-100 font-bold">
                {(data.outgoing || []).length} calls
              </span>
            </div>

            {(!data.outgoing || data.outgoing.length === 0) ? (
              <div className="text-xs text-slate-400 italic p-3 text-center">No outgoing callees recorded for `{symbolName}`.</div>
            ) : (
              <div className="space-y-3 font-mono text-xs">
                {data.outgoing.map((rel, idx) => (
                  <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2 hover:border-purple-300 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <CornerDownRight className="w-4 h-4 text-purple-600 shrink-0" />
                        <span className="font-bold text-slate-900 text-sm">{rel.callee}</span>
                      </div>
                      {rel.target_class && (
                        <span className="bg-slate-200 text-slate-700 text-[10px] px-1.5 py-0.5 rounded">
                          Class: {rel.target_class}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center justify-between text-slate-500 text-[11px] pt-1">
                      <span className="truncate">{rel.file}:{rel.line}</span>
                      {rel.target_file && (
                        <button
                          onClick={() => onNavigateToCode(rel.target_file!, rel.target_start_line || 1, rel.target_end_line || 10)}
                          className="text-purple-600 hover:text-purple-800 font-sans font-medium cursor-pointer"
                        >
                          Inspect Code
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Incoming Callers Panel */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <GitFork className="w-4 h-4 text-indigo-600" />
                <span>Incoming Callers (What calls `{symbolName}`)</span>
              </h2>
              <span className="text-[11px] font-mono bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-100 font-bold">
                {(data.incoming || []).length} callers
              </span>
            </div>

            {(!data.incoming || data.incoming.length === 0) ? (
              <div className="text-xs text-slate-400 italic p-3 text-center">No incoming callers recorded for `{symbolName}`.</div>
            ) : (
              <div className="space-y-3 font-mono text-xs">
                {data.incoming.map((rel, idx) => (
                  <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2 hover:border-indigo-300 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-slate-900 text-sm">{rel.caller}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-indigo-500" />
                        <span className="text-slate-600">{symbolName}</span>
                      </div>
                    </div>

                    <div className="text-slate-500 text-[11px] pt-1">
                      <span>{rel.file}:{rel.line}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
