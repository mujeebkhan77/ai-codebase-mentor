import React, { useState, useEffect, useCallback } from "react";
import { AppShell } from "./components/layout/AppShell";
import { OverviewDashboard } from "./components/overview/OverviewDashboard";
import { CodeExplorer } from "./components/explorer/CodeExplorer";
import { AskMentor } from "./components/mentor/AskMentor";
import { SearchExperience } from "./components/search/SearchExperience";
import { SymbolExplorer } from "./components/symbols/SymbolExplorer";
import { RelationshipGraph } from "./components/graph/RelationshipGraph";
import { AddRepoModal } from "./components/modals/AddRepoModal";
import { DeleteRepoModal } from "./components/modals/DeleteRepoModal";
import { listRepositories, getRepoInfo, getRepoStructure } from "./lib/api";
import { RepoInfo } from "./lib/types";

export function App() {
  const [currentTab, setCurrentTab] = useState<string>("overview");
  const [activeRepoId, setActiveRepoId] = useState<string>("");
  const [repoList, setRepoList] = useState<RepoInfo[]>([]);
  const [activeRepoInfo, setActiveRepoInfo] = useState<RepoInfo | null>(null);
  const [activeRepoStructure, setActiveRepoStructure] = useState<string>("");
  
  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteTargetRepoId, setDeleteTargetRepoId] = useState<string | null>(null);

  // Jump to code state
  const [selectedExplorerFile, setSelectedExplorerFile] = useState<string>("");
  const [selectedLineRange, setSelectedLineRange] = useState<{ start: number; end: number } | undefined>(undefined);

  // Fetch repositories list from backend
  const fetchReposList = useCallback(async () => {
    try {
      const repos = await listRepositories();
      setRepoList(repos);
      if (repos.length > 0) {
        if (!activeRepoId || !repos.some((r) => r.repo_id === activeRepoId)) {
          setActiveRepoId(repos[0].repo_id);
        }
      } else {
        setActiveRepoId("");
        setActiveRepoInfo(null);
        setActiveRepoStructure("");
      }
    } catch (err) {
      console.error("Failed to list repositories from backend API:", err);
    }
  }, [activeRepoId]);

  useEffect(() => {
    fetchReposList();
  }, [fetchReposList]);

  // Load active repository info & file structure
  useEffect(() => {
    async function loadActiveRepo() {
      if (!activeRepoId) {
        setActiveRepoInfo(null);
        setActiveRepoStructure("");
        return;
      }
      try {
        const info = await getRepoInfo(activeRepoId);
        setActiveRepoInfo(info);
        const struct = await getRepoStructure(activeRepoId);
        setActiveRepoStructure(struct);
      } catch (err) {
        console.error(`Failed to load repository info for '${activeRepoId}':`, err);
      }
    }
    loadActiveRepo();
  }, [activeRepoId]);

  const handleNavigateToCode = (filePath: string, startLine: number, endLine: number) => {
    setSelectedExplorerFile(filePath);
    setSelectedLineRange({ start: startLine, end: endLine });
    setCurrentTab("explorer");
  };

  const handleRepoAdded = (newRepoId: string) => {
    fetchReposList();
    setActiveRepoId(newRepoId);
  };

  const handleRepoDeleted = (deletedRepoId: string) => {
    fetchReposList();
  };

  return (
    <AppShell
      currentTab={currentTab}
      onTabChange={setCurrentTab}
      activeRepoId={activeRepoId}
      repoList={repoList}
      onSelectRepo={setActiveRepoId}
      onOpenAddModal={() => setIsAddModalOpen(true)}
      onOpenDeleteModal={(rId) => setDeleteTargetRepoId(rId)}
    >
      {currentTab === "overview" && (
        <OverviewDashboard repoInfo={activeRepoInfo} onNavigate={setCurrentTab} />
      )}

      {currentTab === "explorer" && (
        <CodeExplorer
          repoId={activeRepoId}
          structureStr={activeRepoStructure}
          initialSelectedFile={selectedExplorerFile}
          initialLineRange={selectedLineRange}
        />
      )}

      {currentTab === "ask" && (
        <AskMentor repoId={activeRepoId} onNavigateToCode={handleNavigateToCode} />
      )}

      {currentTab === "search" && (
        <SearchExperience repoId={activeRepoId} onNavigateToCode={handleNavigateToCode} />
      )}

      {currentTab === "symbols" && (
        <SymbolExplorer repoId={activeRepoId} onNavigateToCode={handleNavigateToCode} />
      )}

      {currentTab === "relationships" && (
        <RelationshipGraph repoId={activeRepoId} onNavigateToCode={handleNavigateToCode} />
      )}

      {/* Modals */}
      <AddRepoModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onRepoAdded={handleRepoAdded}
      />

      <DeleteRepoModal
        isOpen={deleteTargetRepoId !== null}
        repoId={deleteTargetRepoId}
        onClose={() => setDeleteTargetRepoId(null)}
        onRepoDeleted={handleRepoDeleted}
      />
    </AppShell>
  );
}

export default App;
