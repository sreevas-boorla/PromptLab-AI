import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="General")
    tags = Column(String(255), default="")  # Comma separated
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    versions = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")

class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    system_prompt = Column(Text, default="")
    user_prompt = Column(Text, nullable=False)
    model_config_json = Column(Text, default="{}")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    prompt = relationship("Prompt", back_populates="versions")

class EvalSuite(Base):
    __tablename__ = "eval_suites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="General")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    test_cases = relationship("TestCase", back_populates="suite", cascade="all, delete-orphan")
    runs = relationship("EvalRun", back_populates="suite", cascade="all, delete-orphan")

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("eval_suites.id"), nullable=False)
    name = Column(String(255), nullable=False)
    input_variables_json = Column(Text, default="{}")
    expected_output = Column(Text, nullable=True)
    evaluator_type = Column(String(50), default="semantic_similarity")  # exact_match, regex_match, semantic_similarity, json_schema, llm_judge
    criteria_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    suite = relationship("EvalSuite", back_populates="test_cases")

class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("eval_suites.id"), nullable=False)
    prompt_version_id = Column(Integer, ForeignKey("prompt_versions.id"), nullable=True)
    model = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    summary_metrics_json = Column(Text, default="{}")

    suite = relationship("EvalSuite", back_populates="runs")
    results = relationship("EvalResult", back_populates="run", cascade="all, delete-orphan")

class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("eval_runs.id"), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    generated_output = Column(Text, default="")
    latency_ms = Column(Float, default=0.0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    metrics_breakdown_json = Column(Text, default="{}")
    error_message = Column(Text, nullable=True)

    run = relationship("EvalRun", back_populates="results")

class AnalyticsLog(Base):
    __tablename__ = "analytics_logs"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, nullable=True)
    model = Column(String(100), nullable=False)
    latency_ms = Column(Float, default=0.0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    action_type = Column(String(50), default="playground")  # playground, optimizer, comparison, evaluation
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
