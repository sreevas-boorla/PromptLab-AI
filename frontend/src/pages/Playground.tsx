import React, { useState } from 'react';
import { Play, Sparkles, Sliders, Clock, DollarSign, Cpu, AlertTriangle, Plus, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import { PlaygroundResponse } from '../types';

export const Playground: React.FC = () => {
  const [systemPrompt, setSystemPrompt] = useState('You are an expert AI assistant providing concise, accurate answers.');
  const [userPrompt, setUserPrompt] = useState('Draft a customer support email to {{customer_name}} regarding their order #{{order_id}} for {{product_name}}.');
  const [model, setModel] = useState('gpt-4o');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(512);
  
  const [variables, setVariables] = useState<Array<{ key: string; value: string }>>([
    { key: 'customer_name', value: 'Sarah Jenkins' },
    { key: 'order_id', value: 'ORD-98421' },
    { key: 'product_name', value: 'PromptLab Pro License' },
  ]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PlaygroundResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAddVariable = () => {
    setVariables([...variables, { key: `var_${variables.length + 1}`, value: '' }]);
  };

  const handleRemoveVariable = (index: number) => {
    setVariables(variables.filter((_, i) => i !== index));
  };

  const handleVariableChange = (index: number, field: 'key' | 'value', val: string) => {
    const updated = [...variables];
    updated[index][field] = val;
    setVariables(updated);
  };

  const handleExecute = async () => {
    setLoading(true);
    setError(null);

    const varsObj: Record<string, string> = {};
    variables.forEach((v) => {
      if (v.key.trim()) varsObj[v.key.trim()] = v.value;
    });

    try {
      const data = await api.executePlayground({
        system_prompt: systemPrompt,
        user_prompt: userPrompt,
        input_variables: varsObj,
        settings: {
          model,
          temperature,
          top_p: 1.0,
          max_tokens: maxTokens,
        },
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center">
            <Sparkles className="w-6 h-6 mr-2 text-blue-500" />
            Prompt Playground
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Test, format, and execute prompts interactively with live parameter substitution and metric telemetry.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex items-center space-x-3">
          <button
            onClick={handleExecute}
            disabled={loading || !userPrompt.trim()}
            className="flex items-center px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-sm rounded-xl shadow-lg shadow-blue-500/20 transition-all cursor-pointer"
            aria-label="Execute prompt"
          >
            {loading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Executing...
              </span>
            ) : (
              <span className="flex items-center">
                <Play className="w-4 h-4 mr-2 fill-current" />
                Run Prompt
              </span>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-sm flex items-center">
          <AlertTriangle className="w-5 h-5 mr-3 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Prompts & Parameters */}
        <div className="lg:col-span-8 space-y-6">
          {/* System Prompt */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
              System Prompt (Optional Persona & Directives)
            </label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              rows={2}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors font-mono"
              placeholder="e.g. You are a senior software architect..."
            />
          </div>

          {/* User Prompt */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
              User Prompt Template (Supports <code className="text-blue-400 font-normal">{"{{variable_name}}"}</code>)
            </label>
            <textarea
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              rows={6}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors font-mono"
              placeholder="Write your prompt template here..."
            />
          </div>

          {/* Input Variables */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Template Variables
              </label>
              <button
                onClick={handleAddVariable}
                className="text-xs text-blue-400 hover:text-blue-300 flex items-center font-medium"
              >
                <Plus className="w-3.5 h-3.5 mr-1" /> Add Variable
              </button>
            </div>
            {variables.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No variables added. Use {"{{var}}"} syntax in your prompt.</p>
            ) : (
              <div className="space-y-2">
                {variables.map((v, i) => (
                  <div key={i} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={v.key}
                      onChange={(e) => handleVariableChange(i, 'key', e.target.value)}
                      placeholder="Variable key"
                      className="w-1/3 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-blue-400 font-mono focus:outline-none focus:border-blue-500"
                    />
                    <input
                      type="text"
                      value={v.value}
                      onChange={(e) => handleVariableChange(i, 'value', e.target.value)}
                      placeholder="Variable test value"
                      className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                    />
                    <button
                      onClick={() => handleRemoveVariable(i)}
                      className="p-1 text-slate-500 hover:text-rose-400 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Output Display */}
          {result && (
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Generated LLM Output
                </span>
                {result.metrics.is_mock && (
                  <span className="text-xs px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400 font-medium flex items-center">
                    <AlertTriangle className="w-3.5 h-3.5 mr-1" /> Mock Mode (Real API keys unconfigured)
                  </span>
                )}
              </div>

              <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 text-sm text-slate-200 font-mono whitespace-pre-wrap leading-relaxed">
                {result.output}
              </div>

              {/* Substituted Prompt Preview */}
              <div className="space-y-1">
                <span className="text-xs text-slate-500 font-medium">Substituted Prompt Payload:</span>
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-900 text-xs text-slate-400 font-mono">
                  {result.substituted_prompt}
                </div>
              </div>

              {/* Telemetry Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                  <div className="flex items-center text-xs text-slate-400 mb-1">
                    <Clock className="w-3.5 h-3.5 mr-1.5 text-blue-400" /> Latency
                  </div>
                  <div className="text-base font-bold text-white">{result.metrics.latency_ms} ms</div>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                  <div className="flex items-center text-xs text-slate-400 mb-1">
                    <Cpu className="w-3.5 h-3.5 mr-1.5 text-purple-400" /> Prompt Tokens
                  </div>
                  <div className="text-base font-bold text-white">{result.metrics.prompt_tokens}</div>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                  <div className="flex items-center text-xs text-slate-400 mb-1">
                    <Cpu className="w-3.5 h-3.5 mr-1.5 text-emerald-400" /> Completion Tokens
                  </div>
                  <div className="text-base font-bold text-white">{result.metrics.completion_tokens}</div>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                  <div className="flex items-center text-xs text-slate-400 mb-1">
                    <DollarSign className="w-3.5 h-3.5 mr-1.5 text-amber-400" /> Est. Cost
                  </div>
                  <div className="text-base font-bold text-white">${result.metrics.estimated_cost.toFixed(6)}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Model Config Sidebar */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 space-y-5">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center border-b border-slate-800 pb-3">
              <Sliders className="w-4 h-4 mr-2 text-blue-400" /> Model Hyperparameters
            </h3>

            {/* Model Selection */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-300">Target Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="gpt-4o">OpenAI GPT-4o</option>
                <option value="gpt-4o-mini">OpenAI GPT-4o-mini</option>
                <option value="claude-3-5-sonnet">Anthropic Claude 3.5 Sonnet</option>
                <option value="gemini-1.5-pro">Google Gemini 1.5 Pro</option>
                <option value="llama-3-70b">Meta Llama 3 70B</option>
              </select>
            </div>

            {/* Temperature Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">Temperature</span>
                <span className="text-blue-400 font-mono">{temperature}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="2.0"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>0.0 (Deterministic)</span>
                <span>2.0 (Creative)</span>
              </div>
            </div>

            {/* Max Tokens */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">Max Tokens</span>
                <span className="text-blue-400 font-mono">{maxTokens}</span>
              </div>
              <input
                type="range"
                min="64"
                max="4096"
                step="64"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                className="w-full accent-blue-500 cursor-pointer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
