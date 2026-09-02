import React, { useState, useEffect } from "react";
import {
  Code2,
  FolderTree,
  MessageSquareCode,
  Search,
  GitFork,
  Boxes,
  PlusCircle,
  Activity,
  CheckCircle2,
  AlertCircle,
  Github,
  Trash2,
  Layers
} from "lucide-react";
import { checkHealth } from "../../lib/api";
import { RepoInfo } from "../../lib/types";

interface AppShellProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  activeRepoId: string;
  repoList: RepoInfo[];
  onSelectRepo: (repoId: string) => void;
  onOpenAddModal: () => void;
  onOpenDeleteModal: (repoId: string) => void;
  children: React.ReactNode;
}

export function AppShell({
  currentTab,
  onTabChange,
  activeRepoId,
  repoList,
  onSelectRepo,
  onOpenAddModal,
  onOpenDeleteModal,
  children
}: AppShellProps) {
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);

  useEffect(() => {
    async function verifyStatus() {
      const isConnected = await checkHealth();
      setApiConnected(isConnected);
    }
    verifyStatus();
    const interval = setInterval(verifyStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: "overview", label: "Overview", icon: Layers },
    { id: "explorer", label: "Code Explorer", icon: FolderTree },
    { id: "ask", label: "AI Mentor", icon: MessageSquareCode, badge: "AI" },
    { id: "search", label: "Multi-Search", icon: Search },
    { id: "symbols", label: "Symbols", icon: Boxes },
    { id: "relationships", label: "Call Graph", icon: GitFork }
  ];

  return (
    <div className="min-h-screen bg-[#fcfcfc] text-slate-900 flex flex-col font-sans antialiased">
      {/* Header */}
      <header className="h-14 border-b border-slate-200 bg-white px-4 flex items-center justify-between sticky top-0 z-30 shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold shadow-sm">
            <Code2 className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-slate-900 tracking-tight text-sm">AI Codebase Mentor</span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-indigo-50 text-indigo-700 rounded-md border border-indigo-100">
                PRO ENGINE
              </span>
            </div>
          </div>
        </div>

        {/* Header Details */}
        <div className="flex items-center space-x-4 text-xs">
          {/* Active Repo Badge */}
          <div className="flex items-center space-x-2 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md">
            <Github className="w-3.5 h-3.5 text-slate-500" />
            <span className="text-slate-500">Active Repo:</span>
            <span className="font-medium text-slate-800 font-mono">{activeRepoId || "None"}</span>
          </div>

          {/* Real API Status */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md border text-xs">
            {apiConnected === null ? (
              <Activity className="w-3.5 h-3.5 text-slate-400 animate-spin" />
            ) : apiConnected ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                <span className="text-emerald-700 font-medium bg-emerald-50 px-1 rounded">Backend Connected</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                <span className="text-red-700 font-medium bg-red-50 px-1 rounded">Backend Offline</span>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-64 border-r border-slate-200 bg-white flex flex-col justify-between shrink-0">
          <div className="p-3 space-y-4">
            {/* Repositories Switcher */}
            <div>
              <div className="flex items-center justify-between px-2 mb-1.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Repositories</span>
                <button
                  onClick={onOpenAddModal}
                  className="text-slate-400 hover:text-indigo-600 transition-colors p-0.5 rounded hover:bg-slate-100 flex items-center space-x-1 text-xs"
                  title="Add Repository"
                >
                  <PlusCircle className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-0.5">
                {repoList.length === 0 ? (
                  <div className="text-[11px] text-slate-400 italic px-2 py-1">No repositories indexed.</div>
                ) : (
                  repoList.map((r) => {
                    const repoId = r.repo_id;
                    const isActive = repoId === activeRepoId;
                    return (
                      <div key={repoId} className="group flex items-center justify-between">
                        <button
                          onClick={() => onSelectRepo(repoId)}
                          className={`flex-1 flex items-center space-x-2 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors truncate ${
                            isActive
                              ? "bg-slate-900 text-white shadow-xs"
                              : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                          }`}
                        >
                          <Github className="w-3.5 h-3.5 shrink-0 opacity-75" />
                          <span className="truncate font-mono">{repoId}</span>
                        </button>

                        <button
                          onClick={() => onOpenDeleteModal(repoId)}
                          className="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-all"
                          title={`Delete ${repoId}`}
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            <div className="h-px bg-slate-100 my-2" />

            {/* Navigation Tabs */}
            <div>
              <div className="px-2 mb-1.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Workspace View</span>
              </div>
              <nav className="space-y-0.5">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => onTabChange(item.id)}
                      className={`w-full flex items-center justify-between px-2.5 py-2 rounded-md text-xs font-medium transition-colors ${
                        isActive
                          ? "bg-indigo-50 text-indigo-700 border border-indigo-100"
                          : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                      }`}
                    >
                      <div className="flex items-center space-x-2.5">
                        <Icon className={`w-4 h-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                        <span>{item.label}</span>
                      </div>
                      {item.badge && (
                        <span className="px-1.5 py-0.5 text-[9px] font-bold bg-indigo-600 text-white rounded">
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Sidebar Footer info */}
          <div className="p-3 border-t border-slate-100 bg-slate-50/50 text-[11px] text-slate-400 space-y-1">
            <div className="flex items-center justify-between">
              <span>Embeddings</span>
              <span className="font-mono text-slate-600">bge-small-en-v1.5</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Vector Store</span>
              <span className="font-mono text-slate-600">ChromaDB</span>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#fcfcfc]">
          {children}
        </main>
      </div>
    </div>
  );
}
