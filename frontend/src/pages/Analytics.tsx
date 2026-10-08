import React, { useState, useEffect } from 'react';
import { BarChart3, Clock, DollarSign, Cpu, CheckCircle2, TrendingUp } from 'lucide-react';
import { api } from '../services/api';
import { AnalyticsSummary } from '../types';

export const Analytics: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await api.getAnalyticsSummary();
      setSummary(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !summary) {
    return <div className="text-slate-500 text-sm p-6">Loading analytics telemetry...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
          <BarChart3 className="w-6 h-6 mr-2 text-blue-500" />
          Analytics & Usage Telemetry
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Monitor token consumption, total API expenditure, latency profiles, and evaluation pass rates.
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Executions</span>
            <TrendingUp className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{summary.total_executions}</div>
        </div>

        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Tokens Processed</span>
            <Cpu className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">{summary.total_tokens.toLocaleString()}</div>
        </div>

        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Expenditure ($)</span>
            <DollarSign className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">${summary.total_cost.toFixed(4)}</div>
        </div>

        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Eval Suite Pass Rate</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{summary.pass_rate_percentage}%</div>
        </div>
      </div>

      {/* Model Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Cost by Model ($)</h3>
          <div className="space-y-3">
            {Object.entries(summary.cost_by_model).map(([model, cost]) => (
              <div key={model} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-mono text-slate-300">{model}</span>
                  <span className="font-mono text-amber-400">${cost.toFixed(6)}</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div className="bg-amber-500 h-full rounded-full" style={{ width: `${Math.min(100, (cost / (summary.total_cost || 1)) * 100)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Average Latency by Model (ms)</h3>
          <div className="space-y-3">
            {Object.entries(summary.latency_by_model).map(([model, latency]) => (
              <div key={model} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-mono text-slate-300">{model}</span>
                  <span className="font-mono text-blue-400">{latency} ms</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div className="bg-blue-500 h-full rounded-full" style={{ width: `${Math.min(100, (latency / 300) * 100)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Timeline Table */}
      <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
        <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Execution Activity Timeline</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Playground Runs</th>
                <th className="py-2.5 px-3">Evaluations Executed</th>
                <th className="py-2.5 px-3">Daily Cost ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {summary.executions_over_time.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-950/50">
                  <td className="py-2.5 px-3 font-mono text-white">{row.date}</td>
                  <td className="py-2.5 px-3">{row.playground_calls}</td>
                  <td className="py-2.5 px-3">{row.evaluations_run}</td>
                  <td className="py-2.5 px-3 font-mono text-amber-400">${row.cost_usd.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
