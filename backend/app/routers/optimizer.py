from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import OptimizerRequest, OptimizerResponse, OptimizerResult, ExecutionMetrics
from ..providers import LLMProvider
from ..optimizer import PromptOptimizerEngine
from ..evaluators import EvaluationEngine
from ..models import AnalyticsLog

router = APIRouter(prefix="/api/v1/optimizer", tags=["Optimizer"])

@router.post("/optimize", response_model=OptimizerResponse)
def optimize_prompt_and_run(req: OptimizerRequest, db: Session = Depends(get_db)):
    try:
        # 1. Transform original prompt using selected strategy
        opt_prompt_text, strategy_summary = PromptOptimizerEngine.optimize_prompt(
            req.original_prompt, req.strategy
        )

        # 2. Execute ORIGINAL Prompt with inputs & settings
        orig_out, orig_lat, orig_pt, orig_ct, orig_cost, orig_mock = LLMProvider.generate(
            system_prompt=req.system_prompt,
            user_prompt=req.original_prompt,
            variables=req.input_variables,
            model=req.settings.model,
            temperature=req.settings.temperature,
            max_tokens=req.settings.max_tokens
        )

        # 3. Execute OPTIMIZED Prompt with IDENTICAL inputs & settings
        opt_out, opt_lat, opt_pt, opt_ct, opt_cost, opt_mock = LLMProvider.generate(
            system_prompt=req.system_prompt,
            user_prompt=opt_prompt_text,
            variables=req.input_variables,
            model=req.settings.model,
            temperature=req.settings.temperature,
            max_tokens=req.settings.max_tokens
        )

        # 4. Evaluate quality scores for both prompts using LLM-as-a-judge real rubric
        orig_score, _, _ = EvaluationEngine.evaluate_llm_judge(orig_out, "")
        opt_score, _, _ = EvaluationEngine.evaluate_llm_judge(opt_out, "")

        # Log analytics
        db.add(AnalyticsLog(model=req.settings.model, latency_ms=orig_lat, prompt_tokens=orig_pt, completion_tokens=orig_ct, total_cost=orig_cost, action_type="optimizer_original"))
        db.add(AnalyticsLog(model=req.settings.model, latency_ms=opt_lat, prompt_tokens=opt_pt, completion_tokens=opt_ct, total_cost=opt_cost, action_type="optimizer_optimized"))
        db.commit()

        orig_result = OptimizerResult(
            prompt=req.original_prompt,
            output=orig_out,
            metrics=ExecutionMetrics(
                latency_ms=orig_lat, prompt_tokens=orig_pt, completion_tokens=orig_ct,
                total_tokens=orig_pt + orig_ct, estimated_cost=orig_cost, is_mock=orig_mock
            ),
            eval_score=orig_score
        )

        opt_result = OptimizerResult(
            prompt=opt_prompt_text,
            output=opt_out,
            metrics=ExecutionMetrics(
                latency_ms=opt_lat, prompt_tokens=opt_pt, completion_tokens=opt_ct,
                total_tokens=opt_pt + opt_ct, estimated_cost=opt_cost, is_mock=opt_mock
            ),
            eval_score=opt_score
        )

        return OptimizerResponse(
            original=orig_result,
            optimized=opt_result,
            strategy_applied=strategy_summary,
            improvement_summary=f"Optimized prompt quality score: {opt_score:.2f} vs Original: {orig_score:.2f}."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimizer error: {str(e)}")
