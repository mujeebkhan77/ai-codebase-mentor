import React, { useState } from "react";
import { PlusCircle, Loader2, X, Github } from "lucide-react";
import { cloneRepository } from "../../lib/api";

interface AddRepoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRepoAdded: (repoId: string) => void;
}

export function AddRepoModal({ isOpen, onClose, onRepoAdded }: AddRepoModalProps) {
  const [repoUrl, setRepoUrl] = useState("");
  const [repoName, setRepoName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await cloneRepository(repoUrl.trim(), repoName.trim() || undefined);
      onRepoAdded(res.repo_id);
      onClose();
      setRepoUrl("");
      setRepoName("");
    } catch (err: any) {
      setError(err.message || "Failed to clone and index repository.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm">
            <Github className="w-5 h-5 text-indigo-600" />
            <h2>Add GitHub Repository</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1 rounded-md cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">GitHub Repository URL *</label>
            <input
              type="text"
              required
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/owner/repo.git"
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Optional Custom Name</label>
            <input
              type="text"
              value={repoName}
              onChange={(e) => setRepoName(e.target.value)}
              placeholder="e.g. my-project"
              className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-2.5 rounded-lg text-xs">
              {error}
            </div>
          )}

          <div className="flex items-center justify-end space-x-2 pt-3">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 rounded-lg cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !repoUrl.trim()}
              className="bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-xs font-medium flex items-center space-x-1.5 shadow-xs cursor-pointer"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <PlusCircle className="w-3.5 h-3.5" />}
              <span>{loading ? "Cloning & Indexing..." : "Clone & Index"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
