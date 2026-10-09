import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_playground_execution_api():
    payload = {
        "system_prompt": "You are a helpful assistant.",
        "user_prompt": "Hello {{name}}, welcome to {{service}}.",
        "input_variables": {"name": "Alice", "service": "PromptLab AI"},
        "settings": {
            "model": "mock-llm",
            "temperature": 0.7,
            "max_tokens": 256
        }
    }
    res = client.post("/api/v1/playground/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "output" in data
    assert "metrics" in data
    assert data["metrics"]["latency_ms"] > 0
    assert data["metrics"]["is_mock"] is True
    assert "Alice" in data["substituted_prompt"]

def test_missing_api_key_validation():
    """Verify Phase 2 requirement: Missing credentials throw explicit error when real model selected."""
    old_key = os.environ.pop("OPENAI_API_KEY", None)
    try:
        payload = {
            "system_prompt": "",
            "user_prompt": "Test query",
            "input_variables": {},
            "settings": {"model": "gpt-4o", "temperature": 0.7, "max_tokens": 100}
        }
        res = client.post("/api/v1/playground/execute", json=payload)
        assert res.status_code == 400
        assert "Missing API key OPENAI_API_KEY" in res.json()["detail"]
    finally:
        if old_key:
            os.environ["OPENAI_API_KEY"] = old_key

def test_mock_optimizer_requires_real_judge():
    payload = {
        "original_prompt": "Write a Python function.",
        "strategy": "chain_of_thought",
        "input_variables": {},
        "settings": {"model": "mock-llm", "temperature": 0.5, "max_tokens": 512}
    }
    res = client.post("/api/v1/optimizer/optimize", json=payload)
    assert res.status_code != 200
    assert "evaluation" in res.json().get("detail", "").lower() or "judge" in res.json().get("detail", "").lower()

def test_model_comparison_api():
    payload = {
        "user_prompt": "Explain quantum entanglement in simple terms.",
        "input_variables": {},
        "models": ["mock-llm", "mock-llm"]
    }
    res = client.post("/api/v1/comparison/compare", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 2
    assert data["fastest_model"] != ""
    assert data["cheapest_model"] != ""

def test_prompts_crud_api():
    create_payload = {
        "title": "API Test Prompt",
        "description": "Created during automated testing",
        "category": "Testing",
        "tags": ["test", "api"],
        "initial_version": {
            "system_prompt": "Test sys",
            "user_prompt": "Test user {{var}}",
            "config_settings": {"model": "mock-llm"},
            "notes": "v1"
        }
    }
    res_create = client.post("/api/v1/prompts", json=create_payload)
    assert res_create.status_code == 200
    prompt_data = res_create.json()
    prompt_id = prompt_data["id"]

    res_list = client.get("/api/v1/prompts")
    assert res_list.status_code == 200
    assert any(p["id"] == prompt_id for p in res_list.json())

    res_get = client.get(f"/api/v1/prompts/{prompt_id}")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "API Test Prompt"

def test_analytics_api():
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_executions" in data
    assert "total_tokens" in data
    assert "total_cost" in data
