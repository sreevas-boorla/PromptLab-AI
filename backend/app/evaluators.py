import re
import json
import math
import difflib
from typing import Dict, Any, Tuple, List
from .providers import LLMProvider

class EvaluationEngine:
    """Real evaluation algorithms for output scoring and validation."""

    @staticmethod
    def evaluate_exact_match(generated_output: str, expected_output: str, ignore_case: bool = True, strip_whitespace: bool = True) -> Tuple[float, bool, Dict[str, Any]]:
        gen = generated_output or ""
        exp = expected_output or ""

        if strip_whitespace:
            gen = gen.strip()
            exp = exp.strip()

        if ignore_case:
            gen_cmp = gen.lower()
            exp_cmp = exp.lower()
        else:
            gen_cmp = gen
            exp_cmp = exp

        is_exact = (gen_cmp == exp_cmp)
        score = 1.0 if is_exact else 0.0

        metrics = {
            "evaluator": "exact_match",
            "ignore_case": ignore_case,
            "strip_whitespace": strip_whitespace,
            "char_length_generated": len(gen),
            "char_length_expected": len(exp)
        }

        return score, is_exact, metrics

    @staticmethod
    def evaluate_regex(generated_output: str, pattern: str) -> Tuple[float, bool, Dict[str, Any]]:
        if not pattern:
            return 1.0, True, {"evaluator": "regex_match", "pattern": pattern, "matched": True}

        try:
            match = re.search(pattern, generated_output, re.MULTILINE | re.DOTALL)
            matched = match is not None
            score = 1.0 if matched else 0.0
            captured = match.groups() if match else ()
            metrics = {
                "evaluator": "regex_match",
                "pattern": pattern,
                "matched": matched,
                "captured_groups": list(captured)
            }
            return score, matched, metrics
        except Exception as e:
            return 0.0, False, {"evaluator": "regex_match", "error": str(e), "matched": False}

    @staticmethod
    def _char_ngrams(text: str, n: int = 3) -> List[str]:
        cleaned = re.sub(r'\s+', ' ', text.lower().strip())
        return [cleaned[i:i+n] for i in range(len(cleaned) - n + 1)]

    @classmethod
    def evaluate_semantic_similarity(cls, generated_output: str, expected_output: str) -> Tuple[float, bool, Dict[str, Any]]:
        """Calculates semantic similarity using character 3-gram cosine similarity and SequenceMatcher ratio."""
        gen = (generated_output or "").strip()
        exp = (expected_output or "").strip()

        if not gen or not exp:
            score = 1.0 if gen == exp else 0.0
            return score, score >= 0.50, {"evaluator": "semantic_similarity", "similarity": score}

        seq_ratio = difflib.SequenceMatcher(None, gen.lower(), exp.lower()).ratio()

        ngrams_gen = cls._char_ngrams(gen, 3)
        ngrams_exp = cls._char_ngrams(exp, 3)

        if not ngrams_gen or not ngrams_exp:
            score = round(seq_ratio, 4)
            return score, score >= 0.50, {"evaluator": "semantic_similarity", "seq_ratio": score}

        vocab = list(set(ngrams_gen).union(set(ngrams_exp)))
        v_gen = [ngrams_gen.count(g) for g in vocab]
        v_exp = [ngrams_exp.count(g) for g in vocab]

        dot = sum(g * e for g, e in zip(v_gen, v_exp))
        norm_g = math.sqrt(sum(g * g for g in v_gen))
        norm_e = math.sqrt(sum(e * e for e in v_exp))

        ngram_cosine = dot / (norm_g * norm_e) if (norm_g * norm_e) > 0 else 0.0
        combined_score = round(0.6 * ngram_cosine + 0.4 * seq_ratio, 4)
        passed = combined_score >= 0.50

        metrics = {
            "evaluator": "semantic_similarity",
            "char_3gram_cosine": round(ngram_cosine, 4),
            "sequence_matcher_ratio": round(seq_ratio, 4),
            "combined_score": combined_score,
            "threshold": 0.50
        }

        return combined_score, passed, metrics

    @staticmethod
    def evaluate_json_schema(generated_output: str, required_keys: List[str] = None) -> Tuple[float, bool, Dict[str, Any]]:
        required_keys = required_keys or []
        cleaned_output = (generated_output or "").strip()
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned_output)
        if json_match:
            cleaned_output = json_match.group(1).strip()

        try:
            parsed = json.loads(cleaned_output)
            if not isinstance(parsed, dict):
                return 0.5, False, {"evaluator": "json_schema", "is_valid_json": True, "is_dict": False}

            if not required_keys:
                return 1.0, True, {"evaluator": "json_schema", "is_valid_json": True, "present_keys": list(parsed.keys())}

            present_keys = [k for k in required_keys if k in parsed]
            missing_keys = [k for k in required_keys if k not in parsed]
            score = round(len(present_keys) / len(required_keys), 4) if required_keys else 1.0
            passed = (score == 1.0)

            metrics = {
                "evaluator": "json_schema",
                "is_valid_json": True,
                "required_keys": required_keys,
                "present_keys": present_keys,
                "missing_keys": missing_keys
            }
            return score, passed, metrics

        except json.JSONDecodeError as e:
            return 0.0, False, {"evaluator": "json_schema", "is_valid_json": False, "json_error": str(e)}

    @classmethod
    def evaluate_llm_judge(cls, generated_output: str, expected_output: str, criteria: Dict[str, Any] = None) -> Tuple[float, bool, Dict[str, Any]]:
        """
        Phase 3: Real LLM-as-a-Judge Evaluation using structured LLM rubric calls.
        Asks LLM to grade candidate output against accuracy, relevance, clarity, and safety directives.
        """
        criteria = criteria or {}
        gen_text = (generated_output or "").strip()
        exp_text = (expected_output or "").strip()

        if not gen_text:
            return 0.0, False, {"evaluator": "llm_judge", "error": "Candidate generated output is empty"}

        judge_model = criteria.get("judge_model")
        if not judge_model or judge_model == "mock-llm":
            raise ValueError("LLM-as-a-Judge requires an explicitly configured real judge model.")
        threshold = float(criteria.get("threshold", 0.70))
        custom_rubric = criteria.get("rubric", "Evaluate output accuracy, relevance, and clarity against expected target.")

        system_judge_prompt = (
            "You are an impartial, expert AI Evaluation Judge. "
            "Analyze the candidate output against the expected ground truth and rubric. "
            "You MUST respond ONLY with a valid JSON object matching this exact schema:\n"
            "```json\n"
            "{\n"
            '  "accuracy_score": 0.0 to 1.0,\n'
            '  "relevance_score": 0.0 to 1.0,\n'
            '  "clarity_score": 0.0 to 1.0,\n'
            '  "safety_score": 1.0,\n'
            '  "composite_score": 0.0 to 1.0,\n'
            '  "passed": true,\n'
            '  "reasoning": "Detailed justification of scores"\n'
            "}\n"
            "```"
        )

        user_judge_prompt = (
            f"### Evaluation Task:\n"
            f"**Candidate Generated Output**:\n{gen_text}\n\n"
            f"**Expected Ground Truth Output**:\n{exp_text if exp_text else 'N/A'}\n\n"
            f"**Evaluation Rubric Directives**:\n{custom_rubric}\n\n"
            f"Grade the candidate output now."
        )

        try:
            llm_out, lat, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
                system_prompt=system_judge_prompt,
                user_prompt=user_judge_prompt,
                variables={},
                model=judge_model,
                temperature=0.0,
                max_tokens=512
            )

            # Extract JSON from LLM Judge response
            clean_out = llm_out.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', clean_out)
            if json_match:
                clean_out = json_match.group(1).strip()

            judge_data = json.loads(clean_out)
            acc = float(judge_data["accuracy_score"])
            rel = float(judge_data["relevance_score"])
            cla = float(judge_data["clarity_score"])
            saf = float(judge_data["safety_score"])
            composite = round(0.35 * acc + 0.35 * rel + 0.20 * cla + 0.10 * saf, 4)
            if not all(0 <= item <= 1 for item in (acc, rel, cla, saf, composite)):
                raise ValueError("Judge scores must be between 0 and 1")
            passed = composite >= threshold
            reasoning = str(judge_data.get("reasoning", "LLM Judge evaluation completed."))

            metrics = {
                "evaluator": "llm_judge",
                "judge_model": judge_model,
                "accuracy_score": acc,
                "relevance_score": rel,
                "clarity_score": cla,
                "safety_score": saf,
                "composite_score": composite,
                "reasoning": reasoning,
                "is_mock_eval": is_mock,
                "judge_latency_ms": lat
            }

            return composite, passed, metrics

        except Exception as e:
            raise RuntimeError(f"LLM evaluation failed; no heuristic scores were recorded: {e}") from e

    @classmethod
    def run_evaluator(cls, evaluator_type: str, generated_output: str, expected_output: str = "", criteria: Dict[str, Any] = None) -> Tuple[float, bool, Dict[str, Any]]:
        criteria = criteria or {}

        if evaluator_type == "exact_match":
            ignore_case = criteria.get("ignore_case", True)
            strip_ws = criteria.get("strip_whitespace", True)
            return cls.evaluate_exact_match(generated_output, expected_output, ignore_case, strip_ws)

        elif evaluator_type == "regex_match":
            pattern = criteria.get("pattern", expected_output)
            return cls.evaluate_regex(generated_output, pattern)

        elif evaluator_type == "json_schema":
            required_keys = criteria.get("required_keys", [])
            return cls.evaluate_json_schema(generated_output, required_keys)

        elif evaluator_type == "llm_judge":
            return cls.evaluate_llm_judge(generated_output, expected_output, criteria)

        else:
            return cls.evaluate_semantic_similarity(generated_output, expected_output)
