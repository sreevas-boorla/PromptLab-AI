from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import PlaygroundExecuteRequest, PlaygroundExecuteResponse, ExecutionMetrics
from ..providers import LLMProvider
from ..models import AnalyticsLog

router = APIRouter(prefix="/api/v1/playground", tags=["Playground"])

@router.post("/execute", response_model=PlaygroundExecuteResponse)
def execute_prompt(req: PlaygroundExecuteRequest, db: Session = Depends(get_db)):
    try:
        output, latency_ms, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
            system_prompt=req.system_prompt,
            user_prompt=req.user_prompt,
            variables=req.input_variables,
            model=req.settings.model,
            temperature=req.settings.temperature,
            max_tokens=req.settings.max_tokens
        )

        sub_prompt = LLMProvider.substitute_variables(req.user_prompt, req.input_variables)

        # Log metrics to DB
        log_entry = AnalyticsLog(
            model=req.settings.model,
            latency_ms=latency_ms,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_cost=cost,
            action_type="playground"
        )
        db.add(log_entry)
        db.commit()

        metrics = ExecutionMetrics(
            latency_ms=latency_ms,
            prompt_tokens=p_tok,
            completion_tokens=c_tok,
            total_tokens=p_tok + c_tok,
            estimated_cost=cost,
            is_mock=is_mock
        )

        return PlaygroundExecuteResponse(
            output=output,
            metrics=metrics,
            substituted_prompt=sub_prompt
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")
