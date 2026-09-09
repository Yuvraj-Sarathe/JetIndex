"""AI Policy Analyst - NLP Query Interface API."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


class AnalystQueryInput(BaseModel):
    question: str = Field(..., description="Natural language question for the AI policy desk")
    user_role: str = Field(default="POLICY_ECONOMIST")


@router.post("/ask")
def ask_policy_analyst(
    query: AnalystQueryInput,
    _token: str = Depends(require_token),
) -> dict:
    """Answers natural language macroeconomic questions using grounded econometric evidence."""
    if settings.MOCK_MODE:
        return {
            "data_tag": "MOCK_DATA",
            "question": query.question,
            "detected_intent": "EXPLAIN_INFLATION_MOVEMENT",
            "answer_summary": "Airfare inflation moved by +0.24% today, bringing the Master Laspeyres Index to 107.09.",
            "statutory_citations": ["MoSPI Methodology for CPI", "ILO CPI Manual (2020)"],
            "affected_routes": ["DEL-BOM", "DEL-BLR"],
        }
    try:
        from engine.ai_analyst.policy_analyst import AIPolicyAnalyst, PolicyAnalystQuery
        analyst = AIPolicyAnalyst()
        result = analyst.answer_query(PolicyAnalystQuery(question=query.question, user_role=query.user_role))
        from dataclasses import asdict
        return {"data_tag": "REAL_COMPUTED", **asdict(result)}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
