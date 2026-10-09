import React, { useState } from 'react';
import { Zap, Sparkles, ArrowRight, CheckCircle2, Clock, Cpu, DollarSign, Sliders } from 'lucide-react';
import { api } from '../services/api';
import { OptimizerResponse } from '../types';

export const Optimizer: React.FC = () => {
  const [originalPrompt, setOriginalPrompt] = useState('Write a python function that calculates prime factors of an integer.');
  const [strategy, setStrategy] = useState('chain_of_thought');
  const [model, setModel] = useState('gemini-2.5-flash');
  const [temperature, setTemperature] = useState(0.7);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OptimizerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.optimizePrompt({
        original_prompt: originalPrompt,
        system_prompt: 'You are a principal software engineer.',
        strategy,
        input_variables: {},
        settings: {
          model,
          temperature,
          top_p: 1.0,
          max_tokens: 1024,
        },
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
          <Zap className="w-6 h-6 mr-2 text-blue-500" />
          Prompt Optimizer & Comparative Benchmark
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Apply automated prompt engineering strategies and test Original vs. Optimized prompts side-by-side under <span className="text-blue-400 font-semibold">identical input variables and model settings</span>.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Inputs */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Original Draft Prompt
            </label>
            <textarea
              value={originalPrompt}
              onChange={(e) => setOriginalPrompt(e.target.value)}
              rows={4}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
              placeholder="Enter original prompt text to optimize..."
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Optimization Strategy</label>
                <select
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="chain_of_thought">Chain-of-Thought (Step-by-step reasoning)</option>
                  <option value="few_shot">Few-Shot Exemplar Framing</option>
                  <option value="role_framing">Principal Role & Directive Framing</option>
                  <option value="compression">Token Compression (Remove fluff)</option>
                  <option value="json_structuring">JSON Schema Output Restriction</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Test Model</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                >
                  <option value="gpt-4o">OpenAI GPT-4o</option>
                  <option value="gpt-4o-mini">OpenAI GPT-4o mini</option>
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                  <option value="llama-3.3-70b-versatile">Groq Llama 3.3 70B</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleOptimize}
              disabled={loading || !originalPrompt.trim()}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/20 flex items-center justify-center text-sm transition-all"
            >
              {loading ? (
                <span>Transforming & Running Comparative Execution...</span>
              ) : (
                <span className="flex items-center">
                  <Sparkles className="w-4 h-4 mr-2" /> Optimize & Execute Side-by-Side Test
                </span>
              )}
            </button>
          </div>

          {/* Results Side by Side */}
          {result && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-blue-950/40 border border-blue-800/60 text-blue-200 text-sm flex items-center justify-between">
                <span className="font-semibold">{result.strategy_applied}</span>
                <span className="text-xs bg-blue-500/20 px-3 py-1 rounded-full text-blue-300 border border-blue-400/30">
                  {result.improvement_summary}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Original Result */}
                <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Original Prompt</span>
                    <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300">
                      Score: {(result.original.eval_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] text-slate-500 uppercase font-bold">Prompt Text:</span>
                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-300 font-mono">
                      {result.original.prompt}
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] text-slate-500 uppercase font-bold">Generated Output:</span>
                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-200 font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">
                      {result.original.output}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center text-xs pt-2">
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800 text-slate-400">
                      {result.original.metrics.latency_ms} ms
                    </div>
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800 text-slate-400">
                      {result.original.metrics.total_tokens} tokens
                    </div>
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800 text-slate-400">
                      ${result.original.metrics.estimated_cost.toFixed(6)}
                    </div>
                  </div>
                </div>

                {/* Optimized Result */}
                <div className="bg-slate-900 rounded-2xl border border-blue-900/60 p-5 space-y-4 shadow-xl shadow-blue-500/5">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center">
                      <Sparkles className="w-3.5 h-3.5 mr-1" /> Optimized Prompt
                    </span>
                    <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      Score: {(result.optimized.eval_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] text-blue-400/80 uppercase font-bold">Transformed Prompt:</span>
                    <div className="bg-slate-950 p-3 rounded-xl border border-blue-900/40 text-xs text-blue-200 font-mono max-h-32 overflow-y-auto">
                      {result.optimized.prompt}
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-[11px] text-blue-400/80 uppercase font-bold">Generated Output:</span>
                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-200 font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">
                      {result.optimized.output}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center text-xs pt-2">
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800 text-slate-400">
                      {result.optimized.metrics.latency_ms} ms
                    </div>
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800 text-slate-400">
                      {result.optimized.metrics.total_tokens} tokens
                    </div>
                    <div className="bg-slate-950 p-2 rounded-lg border border-slate-800 text-slate-400">
                      ${result.optimized.metrics.estimated_cost.toFixed(6)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Strategy Explanations Sidebar */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Strategy Playbook</h3>

            <div className="space-y-3 text-xs text-slate-400">
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <span className="font-semibold text-blue-400 block mb-1">Chain-of-Thought</span>
                Forces multi-step explicit reasoning decomposition before providing the final answer.
              </div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <span className="font-semibold text-purple-400 block mb-1">Few-Shot Framing</span>
                Injects input-output exemplars establishing strict output structure patterns.
              </div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <span className="font-semibold text-emerald-400 block mb-1">Role & Persona Directive</span>
                Assigns authoritative domain expert persona constraints.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
