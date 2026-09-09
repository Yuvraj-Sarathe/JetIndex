"""Model Validation Center API."""

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_token

router = APIRouter()


@router.get("")
def get_validation_report(
    _token: str = Depends(require_token),
) -> dict:
    """Returns multi-model validation report: Pearson R, MAPE, R², error distributions."""
    if settings.MOCK_MODE:
        return {
            "data_tag": "MOCK_DATA",
            "validation_result": "ALL_MANDATES_PASSED_HIGH_FIDELITY",
            "models_comparison": [
                {"model": "Official Algorithmic Index", "pearson_r": 0.9858, "mape_pct": 0.838, "r2_score": 0.9709},
                {"model": "Ridge + GBDT Ensemble", "pearson_r": 0.92, "mape_pct": 1.5, "r2_score": 0.85},
            ],
            "error_distribution": {"mean_residual": 0.04, "std_residual": 1.15, "normality_test": "PASSED"},
        }
    try:
        from engine.validation.model_validator import get_validation_center_report

        return {"data_tag": "REAL_COMPUTED", **get_validation_center_report()}
    except Exception as e:
        return {"error": str(e), "data_tag": "ERROR"}
