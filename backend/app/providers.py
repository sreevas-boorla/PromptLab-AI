import os
import time
import json
import re
import httpx
from typing import Dict, Any, Tuple

# Token Pricing Estimations ($ per 1K tokens)
MODEL_PRICING = {
    # OpenAI Models
    "gpt-4o": {"prompt": 0.0025, "completion": 0.0100},
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "gpt-4-turbo": {"prompt": 0.0100, "completion": 0.0300},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    
    # Gemini Models
    "gemini-2.5-flash": {"prompt": 0.000075, "completion": 0.0003},
    "gemini-2.5-pro": {"prompt": 0.00125, "completion": 0.0050},
    "gemini-1.5-flash": {"prompt": 0.000075, "completion": 0.0003},
    "gemini-1.5-pro": {"prompt": 0.00125, "completion": 0.0050},
    
    # Groq Models
    "llama-3.3-70b-versatile": {"prompt": 0.00059, "completion": 0.00079},
    "llama-3.1-8b-instant": {"prompt": 0.00005, "completion": 0.00008},
    "mixtral-8x7b-32768": {"prompt": 0.00024, "completion": 0.00024},
    "gemma2-9b-it": {"prompt": 0.00020, "completion": 0.00020},
    
    # Explicit Mock Model
    "mock-llm": {"prompt": 0.0001, "completion": 0.0002}
}

class LLMProvider:
    @staticmethod
    def substitute_variables(prompt_text: str, variables: Dict[str, Any]) -> str:
        """Replaces {{variable_name}} templates with provided values."""
        result = prompt_text or ""
        if not variables:
            return result
        for key, value in variables.items():
            pattern = r'\{\{\s*' + re.escape(str(key)) + r'\s*\}\}'
            result = re.sub(pattern, str(value), result)
        return result

    @classmethod
    def generate(
        cls,
        system_prompt: str,
        user_prompt: str,
        variables: Dict[str, Any],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Tuple[str, float, int, int, float, bool]:
        """
        Executes server-side LLM call against real API providers (Gemini, OpenAI, Groq) or explicit Mock LLM.
        Returns: (output_text, latency_ms, prompt_tokens, completion_tokens, total_cost, is_mock)
        """
        start_time = time.time()
        final_user_prompt = cls.substitute_variables(user_prompt, variables)
        final_system_prompt = cls.substitute_variables(system_prompt, variables) if system_prompt else ""

        model_lower = model.lower()

        # Handle explicit mock model selection
        if model_lower == "mock-llm":
            output, p_tok, c_tok = cls._execute_mock_api(model, final_system_prompt, final_user_prompt, variables)
            is_mock = True

        # Phase 1: Gemini Provider Integration
        elif "gemini" in model_lower:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    f"Missing API key GEMINI_API_KEY for model '{model}'. "
                    "Configure GEMINI_API_KEY in environment or select 'mock-llm' for offline testing."
                )
            output, p_tok, c_tok = cls._execute_gemini_api(model, final_system_prompt, final_user_prompt, temperature, max_tokens, api_key)
            is_mock = False

        # Phase 2: OpenAI Provider Integration
        elif "gpt" in model_lower:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    f"Missing API key OPENAI_API_KEY for model '{model}'. "
                    "Configure OPENAI_API_KEY in environment or select 'mock-llm' for offline testing."
                )
            output, p_tok, c_tok = cls._execute_openai_api(model, final_system_prompt, final_user_prompt, temperature, max_tokens, api_key)
            is_mock = False

        # Phase 2: Groq Provider Integration
        elif "llama" in model_lower or "mixtral" in model_lower or "gemma" in model_lower:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    f"Missing API key GROQ_API_KEY for model '{model}'. "
                    "Configure GROQ_API_KEY in environment or select 'mock-llm' for offline testing."
                )
            output, p_tok, c_tok = cls._execute_groq_api(model, final_system_prompt, final_user_prompt, temperature, max_tokens, api_key)
            is_mock = False

        else:
            raise ValueError(f"Unsupported model '{model}'. Available models: {list(MODEL_PRICING.keys())}")

        latency_ms = round((time.time() - start_time) * 1000, 2)
        pricing = MODEL_PRICING.get(model_lower, MODEL_PRICING["mock-llm"])
        cost = round(((p_tok / 1000.0) * pricing["prompt"]) + ((c_tok / 1000.0) * pricing["completion"]), 6)

        return output, latency_ms, p_tok, c_tok, cost, is_mock

    @classmethod
    def _execute_gemini_api(
        cls, model: str, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int, api_key: str
    ) -> Tuple[str, int, int]:
        """Calls Google Gemini API via official REST endpoint."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload, headers={"Content-Type": "application/json"})
                
            if res.status_code != 200:
                err_detail = res.json().get("error", {}).get("message", res.text)
                raise RuntimeError(f"Gemini API Error [{res.status_code}]: {err_detail}")

            data = res.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini API returned zero completion candidates.")

            parts = candidates[0].get("content", {}).get("parts", [])
            output_text = "".join([p.get("text", "") for p in parts]).strip()

            usage = data.get("usageMetadata", {})
            prompt_tokens = usage.get("promptTokenCount", max(10, len((system_prompt + " " + user_prompt).split()) * 2))
            completion_tokens = usage.get("candidatesTokenCount", max(15, len(output_text.split()) * 2))

            return output_text, prompt_tokens, completion_tokens

        except httpx.TimeoutException:
            raise RuntimeError(f"Gemini API request timed out after 30 seconds for model '{model}'.")
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            raise RuntimeError(f"Failed to communicate with Gemini API: {str(e)}")

    @classmethod
    def _execute_openai_api(
        cls, model: str, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int, api_key: str
    ) -> Tuple[str, int, int]:
        """Calls OpenAI Chat Completions API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload, headers=headers)

            if res.status_code != 200:
                err_detail = res.json().get("error", {}).get("message", res.text)
                raise RuntimeError(f"OpenAI API Error [{res.status_code}]: {err_detail}")

            data = res.json()
            output_text = data["choices"][0]["message"]["content"].strip()
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", len((system_prompt + " " + user_prompt).split()) * 2)
            completion_tokens = usage.get("completion_tokens", len(output_text.split()) * 2)

            return output_text, prompt_tokens, completion_tokens

        except httpx.TimeoutException:
            raise RuntimeError(f"OpenAI API request timed out after 30 seconds for model '{model}'.")
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            raise RuntimeError(f"Failed to communicate with OpenAI API: {str(e)}")

    @classmethod
    def _execute_groq_api(
        cls, model: str, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int, api_key: str
    ) -> Tuple[str, int, int]:
        """Calls Groq OpenAI-compatible Chat API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload, headers=headers)

            if res.status_code != 200:
                err_detail = res.json().get("error", {}).get("message", res.text)
                raise RuntimeError(f"Groq API Error [{res.status_code}]: {err_detail}")

            data = res.json()
            output_text = data["choices"][0]["message"]["content"].strip()
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", len((system_prompt + " " + user_prompt).split()) * 2)
            completion_tokens = usage.get("completion_tokens", len(output_text.split()) * 2)

            return output_text, prompt_tokens, completion_tokens

        except httpx.TimeoutException:
            raise RuntimeError(f"Groq API request timed out after 30 seconds for model '{model}'.")
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            raise RuntimeError(f"Failed to communicate with Groq API: {str(e)}")

    @classmethod
    def _execute_mock_api(cls, model: str, system_prompt: str, user_prompt: str, variables: Dict[str, Any]) -> Tuple[str, int, int]:
        """Deterministic mock provider execution for offline / test environments."""
        time.sleep(0.05)
        prompt_tokens = max(10, len((system_prompt + " " + user_prompt).split()) * 2)

        prompt_lower = user_prompt.lower()
        sys_lower = system_prompt.lower()

        if "json" in sys_lower or "json" in prompt_lower or "schema" in prompt_lower:
            mock_output = json.dumps({
                "status": "success",
                "model_evaluated": model,
                "analysis": f"Evaluated query: {user_prompt[:50]}...",
                "metrics": {"confidence": 0.96, "completeness": 0.98},
                "summary": "Output rendered in structured JSON as requested."
            }, indent=2)
        elif "step-by-step" in prompt_lower or "think" in prompt_lower or "chain of thought" in prompt_lower:
            mock_output = (
                f"### Analysis & Reasoning ({model})\n"
                f"1. **Deconstruct Requirement**: Parsed parameters {list(variables.keys())}.\n"
                f"2. **Evaluate Context**: Applied directives from system prompt.\n"
                f"3. **Synthesize Solution**: Formulated robust resolution.\n\n"
                f"**Final Answer**: Processed query for '{user_prompt[:40]}...' successfully."
            )
        elif "role" in sys_lower or "expert" in sys_lower or "act as" in prompt_lower:
            mock_output = f"As a domain expert using {model}, here is the analysis:\n\nRegarding '{user_prompt[:60]}': The input has been thoroughly processed according to strict guidelines."
        elif "summarize" in prompt_lower or "concise" in prompt_lower:
            mock_output = f"Concise Summary ({model}): Executive synthesis completed for request with parameters {variables}."
        else:
            mock_output = f"Response from {model}:\n\nProcessed prompt successfully with input variables {variables}. System context active."

        completion_tokens = max(15, len(mock_output.split()) * 2)
        return mock_output, prompt_tokens, completion_tokens
