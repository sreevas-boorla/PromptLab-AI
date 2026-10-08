export interface ModelSettings {
  model: string;
  temperature: number;
  top_p: number;
  max_tokens: number;
  system_prompt?: string;
}

export interface ExecutionMetrics {
  latency_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  is_mock?: boolean;
}

export interface PlaygroundResponse {
  output: string;
  metrics: ExecutionMetrics;
  substituted_prompt: string;
}

export interface OptimizerResult {
  prompt: string;
  output: string;
  metrics: ExecutionMetrics;
  eval_score: number;
}

export interface OptimizerResponse {
  original: OptimizerResult;
  optimized: OptimizerResult;
  strategy_applied: string;
  improvement_summary: string;
}

export interface ComparisonModelResult {
  model: string;
  output: string;
  metrics: ExecutionMetrics;
  status: string;
  error?: string;
}

export interface ComparisonResponse {
  results: ComparisonModelResult[];
  fastest_model: string;
  cheapest_model: string;
}

export interface PromptVersion {
  id: number;
  prompt_id: number;
  version_number: number;
  system_prompt: string;
  user_prompt: string;
  config_settings: Record<string, any>;
  notes?: string;
  created_at: string;
}

export interface PromptItem {
  id: number;
  title: string;
  description?: string;
  category: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  latest_version?: PromptVersion;
  versions_count: number;
}

export interface TestCase {
  id: number;
  suite_id: number;
  name: string;
  input_variables: Record<string, any>;
  expected_output?: string;
  evaluator_type: string;
  criteria: Record<string, any>;
  created_at: string;
}

export interface EvalSuite {
  id: number;
  name: string;
  description?: string;
  category: string;
  created_at: string;
  updated_at: string;
  test_cases_count: number;
}

export interface EvalResultItem {
  id: number;
  test_case_id: number;
  test_case_name: string;
  generated_output: string;
  latency_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_cost: number;
  score: number;
  passed: boolean;
  metrics_breakdown: Record<string, any>;
  error_message?: string;
}

export interface EvalRunResponse {
  id: number;
  suite_id: number;
  model: string;
  status: string;
  created_at: string;
  completed_at?: string;
  summary_metrics: Record<string, any>;
  results: EvalResultItem[];
}

export interface AnalyticsSummary {
  total_executions: number;
  total_tokens: number;
  total_cost: number;
  avg_latency_ms: number;
  pass_rate_percentage: number;
  cost_by_model: Record<string, number>;
  latency_by_model: Record<string, number>;
  executions_over_time: Array<{
    date: string;
    playground_calls: number;
    evaluations_run: number;
    cost_usd: number;
  }>;
}
