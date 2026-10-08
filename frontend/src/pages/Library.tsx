import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Search, Tag, GitCommit, Trash2, Edit3, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { PromptItem, PromptVersion } from '../types';

export const Library: React.FC = () => {
  const [prompts, setPrompts] = useState<PromptItem[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<PromptItem | null>(null);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New Prompt Form
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('General');
  const [newTags, setNewTags] = useState('prod,template');
  const [newSysPrompt, setNewSysPrompt] = useState('You are an expert AI assistant.');
  const [newUserPrompt, setNewUserPrompt] = useState('Hello {{name}}, how can I help with {{topic}}?');

  useEffect(() => {
    loadPrompts();
  }, [search]);

  const loadPrompts = async () => {
    try {
      const data = await api.listPrompts({ search });
      setPrompts(data);
      if (data.length > 0 && !selectedPrompt) {
        handleSelectPrompt(data[0]);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPrompt = async (prompt: PromptItem) => {
    setSelectedPrompt(prompt);
    try {
      const vList = await api.listPromptVersions(prompt.id);
      setVersions(vList);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleCreatePrompt = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createPrompt({
        title: newTitle,
        description: 'User created prompt template',
        category: newCategory,
        tags: newTags.split(',').map((t) => t.trim()),
        initial_version: {
          system_prompt: newSysPrompt,
          user_prompt: newUserPrompt,
          config_settings: { model: 'gpt-4o' },
          notes: 'v1 initial prompt',
        },
      });
      setShowCreateModal(false);
      setNewTitle('');
      loadPrompts();
    } catch (err: any) {
      alert(err.message || 'Failed to create prompt');
    }
  };

  const handleDeletePrompt = async (id: number) => {
    if (!confirm('Are you sure you want to delete this prompt?')) return;
    try {
      await api.deletePrompt(id);
      setSelectedPrompt(null);
      loadPrompts();
    } catch (err: any) {
      alert(err.message || 'Failed to delete');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
            <BookOpen className="w-6 h-6 mr-2 text-blue-500" />
            Prompt Version Control Library
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Store, audit, tag, and track prompt revision history across team projects.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/20 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4 mr-2" /> New Prompt
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Prompts List & Search */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search prompts by title or category..."
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="space-y-2">
            {prompts.map((p) => {
              const active = selectedPrompt?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => handleSelectPrompt(p)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                    active
                      ? 'bg-blue-600/15 border-blue-500/40 text-white'
                      : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-sm">{p.title}</h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-blue-400">
                      v{p.versions_count}
                    </span>
                  </div>
                  {p.description && <p className="text-xs text-slate-400 mt-1 line-clamp-1">{p.description}</p>}
                  
                  <div className="flex items-center space-x-2 mt-2">
                    {p.tags.map((t, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                        #{t}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Prompt Inspector & Version History */}
        <div className="lg:col-span-7 space-y-6">
          {selectedPrompt ? (
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h2 className="text-xl font-bold text-white">{selectedPrompt.title}</h2>
                  <p className="text-xs text-slate-400 mt-1">{selectedPrompt.description}</p>
                </div>
                <button
                  onClick={() => handleDeletePrompt(selectedPrompt.id)}
                  className="p-2 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-slate-800"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>

              {/* Version History List */}
              <div className="space-y-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center">
                  <GitCommit className="w-4 h-4 mr-1.5 text-blue-400" /> Revision History ({versions.length})
                </h3>

                <div className="space-y-3">
                  {versions.map((ver) => (
                    <div key={ver.id} className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-blue-400 font-mono">Version {ver.version_number}</span>
                        <span className="text-slate-500">{new Date(ver.created_at).toLocaleDateString()}</span>
                      </div>

                      {ver.system_prompt && (
                        <div className="text-xs text-slate-400">
                          <span className="font-semibold text-slate-500">System Directive:</span> {ver.system_prompt}
                        </div>
                      )}

                      <div className="bg-slate-900 p-3 rounded-lg text-xs text-slate-200 font-mono whitespace-pre-wrap border border-slate-800">
                        {ver.user_prompt}
                      </div>

                      {ver.notes && <div className="text-[11px] text-slate-500 italic">Notes: {ver.notes}</div>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-8 text-center text-slate-500 text-sm">
              Select a prompt from the left list to view version history.
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 max-w-lg w-full p-6 space-y-4">
            <h3 className="text-lg font-bold text-white">Create New Prompt Template</h3>
            <form onSubmit={handleCreatePrompt} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Category</label>
                <input
                  type="text"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">User Prompt Template</label>
                <textarea
                  value={newUserPrompt}
                  onChange={(e) => setNewUserPrompt(e.target.value)}
                  rows={4}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 font-mono"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg"
                >
                  Save Prompt
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
