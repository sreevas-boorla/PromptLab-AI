import {
  ModelSettings,
  PlaygroundResponse,
  OptimizerResponse,
  ComparisonResponse,
  PromptItem,
  PromptVersion,
  EvalSuite,
  TestCase,
  EvalRunResponse,
  AnalyticsSummary
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || `HTTP Error ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Playground API
  executePlayground: (data: {
    system_prompt: string;
    user_prompt: string;
    input_variables: Record<string, any>;
    settings: ModelSettings;
  }) => fetchJson<PlaygroundResponse>(`${API_BASE}/playground/execute`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Optimizer API
  optimizePrompt: (data: {
    original_prompt: string;
    system_prompt: string;
    strategy: string;
    input_variables: Record<string, any>;
    settings: ModelSettings;
  }) => fetchJson<OptimizerResponse>(`${API_BASE}/optimizer/optimize`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Model Comparison API
  compareModels: (data: {
    system_prompt: string;
    user_prompt: string;
    input_variables: Record<string, any>;
    models: string[];
    temperature: number;
    max_tokens: number;
  }) => fetchJson<ComparisonResponse>(`${API_BASE}/comparison/compare`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Prompt Library API
  listPrompts: (params?: { category?: string; tag?: string; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.category) query.append('category', params.category);
    if (params?.tag) query.append('tag', params.tag);
    if (params?.search) query.append('search', params.search);
    return fetchJson<PromptItem[]>(`${API_BASE}/prompts?${query.toString()}`);
  },

  createPrompt: (data: {
    title: string;
    description: string;
    category: string;
    tags: string[];
    initial_version: {
      system_prompt: string;
      user_prompt: string;
      config_settings: Record<string, any>;
      notes: string;
    };
  }) => fetchJson<PromptItem>(`${API_BASE}/prompts`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  deletePrompt: (promptId: number) => fetchJson<{ status: string }>(`${API_BASE}/prompts/${promptId}`, {
    method: 'DELETE',
  }),

  listPromptVersions: (promptId: number) => fetchJson<PromptVersion[]>(`${API_BASE}/prompts/${promptId}/versions`),

  // Evaluation Suite API
  listSuites: () => fetchJson<EvalSuite[]>(`${API_BASE}/evaluations/suites`),

  createSuite: (data: {
    name: string;
    description: string;
    category: string;
    test_cases: Array<{
      name: string;
      input_variables: Record<string, any>;
      expected_output: string;
      evaluator_type: string;
      criteria: Record<string, any>;
    }>;
  }) => fetchJson<EvalSuite>(`${API_BASE}/evaluations/suites`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  listTestCases: (suiteId: number) => fetchJson<TestCase[]>(`${API_BASE}/evaluations/suites/${suiteId}/test-cases`),

  runEvalSuite: (data: {
    suite_id: number;
    system_prompt: string;
    user_prompt: string;
    model: string;
  }) => fetchJson<EvalRunResponse>(`${API_BASE}/evaluations/run`, {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Analytics API
  getAnalyticsSummary: () => fetchJson<AnalyticsSummary>(`${API_BASE}/analytics/summary`),
};
