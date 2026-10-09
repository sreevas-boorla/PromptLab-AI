import React, { useState, useEffect } from 'react';
import { CheckCircle2, Play, AlertCircle, Plus, FileText, ChevronRight, BarChart } from 'lucide-react';
import { api } from '../services/api';
import { EvalSuite, EvalRunResponse, TestCase } from '../types';

export const Evaluations: React.FC = () => {
  const [suites, setSuites] = useState<EvalSuite[]>([]);
  const [selectedSuiteId, setSelectedSuiteId] = useState<number | null>(null);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  
  const [promptInput, setPromptInput] = useState('Process query for {{topic}} and provide structured explanation.');
  const [model, setModel] = useState('gemini-2.5-flash');

  const [loadingSuites, setLoadingSuites] = useState(true);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<EvalRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSuites();
  }, []);

  const loadSuites = async () => {
    try {
      const data = await api.listSuites();
      setSuites(data);
      if (data.length > 0) {
        setSelectedSuiteId(data[0].id);
        loadTestCases(data[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load evaluation suites');
    } finally {
      setLoadingSuites(false);
    }
  };

  const loadTestCases = async (suiteId: number) => {
    try {
      const cases = await api.listTestCases(suiteId);
      setTestCases(cases);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleSelectSuite = (id: number) => {
    setSelectedSuiteId(id);
    loadTestCases(id);
    setRunResult(null);
  };

  const handleRunEvaluation = async () => {
    if (!selectedSuiteId) return;
    setRunning(true);
    setError(null);
    try {
      const result = await api.runEvalSuite({
        suite_id: selectedSuiteId,
        system_prompt: 'You are an enterprise AI evaluator.',
        user_prompt: promptInput,
        model,
      });
      setRunResult(result);
    } catch (err: any) {
      setError(err.message || 'Evaluation run failed');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
          <CheckCircle2 className="w-6 h-6 mr-2 text-blue-500" />
          Evaluation Engine & Dataset Benchmark
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Execute automated test suites using <span className="text-blue-400 font-semibold">real evaluation algorithms</span> (Exact Match, Regex, Cosine Similarity, JSON Schema, LLM-as-a-Judge).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Test Suites List */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Evaluation Suites</h3>
            </div>

            {loadingSuites ? (
              <div className="text-xs text-slate-500 p-3">Loading suites...</div>
            ) : (
              <div className="space-y-2">
                {suites.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => handleSelectSuite(s.id)}
                    className={`w-full text-left p-3 rounded-xl border transition-all ${
                      selectedSuiteId === s.id
                        ? 'bg-blue-600/15 border-blue-500/40 text-white'
                        : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm">{s.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        {s.test_cases_count} cases
                      </span>
                    </div>
                    {s.description && <p className="text-xs text-slate-400 mt-1 line-clamp-1">{s.description}</p>}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Execution & Test Cases */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Target System Prompt / Template for Suite Execution
            </label>
            <textarea
              value={promptInput}
              onChange={(e) => setPromptInput(e.target.value)}
              rows={3}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 font-mono"
            />

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
              <div className="w-full sm:w-64">
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

              <button
                onClick={handleRunEvaluation}
                disabled={running || !selectedSuiteId}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/20 transition-all flex items-center justify-center"
              >
                {running ? 'Running Evaluation Suite...' : 'Run Test Suite'}
              </button>
            </div>
          </div>

          {/* Test Case Breakdown */}
          {testCases.length > 0 && !runResult && (
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Suite Test Cases ({testCases.length})
              </h3>
              <div className="space-y-2">
                {testCases.map((tc) => (
                  <div key={tc.id} className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="font-medium text-sm text-white">{tc.name}</span>
                      <div className="text-xs text-slate-400 mt-0.5">
                        Evaluator: <code className="text-blue-400">{tc.evaluator_type}</code>
                      </div>
                    </div>
                    {tc.expected_output && (
                      <span className="text-xs text-slate-500 max-w-xs truncate font-mono">
                        Target: {tc.expected_output}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Run Results */}
          {runResult && (
            <div className="space-y-6">
              {/* Summary Header */}
              <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div>
                  <span className="text-xs text-slate-400 block mb-1">Pass Rate</span>
                  <span className="text-2xl font-bold text-emerald-400">{runResult.summary_metrics.pass_rate_percentage}%</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block mb-1">Average Score</span>
                  <span className="text-2xl font-bold text-blue-400">{(runResult.summary_metrics.average_score * 100).toFixed(1)}%</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block mb-1">Passed / Total</span>
                  <span className="text-2xl font-bold text-white">
                    {runResult.summary_metrics.passed_cases} / {runResult.summary_metrics.total_test_cases}
                  </span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block mb-1">Total Cost</span>
                  <span className="text-2xl font-bold text-amber-400">${runResult.summary_metrics.total_cost_usd}</span>
                </div>
              </div>

              {/* Detailed Result Items */}
              <div className="space-y-3">
                {runResult.results.map((r, i) => (
                  <div key={i} className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center space-x-2">
                        {r.passed ? (
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                            PASSED
                          </span>
                        ) : (
                          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                            FAILED
                          </span>
                        )}
                        <span className="font-semibold text-sm text-white">{r.test_case_name}</span>
                      </div>
                      <span className="text-xs font-mono text-slate-400">Score: {(r.score * 100).toFixed(0)}%</span>
                    </div>

                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-200 font-mono whitespace-pre-wrap">
                      {r.generated_output}
                    </div>

                    <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-900 text-xs text-slate-400 font-mono">
                      Metrics breakdown: {JSON.stringify(r.metrics_breakdown)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
