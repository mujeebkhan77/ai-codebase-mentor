import React, { useState } from "react";
import { Copy, Check, FileCode } from "lucide-react";

interface CodeViewerProps {
  filePath: string;
  codeContent: string;
  startLine?: number;
  highlightedRange?: { start: number; end: number };
}

export function CodeViewer({
  filePath,
  codeContent,
  startLine = 1,
  highlightedRange
}: CodeViewerProps) {
  const [copied, setCopied] = useState(false);

  const lines = codeContent.split("\n");

  const handleCopy = () => {
    navigator.clipboard.writeText(codeContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs flex flex-col h-full">
      {/* Code Header / Breadcrumbs */}
      <div className="bg-slate-50 border-b border-slate-200 px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-700 truncate">
          <FileCode className="w-4 h-4 text-indigo-600 shrink-0" />
          <span className="truncate">{filePath || "select a file..."}</span>
          {highlightedRange && (
            <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-1.5 py-0.5 rounded border border-amber-200">
              L{highlightedRange.start}-{highlightedRange.end}
            </span>
          )}
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center space-x-1 text-xs text-slate-500 hover:text-slate-900 bg-white border border-slate-200 px-2 py-1 rounded hover:bg-slate-100 transition-colors cursor-pointer"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>

      {/* Code Viewport with Line Numbers */}
      <div className="flex-1 overflow-auto font-mono text-xs leading-relaxed bg-[#fafafa]">
        <table className="w-full border-collapse">
          <tbody>
            {lines.map((lineText, idx) => {
              const lineNumber = startLine + idx;
              const isHighlighted =
                highlightedRange &&
                lineNumber >= highlightedRange.start &&
                lineNumber <= highlightedRange.end;

              return (
                <tr
                  key={idx}
                  id={`L${lineNumber}`}
                  className={`group transition-colors ${
                    isHighlighted ? "bg-amber-50/90 border-l-4 border-amber-500" : "hover:bg-slate-100/60"
                  }`}
                >
                  {/* Line Number Column */}
                  <td className="w-12 select-none text-right pr-3 py-0.5 text-slate-400 font-mono text-[11px] border-r border-slate-200 bg-slate-50/50 group-hover:text-slate-600">
                    {lineNumber}
                  </td>
                  {/* Code Line Content */}
                  <td className="pl-4 pr-4 py-0.5 whitespace-pre text-slate-800 font-mono">
                    {lineText || " "}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
