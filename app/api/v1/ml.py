"""
JetIndex - ML Model Training & Nowcast API Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class TrainRequest(BaseModel):
    force_retrain: bool = False


class TrainResponse(BaseModel):
    status: str
    model_version: str
    r2_train: float
    r2_test: float
    rmse_test: float
    mape_test: float
    sample_size: int
    message: str


class NowcastRequest(BaseModel):
    horizon_days: int = 14


class ForecastStepResponse(BaseModel):
    forecast_date: str
    horizon_days: int
    predicted_laspeyres_index: float
    confidence_interval_95_lower: float
    confidence_interval_95_upper: float
    projected_daily_change_pct: float
    projected_transport_impact_bps: float
    projected_headline_cpi_impact_bps: float


class NowcastResponse(BaseModel):
    as_of_date: str
    current_index: float
    model_version: str
    forecast_horizon_days: int
    summary_mean_forecast: float
    net_projected_transport_bps: float
    net_projected_headline_cpi_bps: float
    monetary_policy_alert: str
    forecast_steps: list[ForecastStepResponse]
    feature_importances: dict[str, float]
    generated_at: str


@router.post("/train", response_model=TrainResponse)
async def train_model(req: TrainRequest):
    """Train the econometric nowcast ensemble (Ridge + GBDT)."""
    try:
        from engine.model_trainer import train_nowcast_model

        ensemble, metrics = train_nowcast_model()

        return TrainResponse(
            status="SUCCESS",
            model_version=metrics.model_version,
            r2_train=metrics.r2_train,
            r2_test=metrics.r2_test,
            rmse_test=metrics.rmse_test,
            mape_test=metrics.mape_test,
            sample_size=metrics.sample_size,
            message="Model trained successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}") from e


@router.post("/nowcast", response_model=NowcastResponse)
async def generate_nowcast(req: NowcastRequest):
    """Generate multi-horizon forward nowcast with confidence intervals."""
    try:
        from engine.nowcast_predictor import InflationNowcastPredictor

        predictor = InflationNowcastPredictor()
        report = predictor.generate_nowcast(horizon_days=req.horizon_days)

        return NowcastResponse(
            as_of_date=report.as_of_date,
            current_index=report.current_index,
            model_version=report.model_version,
            forecast_horizon_days=report.forecast_horizon_days,
            summary_mean_forecast=report.summary_mean_forecast,
            net_projected_transport_bps=report.net_projected_transport_bps,
            net_projected_headline_cpi_bps=report.net_projected_headline_cpi_bps,
            monetary_policy_alert=report.monetary_policy_alert,
            forecast_steps=[
                ForecastStepResponse(
                    forecast_date=step.forecast_date,
                    horizon_days=step.horizon_days,
                    predicted_laspeyres_index=step.predicted_laspeyres_index,
                    confidence_interval_95_lower=step.confidence_interval_95_lower,
                    confidence_interval_95_upper=step.confidence_interval_95_upper,
                    projected_daily_change_pct=step.projected_daily_change_pct,
                    projected_transport_impact_bps=step.projected_transport_impact_bps,
                    projected_headline_cpi_impact_bps=step.projected_headline_cpi_impact_bps,
                )
                for step in report.forecast_steps
            ],
            feature_importances=report.feature_importances,
            generated_at=report.generated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nowcast failed: {str(e)}") from e


@router.get("/model/status")
async def get_model_status():
    """Check if a trained model exists and get its metadata."""
    import os

    from engine.model_trainer import MODEL_ARTIFACT_PATH

    if os.path.exists(MODEL_ARTIFACT_PATH):
        from engine.model_trainer import EconometricNowcastEnsemble

        try:
            model = EconometricNowcastEnsemble.load(MODEL_ARTIFACT_PATH)
            return {
                "exists": True,
                "is_trained": model.is_trained,
                "model_version": model.metrics.model_version if model.metrics else "unknown",
                "metrics": model.metrics.__dict__ if model.metrics else None,
            }
        except Exception:
            return {"exists": True, "is_trained": False, "error": "Failed to load model"}
    else:
        return {"exists": False, "is_trained": False}
