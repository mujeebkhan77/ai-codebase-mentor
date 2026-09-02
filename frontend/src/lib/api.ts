import {
  RepoInfo,
  SearchResponse,
  SymbolResponse,
  RelationshipResponse,
  AskResponse,
  DeleteRepoResponse,
  FileContentResponse
} from "./types";

const API_BASE_URL = "/api";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const data = await res.json();
      if (data && data.detail) {
        errorDetail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // Ignore JSON parse failure on error body
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

export async function listRepositories(): Promise<RepoInfo[]> {
  const res = await fetch(`${API_BASE_URL}/repositories`, { cache: "no-store" });
  return handleResponse<RepoInfo[]>(res);
}

export async function getRepoInfo(repoId: string): Promise<RepoInfo> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}`, { cache: "no-store" });
  return handleResponse<RepoInfo>(res);
}

export async function deleteRepository(repoId: string): Promise<DeleteRepoResponse> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}`, {
    method: "DELETE"
  });
  return handleResponse<DeleteRepoResponse>(res);
}

export async function getRepoStructure(repoId: string): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}/structure`, { cache: "no-store" });
  const data = await handleResponse<{ repo_id: string; structure: string }>(res);
  return data.structure;
}

export async function getFileContent(repoId: string, path: string): Promise<FileContentResponse> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}/file?path=${encodeURIComponent(path)}`, { cache: "no-store" });
  return handleResponse<FileContentResponse>(res);
}

export async function searchCodebase(
  repoId: string,
  query: string,
  symbolName?: string,
  limit: number = 10,
  strategies?: string[]
): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, symbol_name: symbolName, limit, strategies })
  });
  return handleResponse<SearchResponse>(res);
}

export async function getSymbolInfo(repoId: string, name: string): Promise<SymbolResponse> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}/symbols/${encodeURIComponent(name)}`, { cache: "no-store" });
  return handleResponse<SymbolResponse>(res);
}

export async function getRelationships(repoId: string, symbolName: string, direction: string = "both"): Promise<RelationshipResponse> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}/relationships/${encodeURIComponent(symbolName)}?direction=${encodeURIComponent(direction)}`, { cache: "no-store" });
  return handleResponse<RelationshipResponse>(res);
}

export async function askMentor(repoId: string, question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE_URL}/repositories/${encodeURIComponent(repoId)}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  return handleResponse<AskResponse>(res);
}

export async function cloneRepository(repoUrl: string, repoName?: string): Promise<RepoInfo> {
  const res = await fetch(`${API_BASE_URL}/repositories`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl, repo_name: repoName })
  });
  return handleResponse<RepoInfo>(res);
}
