import React, { useState } from "react";
import { AlertTriangle, Trash2, Loader2, X } from "lucide-react";
import { deleteRepository } from "../../lib/api";

interface DeleteRepoModalProps {
  isOpen: boolean;
  repoId: string | null;
  onClose: () => void;
  onRepoDeleted: (deletedRepoId: string) => void;
}

export function DeleteRepoModal({ isOpen, repoId, onClose, onRepoDeleted }: DeleteRepoModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !repoId) return null;

  const handleDelete = async () => {
    setLoading(true);
    setError(null);
    try {
      await deleteRepository(repoId);
      onRepoDeleted(repoId);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to delete repository.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center space-x-2 text-red-600 font-bold text-sm">
            <AlertTriangle className="w-5 h-5" />
            <h2>Remove Repository</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1 rounded-md cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2 text-xs text-slate-600">
          <p>
            Are you sure you want to remove <strong className="text-slate-900 font-mono">{repoId}</strong> from AI Codebase Mentor?
          </p>
          <p className="bg-amber-50 border border-amber-200 text-amber-800 p-3 rounded-lg text-[11px]">
            This action will permanently delete the local repository clone and all associated Chroma vector and symbol indexes from disk.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-2.5 rounded-lg text-xs">
            {error}
          </div>
        )}

        <div className="flex items-center justify-end space-x-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 rounded-lg cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-xs font-medium flex items-center space-x-1.5 shadow-xs cursor-pointer"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
            <span>Remove Repository</span>
          </button>
        </div>
      </div>
    </div>
  );
}
