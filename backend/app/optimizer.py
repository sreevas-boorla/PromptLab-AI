from typing import Tuple, Dict, Any

class PromptOptimizerEngine:
    """Prompt Optimization Engine offering multi-strategy prompt transformations."""

    @staticmethod
    def optimize_prompt(original_prompt: str, strategy: str = "chain_of_thought") -> Tuple[str, str]:
        """
        Transforms prompt based on selected strategy.
        Returns: (optimized_prompt, strategy_applied_summary)
        """
        original_clean = original_prompt.strip()

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
            # Token reduction while preserving semantic core
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
