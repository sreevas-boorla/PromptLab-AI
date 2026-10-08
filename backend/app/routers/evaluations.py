import json
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import EvalSuite, TestCase, EvalRun, EvalResult, AnalyticsLog
from ..schemas import (
    EvalSuiteCreate, EvalSuiteResponse, TestCaseCreate, TestCaseResponse,
    EvalRunRequest, EvalRunResponse, EvalResultResponse
)
from ..providers import LLMProvider
from ..evaluators import EvaluationEngine

router = APIRouter(prefix="/api/v1/evaluations", tags=["Evaluations"])

def _format_test_case(tc: TestCase) -> TestCaseResponse:
    return TestCaseResponse(
        id=tc.id,
        suite_id=tc.suite_id,
        name=tc.name,
        input_variables=json.loads(tc.input_variables_json or "{}"),
        expected_output=tc.expected_output,
        evaluator_type=tc.evaluator_type,
        criteria=json.loads(tc.criteria_json or "{}"),
        created_at=tc.created_at
    )

def _format_suite(suite: EvalSuite) -> EvalSuiteResponse:
    return EvalSuiteResponse(
        id=suite.id,
        name=suite.name,
        description=suite.description,
        category=suite.category,
        created_at=suite.created_at,
        updated_at=suite.updated_at,
        test_cases_count=len(suite.test_cases)
    )

@router.get("/suites", response_model=List[EvalSuiteResponse])
def list_suites(db: Session = Depends(get_db)):
    suites = db.query(EvalSuite).order_by(EvalSuite.updated_at.desc()).all()
    return [_format_suite(s) for s in suites]

@router.post("/suites", response_model=EvalSuiteResponse)
def create_suite(req: EvalSuiteCreate, db: Session = Depends(get_db)):
    suite = EvalSuite(
        name=req.name,
        description=req.description,
        category=req.category
    )
    db.add(suite)
    db.commit()
    db.refresh(suite)

    for tc_req in req.test_cases:
        tc = TestCase(
            suite_id=suite.id,
            name=tc_req.name,
            input_variables_json=json.dumps(tc_req.input_variables),
            expected_output=tc_req.expected_output,
            evaluator_type=tc_req.evaluator_type,
            criteria_json=json.dumps(tc_req.criteria)
        )
        db.add(tc)

    db.commit()
    db.refresh(suite)
    return _format_suite(suite)

@router.get("/suites/{suite_id}", response_model=EvalSuiteResponse)
def get_suite(suite_id: int, db: Session = Depends(get_db)):
    suite = db.query(EvalSuite).filter(EvalSuite.id == suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    return _format_suite(suite)

@router.get("/suites/{suite_id}/test-cases", response_model=List[TestCaseResponse])
def list_test_cases(suite_id: int, db: Session = Depends(get_db)):
    cases = db.query(TestCase).filter(TestCase.suite_id == suite_id).all()
    return [_format_test_case(c) for c in cases]

@router.post("/suites/{suite_id}/test-cases", response_model=TestCaseResponse)
def add_test_case(suite_id: int, req: TestCaseCreate, db: Session = Depends(get_db)):
    suite = db.query(EvalSuite).filter(EvalSuite.id == suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")

    tc = TestCase(
        suite_id=suite.id,
        name=req.name,
        input_variables_json=json.dumps(req.input_variables),
        expected_output=req.expected_output,
        evaluator_type=req.evaluator_type,
        criteria_json=json.dumps(req.criteria)
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return _format_test_case(tc)

@router.post("/run", response_model=EvalRunResponse)
def execute_eval_run(req: EvalRunRequest, db: Session = Depends(get_db)):
    suite = db.query(EvalSuite).filter(EvalSuite.id == req.suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="Evaluation suite not found")

    run = EvalRun(
        suite_id=suite.id,
        prompt_version_id=req.prompt_version_id,
        model=req.model,
        status="running",
        created_at=datetime.datetime.utcnow()
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    test_cases = db.query(TestCase).filter(TestCase.suite_id == suite.id).all()
    results_formatted = []
    total_score = 0.0
    passed_count = 0
    total_tokens = 0
    total_cost = 0.0

    for tc in test_cases:
        input_vars = json.loads(tc.input_variables_json or "{}")
        criteria = json.loads(tc.criteria_json or "{}")

        # Execute LLM call for current test case
        out, lat, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
            system_prompt=req.system_prompt or "",
            user_prompt=req.user_prompt,
            variables=input_vars,
            model=req.model
        )

        # REAL EVALUATION LOGIC - No hardcoded scores!
        score, passed, metrics_breakdown = EvaluationEngine.run_evaluator(
            evaluator_type=tc.evaluator_type,
            generated_output=out,
            expected_output=tc.expected_output or "",
            criteria=criteria
        )

        db_result = EvalResult(
            run_id=run.id,
            test_case_id=tc.id,
            generated_output=out,
            latency_ms=lat,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_cost=cost,
            score=score,
            passed=passed,
            metrics_breakdown_json=json.dumps(metrics_breakdown)
        )
        db.add(db_result)

        db.add(AnalyticsLog(model=req.model, latency_ms=lat, prompt_tokens=p_tok, completion_tokens=c_tok, total_cost=cost, action_type="evaluation"))

        total_score += score
        if passed:
            passed_count += 1
        total_tokens += (p_tok + c_tok)
        total_cost += cost

        results_formatted.append(EvalResultResponse(
            id=0,
            test_case_id=tc.id,
            test_case_name=tc.name,
            generated_output=out,
            latency_ms=lat,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_cost=cost,
            score=score,
            passed=passed,
            metrics_breakdown=metrics_breakdown
        ))

    num_cases = len(test_cases)
    avg_score = round(total_score / num_cases, 4) if num_cases > 0 else 0.0
    pass_rate = round((passed_count / num_cases) * 100, 2) if num_cases > 0 else 0.0

    summary_metrics = {
        "total_test_cases": num_cases,
        "passed_cases": passed_count,
        "failed_cases": num_cases - passed_count,
        "average_score": avg_score,
        "pass_rate_percentage": pass_rate,
        "total_tokens_consumed": total_tokens,
        "total_cost_usd": round(total_cost, 6)
    }

    run.status = "completed"
    run.completed_at = datetime.datetime.utcnow()
    run.summary_metrics_json = json.dumps(summary_metrics)
    db.commit()

    return EvalRunResponse(
        id=run.id,
        suite_id=suite.id,
        model=req.model,
        status="completed",
        created_at=run.created_at,
        completed_at=run.completed_at,
        summary_metrics=summary_metrics,
        results=results_formatted
    )
