import React, { useState } from 'react';
import { Layers, Play, Clock, DollarSign, Cpu, Zap, Trophy, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { ComparisonResponse } from '../types';

export const Comparison: React.FC = () => {
  const [prompt, setPrompt] = useState('Compare Relational SQL vs NoSQL document databases for high-throughput transactional applications.');
  const [selectedModels, setSelectedModels] = useState<string[]>(['gpt-4o-mini', 'gemini-2.5-flash', 'llama-3.3-70b-versatile']);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const availableModels = [
    { id: 'gpt-4o', label: 'OpenAI GPT-4o' },
    { id: 'gpt-4o-mini', label: 'OpenAI GPT-4o-mini' },
    { id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash' },
    { id: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro' },
    { id: 'llama-3.3-70b-versatile', label: 'Llama 3.3 70B (Groq)' },
    { id: 'llama-3.1-8b-instant', label: 'Llama 3.1 8B (Groq)' },
  ];

  const toggleModel = (id: string) => {
    if (selectedModels.includes(id)) {
      if (selectedModels.length > 1) setSelectedModels(selectedModels.filter(m => m !== id));
    } else {
      setSelectedModels([...selectedModels, id]);
    }
  };

  const handleCompare = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.compareModels({
        system_prompt: 'You are an enterprise software architect.',
        user_prompt: prompt,
        input_variables: {},
        models: selectedModels,
        temperature: 0.7,
        max_tokens: 1024,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
          <Layers className="w-6 h-6 mr-2 text-blue-500" />
          Multi-Model Side-by-Side Comparison
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Execute identical prompts simultaneously across LLM provider models to evaluate latency, cost, and output quality.
        </p>
      </div>

      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
        <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Prompt for Multi-Model Benchmark
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={3}
          className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
        />

        <div className="space-y-2">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
            Select Models to Compare ({selectedModels.length} Selected)
          </label>
          <div className="flex flex-wrap gap-2">
            {availableModels.map((m) => {
              const active = selectedModels.includes(m.id);
              return (
                <button
                  key={m.id}
                  onClick={() => toggleModel(m.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${
                    active
                      ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  {m.label}
                </button>
              );
            })}
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={loading || !prompt.trim()}
          className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/20 flex items-center justify-center text-sm transition-all"
        >
          {loading ? 'Running Multi-Model Benchmark...' : 'Run Side-by-Side Model Comparison'}
        </button>
      </div>

      {result && (
        <div className="space-y-6">
          {/* Winner Badges */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 flex items-center space-x-3">
              <Trophy className="w-6 h-6 text-emerald-400 shrink-0" />
              <div>
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block">Fastest Execution</span>
                <span className="text-sm font-bold text-white">{result.fastest_model}</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800/60 flex items-center space-x-3">
              <DollarSign className="w-6 h-6 text-amber-400 shrink-0" />
              <div>
                <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider block">Lowest Cost</span>
                <span className="text-sm font-bold text-white">{result.cheapest_model}</span>
              </div>
            </div>
          </div>

          {/* Grid of Results */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {result.results.map((res) => (
              <div key={res.model} className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <span className="text-sm font-bold text-white uppercase font-mono">{res.model}</span>
                  <div className="flex items-center space-x-2 text-xs">
                    <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300 font-mono">
                      {res.metrics.latency_ms} ms
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-amber-400 font-mono">
                      ${res.metrics.estimated_cost.toFixed(6)}
                    </span>
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-200 font-mono whitespace-pre-wrap max-h-72 overflow-y-auto leading-relaxed">
                  {res.output}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
                  <span>Tokens: {res.metrics.total_tokens}</span>
                  {res.metrics.is_mock && <span className="text-amber-400 font-medium">Mock Mode</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
