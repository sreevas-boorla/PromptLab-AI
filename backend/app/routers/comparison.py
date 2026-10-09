from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ComparisonRequest, ComparisonResponse, ComparisonModelResult, ExecutionMetrics
from ..providers import LLMProvider
from ..models import AnalyticsLog

router = APIRouter(prefix="/api/v1/comparison", tags=["Model Comparison"])

@router.post("/compare", response_model=ComparisonResponse)
def compare_models(req: ComparisonRequest, db: Session = Depends(get_db)):
    try:
        results = []
        fastest_model = ""
        cheapest_model = ""
        min_latency = float('inf')
        min_cost = float('inf')

        for model in req.models:
            out, lat, p_tok, c_tok, cost, is_mock = LLMProvider.generate(
                system_prompt=req.system_prompt,
                user_prompt=req.user_prompt,
                variables=req.input_variables,
                model=model,
                temperature=req.temperature,
                max_tokens=req.max_tokens
            )

            db.add(AnalyticsLog(model=model, latency_ms=lat, prompt_tokens=p_tok, completion_tokens=c_tok, total_cost=cost, action_type="comparison"))

            if lat < min_latency:
                min_latency = lat
                fastest_model = model

            if cost < min_cost:
                min_cost = cost
                cheapest_model = model

            res = ComparisonModelResult(
                model=model,
                output=out,
                metrics=ExecutionMetrics(
                    latency_ms=lat,
                    prompt_tokens=p_tok,
                    completion_tokens=c_tok,
                    total_tokens=p_tok + c_tok,
                    estimated_cost=cost,
                    is_mock=is_mock
                )
            )
            results.append(res)

        db.commit()

        return ComparisonResponse(
            results=results,
            fastest_model=fastest_model,
            cheapest_model=cheapest_model
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")
