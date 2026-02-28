from fastapi import APIRouter

from app.schemas.safety import SafetyEvaluateRequest, SafetyEvaluateResponse
from app.services.safety_monitor_service import SafetyMonitorService

router = APIRouter()
safety_monitor_service = SafetyMonitorService()


@router.post("/safety/evaluate", response_model=SafetyEvaluateResponse)
def evaluate_safety(payload: SafetyEvaluateRequest) -> SafetyEvaluateResponse:
    return safety_monitor_service.evaluate(payload)
