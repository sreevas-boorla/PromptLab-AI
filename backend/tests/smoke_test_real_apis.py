import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.providers import LLMProvider

def run_smoke_tests():
    print("==================================================")
    print("   PromptLab AI - Real LLM Provider Smoke Tests   ")
    print("==================================================")

    # 1. Gemini Smoke Test
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print("\n[GEMINI] Testing Gemini API (gemini-1.5-flash)...")
        try:
            out, lat, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
                system_prompt="You are a smoke test evaluator.",
                user_prompt="Respond with 'Gemini API Operational'.",
                variables={},
                model="gemini-1.5-flash"
            )
            print(f"  Status: SUCCESS | Latency: {lat}ms | Tokens: {p_tok}+{c_tok} | Cost: ${cost}")
            print(f"  Output: {out[:100]}")
        except Exception as e:
            print(f"  Status: FAILED | Error: {e}")
    else:
        print("\n[GEMINI] SKIPPED (GEMINI_API_KEY not set in environment)")

    # 2. OpenAI Smoke Test
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("\n[OPENAI] Testing OpenAI API (gpt-4o-mini)...")
        try:
            out, lat, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
                system_prompt="You are a smoke test evaluator.",
                user_prompt="Respond with 'OpenAI API Operational'.",
                variables={},
                model="gpt-4o-mini"
            )
            print(f"  Status: SUCCESS | Latency: {lat}ms | Tokens: {p_tok}+{c_tok} | Cost: ${cost}")
            print(f"  Output: {out[:100]}")
        except Exception as e:
            print(f"  Status: FAILED | Error: {e}")
    else:
        print("\n[OPENAI] SKIPPED (OPENAI_API_KEY not set in environment)")

    # 3. Groq Smoke Test
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print("\n[GROQ] Testing Groq API (llama-3.1-8b-instant)...")
        try:
            out, lat, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
                system_prompt="You are a smoke test evaluator.",
                user_prompt="Respond with 'Groq API Operational'.",
                variables={},
                model="llama-3.1-8b-instant"
            )
            print(f"  Status: SUCCESS | Latency: {lat}ms | Tokens: {p_tok}+{c_tok} | Cost: ${cost}")
            print(f"  Output: {out[:100]}")
        except Exception as e:
            print(f"  Status: FAILED | Error: {e}")
    else:
        print("\n[GROQ] SKIPPED (GROQ_API_KEY not set in environment)")

    print("\n==================================================")
    print("Smoke tests finished.")

if __name__ == "__main__":
    run_smoke_tests()
