from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
import datetime

# Model Settings
class ModelSettings(BaseModel):
    model: str = Field(default="gpt-4o", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, ge=1)
    system_prompt: Optional[str] = Field(default="")

# Playground Schemas
class PlaygroundExecuteRequest(BaseModel):
    system_prompt: str = ""
    user_prompt: str
    input_variables: Dict[str, Any] = Field(default_factory=dict)
    settings: ModelSettings

class ExecutionMetrics(BaseModel):
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    is_mock: bool = False

class PlaygroundExecuteResponse(BaseModel):
    output: str
    metrics: ExecutionMetrics
    substituted_prompt: str

# Optimizer Schemas
class OptimizerRequest(BaseModel):
    original_prompt: str
    system_prompt: str = ""
    strategy: str = Field(default="chain_of_thought", description="chain_of_thought, few_shot, role_framing, compression, json_structuring")
    input_variables: Dict[str, Any] = Field(default_factory=dict)
    settings: ModelSettings

class OptimizerResult(BaseModel):
    prompt: str
    output: str
    metrics: ExecutionMetrics
    eval_score: float

class OptimizerResponse(BaseModel):
    original: OptimizerResult
    optimized: OptimizerResult
    strategy_applied: str
    improvement_summary: str

# Model Comparison Schemas
class ComparisonRequest(BaseModel):
    system_prompt: str = ""
    user_prompt: str
    input_variables: Dict[str, Any] = Field(default_factory=dict)
    models: List[str] = Field(default_factory=lambda: ["gpt-4o-mini", "gemini-2.5-flash", "llama-3.3-70b-versatile"])
    temperature: float = 0.7
    max_tokens: int = 1024

class ComparisonModelResult(BaseModel):
    model: str
    output: str
    metrics: ExecutionMetrics
    status: str = "success"
    error: Optional[str] = None

class ComparisonResponse(BaseModel):
    results: List[ComparisonModelResult]
    fastest_model: str
    cheapest_model: str

# Prompt Library Schemas
class PromptVersionCreate(BaseModel):
    system_prompt: str = ""
    user_prompt: str
    config_settings: Dict[str, Any] = Field(default_factory=dict, description="Model configuration settings")
    notes: Optional[str] = ""

class PromptVersionResponse(BaseModel):
    id: int
    prompt_id: int
    version_number: int
    system_prompt: str
    user_prompt: str
    config_settings: Dict[str, Any]
    notes: Optional[str]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class PromptCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    category: str = "General"
    tags: List[str] = Field(default_factory=list)
    initial_version: PromptVersionCreate

class PromptUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class PromptResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    tags: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    latest_version: Optional[PromptVersionResponse] = None
    versions_count: int = 0

    model_config = ConfigDict(from_attributes=True)

# Evaluation Schemas
class TestCaseCreate(BaseModel):
    name: str
    input_variables: Dict[str, Any] = Field(default_factory=dict)
    expected_output: Optional[str] = ""
    evaluator_type: str = Field(default="semantic_similarity", description="exact_match, regex_match, semantic_similarity, json_schema, llm_judge")
    criteria: Dict[str, Any] = Field(default_factory=dict)

class TestCaseResponse(BaseModel):
    id: int
    suite_id: int
    name: str
    input_variables: Dict[str, Any]
    expected_output: Optional[str]
    evaluator_type: str
    criteria: Dict[str, Any]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class EvalSuiteCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    category: str = "General"
    test_cases: List[TestCaseCreate] = Field(default_factory=list)

class EvalSuiteResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    test_cases_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class EvalRunRequest(BaseModel):
    suite_id: int
    prompt_version_id: Optional[int] = None
    system_prompt: Optional[str] = ""
    user_prompt: str
    model: str = "gpt-4o"

class EvalResultResponse(BaseModel):
    id: int
    test_case_id: int
    test_case_name: str
    generated_output: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_cost: float
    score: float
    passed: bool
    metrics_breakdown: Dict[str, Any]
    error_message: Optional[str] = None

class EvalRunResponse(BaseModel):
    id: int
    suite_id: int
    model: str
    status: str
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    summary_metrics: Dict[str, Any]
    results: List[EvalResultResponse] = Field(default_factory=list)

# Analytics Schemas
class AnalyticsSummaryResponse(BaseModel):
    total_executions: int
    total_tokens: int
    total_cost: float
    avg_latency_ms: float
    pass_rate_percentage: float
    cost_by_model: Dict[str, float]
    latency_by_model: Dict[str, float]
    executions_over_time: List[Dict[str, Any]]
