import type {
  RecommendationHistoryRequest,
  RecommendationHistoryResponse,
  RecommendationRequest,
  RecommendationResponse,
} from "@/features/recommendations/types";
import { apiBaseUrl } from "@/lib/api/base-url";

const API_BASE_URL = apiBaseUrl();

export async function postRecommendations(
  payload: RecommendationRequest,
): Promise<RecommendationResponse> {
  const response = await fetch(`${API_BASE_URL}/recommendations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Recommendation request failed with status ${response.status}`);
  }

  return (await response.json()) as RecommendationResponse;
}

export async function postRecommendationHistory(
  payload: RecommendationHistoryRequest,
): Promise<RecommendationHistoryResponse> {
  const response = await fetch(`${API_BASE_URL}/recommendations/history`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Recommendation history request failed with status ${response.status}`);
  }

  return (await response.json()) as RecommendationHistoryResponse;
}
