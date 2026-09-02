import React from "react";
import {
  FileText,
  Boxes,
  GitFork,
  Code2,
  Terminal,
  FolderTree,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  AlertCircle,
  MessageSquareCode
} from "lucide-react";
import { RepoInfo } from "../../lib/types";

interface OverviewDashboardProps {
  repoInfo: RepoInfo | null;
  onNavigate: (tab: string) => void;
}

export function OverviewDashboard({ repoInfo, onNavigate }: OverviewDashboardProps) {
  if (!repoInfo) {
    return (
      <div className="max-w-4xl mx-auto p-8 text-center space-y-3 bg-white border border-slate-200 rounded-xl shadow-xs">
        <AlertCircle className="w-8 h-8 text-slate-400 mx-auto" />
        <h2 className="text-base font-bold text-slate-800">No Repository Selected</h2>
        <p className="text-xs text-slate-500">Please select or add a repository from the left sidebar to view intelligence metrics.</p>
      </div>
    );
  }

  const manifest = repoInfo.manifest;
  const repoName = manifest?.repository_name || repoInfo.repo_id;
  const repoPath = repoInfo.repo_path;
  const languages = manifest?.languages || {};
  const totalFiles = manifest?.total_files || 0;
  const symbols = manifest?.symbols_summary || { total_symbols: 0, classes_count: 0, functions_count: 0, methods_count: 0 };
  const relationships = manifest?.relationships_summary || { total_relationships: 0, top_called_symbols: [] };
  const entryPoints = manifest?.entry_points || [];
  const configFiles = manifest?.config_files || [];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight font-mono">{repoName}</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Indexed & Ready
            </span>
          </div>
          <p className="text-sm text-slate-500">
            Path: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs text-slate-700 font-mono">{repoPath}</code>
          </p>

          {/* Languages breakdown pills */}
          {Object.keys(languages).length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-2">
              {Object.entries(languages).map(([lang, count]) => (
                <span key={lang} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-slate-100 text-slate-700 border border-slate-200">
                  <span className="w-2 h-2 rounded-full bg-indigo-500 mr-1.5" />
                  {lang} ({count} files)
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Quick Ask CTA */}
        <button
          onClick={() => onNavigate("ask")}
          className="flex items-center space-x-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2.5 rounded-lg font-medium text-xs shadow-sm transition-colors cursor-pointer"
        >
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span>Ask AI Mentor</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* 4 Main Intelligence Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Total Files</span>
            <FileText className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">{totalFiles.toLocaleString()}</div>
          <p className="text-xs text-slate-500 mt-1">Source & test files</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">AST Symbols</span>
            <Boxes className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">{symbols.total_symbols.toLocaleString()}</div>
          <p className="text-xs text-slate-500 mt-1">
            {symbols.classes_count} classes · {symbols.functions_count} funcs · {symbols.methods_count} methods
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Relationships</span>
            <GitFork className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">{relationships.total_relationships.toLocaleString()}</div>
          <p className="text-xs text-slate-500 mt-1">Call-graph caller/callee links</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Vector Index</span>
            <Code2 className="w-5 h-5 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">384-dim</div>
          <p className="text-xs text-slate-500 mt-1">BAAI/bge-small-en-v1.5</p>
        </div>
      </div>

      {/* Details Grid: Entry Points, Configs & Top Symbols */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Entry Points & Config Files */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-indigo-600" />
            <span>Entry Points & Configuration</span>
          </h2>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-500 block mb-1 font-medium">Detected Entry Points:</span>
              {entryPoints.length === 0 ? (
                <div className="text-slate-400 italic">None detected</div>
              ) : (
                <div className="space-y-1">
                  {entryPoints.map((ep) => (
                    <div key={ep} className="bg-slate-50 border border-slate-200 px-2.5 py-1.5 rounded font-mono text-slate-800 flex items-center justify-between">
                      <span>{ep}</span>
                      <span className="text-[10px] text-indigo-600 font-semibold uppercase bg-indigo-50 px-1 rounded">Entry</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <span className="text-slate-500 block mb-1 font-medium">Config & Dependency Files:</span>
              {configFiles.length === 0 ? (
                <div className="text-slate-400 italic">None detected</div>
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {configFiles.map((cfg) => (
                    <span key={cfg} className="bg-slate-100 text-slate-700 px-2 py-1 rounded font-mono border border-slate-200">
                      {cfg}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Top Connected Call Graph Symbols */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
          <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <GitFork className="w-4 h-4 text-purple-600" />
            <span>Top Connected Symbols</span>
          </h2>

          <div className="space-y-2 text-xs">
            {relationships.top_called_symbols.length === 0 ? (
              <div className="text-slate-400 italic p-2">No call relationships indexed.</div>
            ) : (
              relationships.top_called_symbols.map((item) => (
                <div key={item.symbol} className="flex items-center justify-between p-2 rounded hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-colors">
                  <span className="font-mono text-slate-800 font-medium">{item.symbol}</span>
                  <span className="text-slate-500 text-[11px] font-medium bg-slate-100 px-2 py-0.5 rounded-full">
                    {item.call_count} calls
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
        <button
          onClick={() => onNavigate("ask")}
          className="text-left p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 hover:shadow-sm transition-all group cursor-pointer"
        >
          <MessageSquareCode className="w-6 h-6 text-indigo-600 mb-2 group-hover:scale-110 transition-transform" />
          <h3 className="text-sm font-semibold text-slate-900">Ask AI Codebase Mentor</h3>
          <p className="text-xs text-slate-500 mt-1">Ask questions grounded in actual repository code and evidence.</p>
        </button>

        <button
          onClick={() => onNavigate("explorer")}
          className="text-left p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 hover:shadow-sm transition-all group cursor-pointer"
        >
          <FolderTree className="w-6 h-6 text-emerald-600 mb-2 group-hover:scale-110 transition-transform" />
          <h3 className="text-sm font-semibold text-slate-900">Code Explorer</h3>
          <p className="text-xs text-slate-500 mt-1">Browse repository source files with syntax highlighting & line markers.</p>
        </button>

        <button
          onClick={() => onNavigate("relationships")}
          className="text-left p-4 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 hover:shadow-sm transition-all group cursor-pointer"
        >
          <GitFork className="w-6 h-6 text-purple-600 mb-2 group-hover:scale-110 transition-transform" />
          <h3 className="text-sm font-semibold text-slate-900">Call Graph Explorer</h3>
          <p className="text-xs text-slate-500 mt-1">Trace caller and callee relationships across repository symbols.</p>
        </button>
      </div>
    </div>
  );
}
