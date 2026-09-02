import React, { useState } from "react";
import {
  Sparkles,
  Send,
  CheckCircle2,
  FileCode,
  ArrowUpRight,
  Loader2,
  AlertCircle,
  Activity,
  Layers,
  RotateCcw
} from "lucide-react";
import { askMentor } from "../../lib/api";
import { AskResponse } from "../../lib/types";

interface AskMentorProps {
  repoId: string;
  onNavigateToCode: (filePath: string, startLine: number, endLine: number) => void;
}

const GENERIC_QUESTIONS = [
  "What are the main entry points and high-level architecture of this repository?",
  "How does request context or state management work here?",
  "Where is primary routing, view dispatching, or request handling implemented?",
  "How does error handling and exception logging work in this codebase?"
];

export function AskMentor({ repoId, onNavigateToCode }: AskMentorProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [progressStep, setProgressStep] = useState<number>(0);
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const steps = [
    "Analyzing question & architecture pattern",
    "Searching semantic vector store & symbol index",
    "Tracing static call-graph relationships",
    "Synthesizing grounded explanation with code evidence"
  ];

  const handleSubmit = async (q: string) => {
    if (!q.trim() || !repoId) return;
    setLoading(true);
    setError(null);
    setResponse(null);
    setProgressStep(1);

    const timer1 = setTimeout(() => setProgressStep(2), 700);
    const timer2 = setTimeout(() => setProgressStep(3), 1500);

    try {
      const res = await askMentor(repoId, q);
      setResponse(res);
      setProgressStep(4);
    } catch (err: any) {
      let msg = err.message || "Failed to complete AI investigation.";
      if (msg.includes("429") || msg.toLowerCase().includes("quota")) {
        msg = "AI analysis is temporarily unavailable because the configured Gemini quota has been exhausted (HTTP 429).";
      }
      setError(msg);
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Ask Prompt Header */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">Ask AI Codebase Mentor</h1>
            <p className="text-xs text-slate-500">
              Query <code className="font-mono text-slate-800 bg-slate-100 px-1 py-0.5 rounded">{repoId}</code> using backend multi-strategy retrieval, symbol graph, and evidence agent.
            </p>
          </div>
        </div>

        {/* Input Prompt Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit(question);
          }}
          className="relative"
        >
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={`Ask anything about ${repoId}...`}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-4 pr-24 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="absolute right-2 top-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white px-4 py-1.5 rounded-md font-medium text-xs flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span>Ask</span>
          </button>
        </form>

        {/* Preset Question Chips */}
        <div className="space-y-1.5 pt-1">
          <span className="text-[11px] font-medium text-slate-400">Suggested Questions:</span>
          <div className="flex flex-wrap gap-2">
            {GENERIC_QUESTIONS.map((pq) => (
              <button
                key={pq}
                onClick={() => {
                  setQuestion(pq);
                  handleSubmit(pq);
                }}
                className="text-xs bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 px-3 py-1 rounded-full border border-slate-200 transition-colors text-left cursor-pointer"
              >
                {pq}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Investigation Progress Step Tracker */}
      {loading && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-800">
            <Activity className="w-4 h-4 text-indigo-600 animate-spin" />
            <span>Investigating Repository ({repoId})...</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
            {steps.map((st, idx) => {
              const isDone = progressStep > idx + 1;
              const isCurrent = progressStep === idx + 1;
              return (
                <div
                  key={st}
                  className={`p-2.5 rounded-lg border text-xs flex items-center space-x-2 ${
                    isDone
                      ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                      : isCurrent
                      ? "bg-indigo-50 border-indigo-200 text-indigo-800 font-medium"
                      : "bg-slate-50 border-slate-200 text-slate-400"
                  }`}
                >
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-indigo-600 animate-spin shrink-0" />
                  ) : (
                    <span className="w-4 h-4 rounded-full border text-[10px] flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>
                  )}
                  <span className="truncate">{st}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error Alert Banner */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-5 rounded-xl text-xs space-y-3 shadow-xs">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 shrink-0 text-red-600 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-red-800 block text-sm">AI Investigation Failed</span>
              <p className="text-red-700 leading-relaxed">{error}</p>
            </div>
          </div>

          <button
            onClick={() => handleSubmit(question)}
            className="flex items-center space-x-1.5 bg-red-700 hover:bg-red-800 text-white px-3 py-1.5 rounded text-xs font-medium transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry Question</span>
          </button>
        </div>
      )}

      {/* Grounded Answer & Evidence Section */}
      {response && !loading && (
        <div className="space-y-6">
          {/* AI Explanation Panel */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                  Grounded AI Explanation
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Iterations: {response.state?.iterations ?? 0} · Tool Calls: {response.state?.tool_calls ?? 0}
                </span>
              </div>
              <span className="text-xs text-slate-400 font-mono">Status: {response.status}</span>
            </div>

            {/* Answer Content */}
            <div className="prose prose-slate max-w-none text-sm text-slate-800 leading-relaxed whitespace-pre-line font-sans">
              {response.answer || response.warning || "No grounded answer generated."}
            </div>
          </div>

          {/* Evidence Cards Panel */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Layers className="w-4 h-4 text-slate-600" />
                <span>Supporting Code Evidence ({(response.evidence || []).length})</span>
              </h2>
              <span className="text-xs text-slate-400">Ranked by retrieval score</span>
            </div>

            {(!response.evidence || response.evidence.length === 0) ? (
              <div className="bg-white border border-slate-200 rounded-xl p-4 text-xs text-slate-400 italic text-center">
                No explicit code snippets were attached as evidence for this response.
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {response.evidence.map((item, idx) => (
                  <div
                    key={idx}
                    className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-3 hover:border-slate-300 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-xs font-mono">
                        <FileCode className="w-4 h-4 text-indigo-600 shrink-0" />
                        <span className="font-semibold text-slate-800">{item.file}</span>
                        <span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded text-[11px]">
                          L{item.start_line}-{item.end_line}
                        </span>
                        {item.symbol && (
                          <span className="bg-indigo-50 text-indigo-700 font-semibold px-2 py-0.5 rounded text-[11px] border border-indigo-100">
                            {item.symbol}
                          </span>
                        )}
                      </div>

                      {/* Jump to Code Action */}
                      <div className="flex items-center space-x-3">
                        {item.rank_score && (
                          <span className="text-[11px] font-mono font-medium text-slate-500 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded">
                            Score: {item.rank_score}
                          </span>
                        )}
                        <button
                          onClick={() => onNavigateToCode(item.file, item.start_line, item.end_line)}
                          className="flex items-center space-x-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 px-2.5 py-1 rounded transition-colors cursor-pointer"
                        >
                          <span>Jump to Code</span>
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
            )}
          </div>
        </div>
      )}
    </div>
  );
}
