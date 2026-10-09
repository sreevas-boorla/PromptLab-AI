import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import AnalyticsLog, EvalResult
from ..schemas import AnalyticsSummaryResponse

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Phase 5: Real Database Analytics Aggregation.
    Calculates actual token counts, costs, latencies, pass rates, and timeline stats directly from DB records.
    """
    logs = db.query(AnalyticsLog).all()

    total_executions = len(logs)
    if total_executions == 0:
        return AnalyticsSummaryResponse(
            total_executions=0,
            total_tokens=0,
            total_cost=0.0,
            avg_latency_ms=0.0,
            pass_rate_percentage=0.0,
            cost_by_model={},
            latency_by_model={},
            executions_over_time=[]
        )

    total_tokens = sum((l.prompt_tokens + l.completion_tokens) for l in logs)
    total_cost = sum(l.total_cost for l in logs)
    avg_latency = (sum(l.latency_ms for l in logs) / total_executions) if total_executions > 0 else 0.0

    eval_results = db.query(EvalResult).all()
    if eval_results:
        passed_evals = [r for r in eval_results if r.passed]
        pass_rate = (len(passed_evals) / len(eval_results)) * 100.0
    else:
        pass_rate = 0.0

    cost_by_model = {}
    latency_by_model = {}
    model_counts = {}

    for l in logs:
        m = l.model
        cost_by_model[m] = round(cost_by_model.get(m, 0.0) + l.total_cost, 6)
        latency_by_model[m] = latency_by_model.get(m, 0.0) + l.latency_ms
        model_counts[m] = model_counts.get(m, 0) + 1

    for m in latency_by_model:
        if model_counts[m] > 0:
            latency_by_model[m] = round(latency_by_model[m] / model_counts[m], 2)

    # Real timeline aggregation by date using SQLite strftime / func.date
    timeline_query = (
        db.query(
            func.date(AnalyticsLog.created_at).label("log_date"),
            func.count(AnalyticsLog.id).label("total_calls"),
            func.sum(AnalyticsLog.total_cost).label("daily_cost")
        )
        .group_by(func.date(AnalyticsLog.created_at))
        .order_by(func.date(AnalyticsLog.created_at).desc())
        .limit(14)
        .all()
    )

    timeline = []
    for row in reversed(timeline_query):
        date_str = str(row.log_date or datetime.date.today().strftime("%Y-%m-%d"))
        timeline.append({
            "date": date_str,
            "playground_calls": int(row.total_calls or 0),
            "evaluations_run": db.query(EvalResult).filter(func.date(EvalResult.run_id) == row.log_date).count(),
            "cost_usd": round(float(row.daily_cost or 0.0), 6)
        })

    return AnalyticsSummaryResponse(
        total_executions=total_executions,
        total_tokens=total_tokens,
        total_cost=round(total_cost, 6),
        avg_latency_ms=round(avg_latency, 2),
        pass_rate_percentage=round(pass_rate, 2),
        cost_by_model=cost_by_model,
        latency_by_model=latency_by_model,
        executions_over_time=timeline
    )
