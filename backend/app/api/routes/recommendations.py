from fastapi import APIRouter

from app.schemas.recommendations import (
    RecommendationHistoryRequest,
    RecommendationHistoryResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()


@router.post("/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    return recommendation_service.generate_recommendations(payload)


@router.post("/recommendations/history", response_model=RecommendationHistoryResponse)
def recommendation_history(payload: RecommendationHistoryRequest) -> RecommendationHistoryResponse:
    return recommendation_service.get_history(
        user_id=payload.user_id,
        role=payload.role,
        request_ids=payload.request_ids,
    )
