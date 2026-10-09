import re
import json
from typing import Tuple, Dict, Any
from .providers import LLMProvider

class PromptOptimizerEngine:
    """Phase 4: AI-Guided Prompt Optimization Engine using LLM prompt analysis and transformations."""

    @classmethod
    def optimize_prompt(
        cls, original_prompt: str, strategy: str = "chain_of_thought", model: str = "gpt-4o"
    ) -> Tuple[str, str]:
        """
        Transforms original draft prompt into an enhanced version using AI LLM reasoning or fallback template strategy.
        Returns: (optimized_prompt, strategy_applied_summary)
        """
        original_clean = (original_prompt or "").strip()
        if not original_clean:
            return "", "No prompt provided to optimize."

        # If explicitly selecting mock model, use deterministic template transformation
        if model.lower() == "mock-llm":
            return cls._template_optimize(original_clean, strategy)

        # AI-Guided Optimization via LLM Meta-Prompt
        system_meta_prompt = (
            "You are a Principal AI Prompt Engineer. Your task is to analyze and optimize a draft user prompt. "
            "You MUST preserve the user's core intent and domain parameters while removing ambiguities, "
            "enhancing structural clarity, and applying the requested prompt engineering strategy.\n\n"
            "Respond ONLY with a valid JSON object matching this exact schema:\n"
            "```json\n"
            "{\n"
            '  "optimized_prompt": "<enhanced prompt containing user variables>",\n'
            '  "strategy_applied": "<brief 1-sentence summary of enhancements applied>",\n'
            '  "key_improvements": ["<improvement 1>", "<improvement 2>"]\n'
            "}\n"
            "```"
        )

        user_meta_prompt = (
            f"### Target Optimization Strategy: {strategy}\n"
            f"### Original Draft Prompt:\n{original_clean}\n\n"
            "Generate the optimized prompt JSON now."
        )

        try:
            llm_out, lat, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
                system_prompt=system_meta_prompt,
                user_prompt=user_meta_prompt,
                variables={},
                model=model,
                temperature=0.3,
                max_tokens=1024
            )

            # Parse JSON from LLM response
            clean_out = llm_out.strip()
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', clean_out)
            if json_match:
                clean_out = json_match.group(1).strip()

            opt_data = json.loads(clean_out)
            opt_prompt = str(opt_data.get("optimized_prompt", "")).strip()
            summary = str(opt_data.get("strategy_applied", f"Applied AI-guided {strategy} optimization.")).strip()

            if not opt_prompt:
                raise ValueError("LLM returned an empty optimized prompt")

            return opt_prompt, summary

        except Exception as e:
            raise RuntimeError(f"AI prompt optimization failed: {e}") from e

    @staticmethod
    def _template_optimize(original_clean: str, strategy: str) -> Tuple[str, str]:
        """Deterministic strategy templates for mock mode or offline fallbacks."""
        if strategy == "chain_of_thought":
            optimized = (
                f"{original_clean}\n\n"
                "### Instructions for Reasoning:\n"
                "Before providing your final answer, break down the problem step-by-step:\n"
                "1. Analyze key inputs and explicit requirements.\n"
                "2. Identify potential edge cases or constraints.\n"
                "3. Reason logically through each intermediate step.\n"
                "4. Provide a clear, definitive final response."
            )
            summary = "Applied Chain-of-Thought reasoning directives to force multi-step decomposition."

        elif strategy == "few_shot":
            optimized = (
                f"### Task Definition:\n{original_clean}\n\n"
                "### Demonstrative Exemplars:\n"
                "Example 1:\n"
                "Input: {{sample_input_1}}\n"
                "Output: [Structured Model Response]\n\n"
                "Example 2:\n"
                "Input: {{sample_input_2}}\n"
                "Output: [Structured Model Response]\n\n"
                "Now process the current input adhering strictly to the pattern shown above."
            )
            summary = "Injected structured few-shot exemplars and task pattern framing."

        elif strategy == "role_framing":
            optimized = (
                "### Persona & Expertise:\n"
                "You are a world-class Principal Domain Specialist with deep expertise and zero tolerance for ambiguity.\n\n"
                "### Objective:\n"
                f"{original_clean}\n\n"
                "### Response Constraints:\n"
                "- Maintain authoritative, rigorous, and professional tone.\n"
                "- Directly answer without unnecessary pleasantries."
            )
            summary = "Configured principal specialist role framing with strict quality directives."

        elif strategy == "compression":
            words = original_clean.split()
            compressed = " ".join([w for w in words if w.lower() not in ["please", "kindly", "i", "want", "you", "to", "would", "like"]])
            optimized = f"Directive: {compressed}. Output concisely without fluff."
            summary = "Compressed token length by removing conversational filler and enforcing conciseness."

        elif strategy == "json_structuring":
            optimized = (
                f"{original_clean}\n\n"
                "### Output Format Constraint:\n"
                "Respond ONLY with a valid JSON object matching this schema:\n"
                "```json\n"
                "{\n"
                '  "status": "success",\n'
                '  "result": "<detailed answer>",\n'
                '  "key_takeaways": ["<item1>", "<item2>"]\n'
                "}\n"
                "```\n"
                "Do not include any text outside the JSON code block."
            )
            summary = "Enforced strict JSON schema constraints and format isolation."

        else:
            optimized = original_clean
            summary = "No optimization strategy applied."

        return optimized, summary
