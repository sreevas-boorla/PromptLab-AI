import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.optimizer import PromptOptimizerEngine

def test_chain_of_thought_strategy():
    orig = "Summarize the quantum physics paper."
    opt, summary = PromptOptimizerEngine.optimize_prompt(orig, strategy="chain_of_thought")
    assert "Instructions for Reasoning" in opt
    assert "step-by-step" in opt.lower()
    assert "Chain-of-Thought" in summary

def test_role_framing_strategy():
    orig = "Draft a database migration plan."
    opt, summary = PromptOptimizerEngine.optimize_prompt(orig, strategy="role_framing")
    assert "Principal Domain Specialist" in opt
    assert "role framing" in summary.lower()

def test_json_structuring_strategy():
    orig = "Extract entity details."
    opt, summary = PromptOptimizerEngine.optimize_prompt(orig, strategy="json_structuring")
    assert "```json" in opt
    assert "JSON" in summary
