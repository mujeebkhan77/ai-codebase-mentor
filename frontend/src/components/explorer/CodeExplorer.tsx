import React, { useState, useEffect } from "react";
import { Folder, FileCode2, Loader2, AlertCircle } from "lucide-react";
import { CodeViewer } from "../code/CodeViewer";
import { getFileContent } from "../../lib/api";

interface CodeExplorerProps {
  repoId: string;
  structureStr: string;
  initialSelectedFile?: string;
  initialLineRange?: { start: number; end: number };
}

export function CodeExplorer({
  repoId,
  structureStr,
  initialSelectedFile,
  initialLineRange
}: CodeExplorerProps) {
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [fileContent, setFileContent] = useState<string>("");
  const [loadingFile, setLoadingFile] = useState<boolean>(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const [highlightedRange, setHighlightedRange] = useState<{ start: number; end: number } | undefined>(initialLineRange);

  // Parse structure string lines into file list
  const filePaths: string[] = React.useMemo(() => {
    if (!structureStr) return [];
    const rawLines = structureStr.split("\n");
    const result: string[] = [];
    
    for (const raw of rawLines) {
      const trimmed = raw.trim();
      if (!trimmed || trimmed.endsWith("/")) continue;
      const cleanPath = trimmed.replace(/^[├└──\s|]+/, "").trim();
      if (cleanPath && !cleanPath.endsWith("/") && !result.includes(cleanPath)) {
        result.push(cleanPath);
      }
    }
    return result;
  }, [structureStr]);

  // Set initial selected file
  useEffect(() => {
    if (initialSelectedFile) {
      const relative = initialSelectedFile.includes(`repositories/${repoId}/`)
        ? initialSelectedFile.split(`repositories/${repoId}/`)[1]
        : initialSelectedFile;
      setSelectedFile(relative || initialSelectedFile);
    } else if (filePaths.length > 0 && !selectedFile) {
      setSelectedFile(filePaths[0]);
    }
  }, [initialSelectedFile, filePaths, repoId]);

  useEffect(() => {
    if (initialLineRange) {
      setHighlightedRange(initialLineRange);
    }
  }, [initialLineRange]);

  // Fetch real file content whenever selectedFile or repoId changes
  useEffect(() => {
    async function fetchContent() {
      if (!selectedFile || !repoId) return;
      setLoadingFile(true);
      setFileError(null);
      try {
        const res = await getFileContent(repoId, selectedFile);
        setFileContent(res.content);
      } catch (err: any) {
        setFileError(err.message || "Failed to load file content from server.");
        setFileContent("");
      } finally {
        setLoadingFile(false);
      }
    }
    fetchContent();
  }, [repoId, selectedFile]);

  return (
    <div className="h-[calc(100vh-6rem)] grid grid-cols-12 gap-4">
      {/* File Tree Navigator Sidebar */}
      <div className="col-span-4 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs flex flex-col">
        <div className="bg-slate-50 border-b border-slate-200 px-3.5 py-2.5 flex items-center justify-between text-xs font-semibold text-slate-700">
          <div className="flex items-center space-x-2">
            <Folder className="w-4 h-4 text-indigo-600" />
            <span>Repository Structure</span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">{filePaths.length} items</span>
        </div>

        <div className="flex-1 overflow-auto p-2 space-y-0.5 text-xs font-mono">
          {filePaths.length === 0 ? (
            <div className="text-slate-400 text-xs p-3 italic">Loading repository tree...</div>
          ) : (
            filePaths.map((filePath) => {
              const isSelected = selectedFile === filePath;
              return (
                <button
                  key={filePath}
                  onClick={() => {
                    setSelectedFile(filePath);
                    setHighlightedRange(undefined);
                  }}
                  className={`w-full flex items-center space-x-2 px-2.5 py-1.5 rounded transition-colors text-left cursor-pointer ${
                    isSelected ? "bg-slate-900 text-white font-medium shadow-xs" : "text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  <FileCode2 className={`w-3.5 h-3.5 shrink-0 ${isSelected ? "text-indigo-400" : "text-slate-400"}`} />
                  <span className="truncate">{filePath}</span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Code Viewer Panel */}
      <div className="col-span-8 h-full flex flex-col">
        {loadingFile ? (
          <div className="bg-white border border-slate-200 rounded-xl h-full flex items-center justify-center text-xs text-slate-500 space-x-2">
            <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
            <span>Loading raw file content from repository...</span>
          </div>
        ) : fileError ? (
          <div className="bg-white border border-red-200 rounded-xl h-full p-6 flex flex-col items-center justify-center text-center space-y-2">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <span className="text-xs font-bold text-red-700">{fileError}</span>
            <span className="text-[11px] text-slate-400">File: {selectedFile}</span>
          </div>
        ) : (
          <CodeViewer
            filePath={selectedFile}
            codeContent={fileContent}
            startLine={1}
            highlightedRange={highlightedRange}
          />
        )}
      </div>
    </div>
  );
}
