import sys
import os
import json

# Ensure parent path is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import Prompt, PromptVersion, EvalSuite, TestCase, AnalyticsLog

def run_migrations():
    print("[MIGRATION] Creating database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed initial prompt if empty
        if db.query(Prompt).count() == 0:
            print("[SEED] Seeding default Prompt Library templates...")
            p1 = Prompt(
                title="Customer Support Response Generator",
                description="Generates empathetic and structured customer support replies.",
                category="Customer Care",
                tags="support,empathy,customer-service"
            )
            db.add(p1)
            db.commit()
            db.refresh(p1)

            v1 = PromptVersion(
                prompt_id=p1.id,
                version_number=1,
                system_prompt="You are an empathetic customer support expert.",
                user_prompt="Draft a response for customer {{customer_name}} regarding issue: {{issue_description}}.",
                model_config_json=json.dumps({"model": "gpt-4o", "temperature": 0.7, "max_tokens": 512}),
                notes="v1 initial prompt template"
            )
            db.add(v1)

            p2 = Prompt(
                title="Code Refactor & Security Audit",
                description="Audits source code snippets for security vulnerabilities and performance bottlenecks.",
                category="Engineering",
                tags="code,security,refactor"
            )
            db.add(p2)
            db.commit()
            db.refresh(p2)

            v2 = PromptVersion(
                prompt_id=p2.id,
                version_number=1,
                system_prompt="You are a Principal Security Engineer.",
                user_prompt="Review the following {{language}} code for vulnerabilities:\n\n```{{language}}\n{{code_snippet}}\n```",
                model_config_json=json.dumps({"model": "claude-3-5-sonnet", "temperature": 0.2, "max_tokens": 1024}),
                notes="v1 security auditor"
            )
            db.add(v2)

        # Seed initial Evaluation Suite if empty
        if db.query(EvalSuite).count() == 0:
            print("[SEED] Seeding default Evaluation Suite & Test Cases...")
            suite = EvalSuite(
                name="System Prompt Benchmark Suite",
                description="Comprehensive evaluation dataset for classification & reasoning accuracy.",
                category="Benchmark"
            )
            db.add(suite)
            db.commit()
            db.refresh(suite)

            tc1 = TestCase(
                suite_id=suite.id,
                name="JSON Structure Test",
                input_variables_json=json.dumps({"input_text": "Extract name John Doe, age 30"}),
                expected_output='{"name": "John Doe", "age": 30}',
                evaluator_type="json_schema",
                criteria_json=json.dumps({"required_keys": ["name", "age"]})
            )

            tc2 = TestCase(
                suite_id=suite.id,
                name="Exact Keyword Verification",
                input_variables_json=json.dumps({"product": "PromptLab"}),
                expected_output="PromptLab AI is operational",
                evaluator_type="exact_match",
                criteria_json=json.dumps({"ignore_case": True, "strip_whitespace": True})
            )

            tc3 = TestCase(
                suite_id=suite.id,
                name="Semantic Reasoning Quality",
                input_variables_json=json.dumps({"topic": "Quantum Computing"}),
                expected_output="Quantum computing utilizes qubits and superposition to process complex information.",
                evaluator_type="semantic_similarity",
                criteria_json=json.dumps({})
            )

            db.add_all([tc1, tc2, tc3])

        # Seed analytics logs if empty
        if db.query(AnalyticsLog).count() == 0:
            print("[SEED] Seeding analytics baseline metrics...")
            db.add(AnalyticsLog(model="gpt-4o", latency_ms=145.2, prompt_tokens=120, completion_tokens=85, total_cost=0.00115, action_type="playground"))
            db.add(AnalyticsLog(model="claude-3-5-sonnet", latency_ms=180.5, prompt_tokens=140, completion_tokens=110, total_cost=0.00207, action_type="optimizer"))
            db.add(AnalyticsLog(model="gemini-1.5-pro", latency_ms=110.0, prompt_tokens=90, completion_tokens=60, total_cost=0.00041, action_type="comparison"))

        db.commit()
        print("[MIGRATION] Database migration and seeding finished successfully.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_migrations()
