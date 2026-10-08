import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.evaluators import EvaluationEngine

def test_exact_match_evaluator():
    score, passed, metrics = EvaluationEngine.evaluate_exact_match("Hello World", "hello world ", ignore_case=True, strip_whitespace=True)
    assert score == 1.0
    assert passed is True
    assert metrics["evaluator"] == "exact_match"

    score_fail, passed_fail, _ = EvaluationEngine.evaluate_exact_match("Hello World", "Goodbye World", ignore_case=True)
    assert score_fail == 0.0
    assert passed_fail is False

def test_regex_match_evaluator():
    pattern = r"Status:\s*(SUCCESS|OK)"
    score, passed, metrics = EvaluationEngine.evaluate_regex("Server Response\nStatus: SUCCESS", pattern)
    assert score == 1.0
    assert passed is True
    assert metrics["matched"] is True

    score_fail, passed_fail, _ = EvaluationEngine.evaluate_regex("Server Response\nStatus: FAILED", pattern)
    assert score_fail == 0.0
    assert passed_fail is False

def test_semantic_similarity_evaluator():
    text1 = "Quantum computing uses qubits to perform rapid calculations."
    text2 = "Quantum computers leverage qubits for fast computation."
    score, passed, metrics = EvaluationEngine.evaluate_semantic_similarity(text1, text2)
    assert score > 0.5
    assert "char_3gram_cosine" in metrics
    assert "sequence_matcher_ratio" in metrics

def test_json_schema_evaluator():
    json_text = '{"status": "ok", "count": 42}'
    score, passed, metrics = EvaluationEngine.evaluate_json_schema(json_text, required_keys=["status", "count"])
    assert score == 1.0
    assert passed is True

    json_invalid = '{"status": "ok"}'
    score_missing, passed_missing, metrics_missing = EvaluationEngine.evaluate_json_schema(json_invalid, required_keys=["status", "count"])
    assert score_missing == 0.5
    assert passed_missing is False
    assert "count" in metrics_missing["missing_keys"]

def test_llm_judge_evaluator():
    generated = "Detailed analysis of quantum superposition in computing systems."
    expected = "Analysis of quantum computing."
    score, passed, metrics = EvaluationEngine.evaluate_llm_judge(generated, expected)
    assert score >= 0.70
    assert passed is True
    assert "accuracy_score" in metrics
