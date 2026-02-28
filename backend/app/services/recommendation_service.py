import logging
import math
from hashlib import sha256
from typing import Any
from urllib.parse import quote_plus
from uuid import uuid4

from app.core.database import SessionLocal
from app.core.settings import settings
from app.models.enums import (
    AuditEventType,
    ProviderEventScope,
    ProviderEventStatus,
    RoleType,
    TravelMode,
)
from app.providers.router import ProviderRouter
from app.repositories.audit_repository import AuditRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.recommendations import (
    Coordinates,
    RecommendationHistoryResponse,
    RecommendationContext,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse
)
from app.services.weather_service import WeatherService

_OUTDOOR_PLACE_TYPES = {"park", "tourist_attraction",
                        "campground", "hiking_area", "beach"}
_INDOOR_PLACE_TYPES = {"cafe", "restaurant",
                       "museum", "shopping_mall", "library"}
_FALLBACK_DISCOVERY_QUERIES = ["cafe", "park", "museum", "restaurant"]
_WEATHER_INDOOR_CONDITIONS = {"rain", "drizzle", "thunderstorm", "snow"}
_HK_FALLBACK_PLACE_CATALOG: list[dict[str, Any]] = [
    {
        "place_id": "hk-hung-hom-promenade",
        "name": "Hung Hom Promenade",
        "address": "Hung Hom Waterfront, Kowloon",
        "types": ["park", "point_of_interest"],
        "latitude": 22.3021,
        "longitude": 114.1872,
    },
    {
        "place_id": "hk-kowloon-park",
        "name": "Kowloon Park",
        "address": "22 Austin Road, Tsim Sha Tsui",
        "types": ["park", "point_of_interest"],
        "latitude": 22.3019,
        "longitude": 114.1716,
    },
    {
        "place_id": "hk-art-park",
        "name": "Art Park (West Kowloon Cultural District)",
        "address": "West Kowloon, Kowloon",
        "types": ["park", "tourist_attraction", "point_of_interest"],
        "latitude": 22.2937,
        "longitude": 114.1580,
    },
    {
        "place_id": "hk-victoria-park",
        "name": "Victoria Park",
        "address": "1 Hing Fat Street, Causeway Bay",
        "types": ["park", "point_of_interest"],
        "latitude": 22.2803,
        "longitude": 114.1916,
    },
    {
        "place_id": "hk-hong-kong-park",
        "name": "Hong Kong Park",
        "address": "19 Cotton Tree Drive, Central",
        "types": ["park", "point_of_interest"],
        "latitude": 22.2772,
        "longitude": 114.1616,
    },
    {
        "place_id": "hk-nan-lian-garden",
        "name": "Nan Lian Garden",
        "address": "60 Fung Tak Road, Diamond Hill",
        "types": ["park", "tourist_attraction", "point_of_interest"],
        "latitude": 22.3402,
        "longitude": 114.2017,
    },
    {
        "place_id": "hk-k11-musea",
        "name": "K11 MUSEA",
        "address": "18 Salisbury Road, Tsim Sha Tsui",
        "types": ["shopping_mall", "point_of_interest"],
        "latitude": 22.2933,
        "longitude": 114.1745,
    },
    {
        "place_id": "hk-harbour-city",
        "name": "Harbour City",
        "address": "3-27 Canton Road, Tsim Sha Tsui",
        "types": ["shopping_mall", "point_of_interest"],
        "latitude": 22.2952,
        "longitude": 114.1679,
    },
    {
        "place_id": "hk-pmq",
        "name": "PMQ",
        "address": "35 Aberdeen Street, Central",
        "types": ["art_gallery", "point_of_interest"],
        "latitude": 22.2838,
        "longitude": 114.1505,
    },
    {
        "place_id": "hk-tai-kwun",
        "name": "Tai Kwun",
        "address": "10 Hollywood Road, Central",
        "types": ["museum", "point_of_interest"],
        "latitude": 22.2819,
        "longitude": 114.1549,
    },
    {
        "place_id": "hk-kam-wah-cafe",
        "name": "Kam Wah Cafe",
        "address": "47 Bute Street, Mong Kok",
        "types": ["cafe", "food"],
        "latitude": 22.3241,
        "longitude": 114.1688,
    },
    {
        "place_id": "hk-sing-heung-yuen",
        "name": "Sing Heung Yuen",
        "address": "2 Mee Lun Street, Central",
        "types": ["restaurant", "food"],
        "latitude": 22.2841,
        "longitude": 114.1542,
    },
    {
        "place_id": "hk-ozone",
        "name": "OZONE",
        "address": "Ritz-Carlton Hong Kong, West Kowloon",
        "types": ["bar", "night_club", "point_of_interest"],
        "latitude": 22.3036,
        "longitude": 114.1609,
    },
    {
        "place_id": "hk-quinary",
        "name": "Quinary",
        "address": "56-58 Hollywood Road, Central",
        "types": ["bar", "night_club", "point_of_interest"],
        "latitude": 22.2812,
        "longitude": 114.1547,
    },
]
logger = logging.getLogger(__name__)


def _tokenize(text: str) -> set[str]:
    return {token.strip().lower() for token in text.split() if token.strip()}


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


def _approx_distance_meters(
    *, origin_latitude: float, origin_longitude: float, latitude: float, longitude: float
) -> int:
    # Equirectangular approximation is accurate enough for nearby HK urban ranges.
    meters_per_degree_lat = 111_320.0
    meters_per_degree_lng = 111_320.0 * math.cos(math.radians(origin_latitude))
    delta_lat = (latitude - origin_latitude) * meters_per_degree_lat
    delta_lng = (longitude - origin_longitude) * meters_per_degree_lng
    return max(1, int(round(math.sqrt((delta_lat * delta_lat) + (delta_lng * delta_lng)))))


def _format_distance_text(distance_meters: int) -> str:
    if distance_meters < 1000:
        rounded = max(50, int(round(distance_meters / 50.0) * 50))
        return f"{rounded} m"
    return f"{distance_meters / 1000:.1f} km"


def _format_walking_duration_text(distance_meters: int) -> str:
    # Approximate walking speed: 4.8 km/h => ~80 m/min.
    minutes = max(3, int(round(distance_meters / 80)))
    return f"{minutes} mins"


class RecommendationService:
    def __init__(
        self,
        provider_router: ProviderRouter | None = None,
        weather_service: WeatherService | None = None
    ):
        self._settings = settings
        self._provider_router = provider_router or ProviderRouter(settings)
        self._weather_service = weather_service or WeatherService(
            self._provider_router)

    def _coarse_user_location(self, *, latitude: float, longitude: float) -> tuple[str, str]:
        region = f"{latitude:.2f},{longitude:.2f}"
        token_length = max(
            6,
            min(24, self._settings.recommendation_user_location_geohash_precision * 2),
        )
        geohash_token = sha256(region.encode(
            "utf-8")).hexdigest()[:token_length]
        return geohash_token, region

    def _persist_recommendation_result(
        self,
        *,
        request: RecommendationRequest,
        response: RecommendationResponse,
        maps_provider_name: str,
        weather_provider_name: str,
    ) -> None:
        role_enum = RoleType(request.role)
        travel_mode = TravelMode(request.travel_mode)

        if self._settings.privacy_store_precise_user_location:
            user_location_region = f"{request.latitude:.6f},{request.longitude:.6f}"
            user_location_geohash = user_location_region
        else:
            user_location_geohash, user_location_region = self._coarse_user_location(
                latitude=request.latitude,
                longitude=request.longitude,
            )

        recommendation_status = (
            ProviderEventStatus.degraded
            if response.context.degraded
            else ProviderEventStatus.success
        )
        if (
            response.context.fallback_reason
            and "disabled_or_unavailable" in response.context.fallback_reason
        ):
            recommendation_status = ProviderEventStatus.fallback

        with SessionLocal() as session:
            user_repository = UserRepository(session)
            recommendation_repository = RecommendationRepository(session)
            audit_repository = AuditRepository(session)

            user_repository.ensure_user(request.user_id)
            recommendation_request = recommendation_repository.create_request(
                request_id=response.request_id,
                user_id=request.user_id,
                role=role_enum,
                query=request.query,
                max_results=request.max_results,
                preference_tags=request.preference_tags,
                travel_mode=travel_mode,
                user_location_geohash=user_location_geohash,
                user_location_region=user_location_region,
                context=response.context,
            )
            recommendation_repository.create_items(
                request_pk=recommendation_request.id,
                recommendations=response.recommendations,
            )

            audit_repository.create_provider_event(
                user_id=request.user_id,
                request_id=response.request_id,
                role=role_enum,
                scope=ProviderEventScope.maps,
                provider_name=maps_provider_name,
                runtime=None,
                status=recommendation_status,
                fallback_reason=response.context.fallback_reason,
                metadata_json={"result_count": len(response.recommendations)},
            )
            weather_status = (
                ProviderEventStatus.degraded
                if response.context.degraded and weather_provider_name == "stub"
                else ProviderEventStatus.success
            )
            audit_repository.create_provider_event(
                user_id=request.user_id,
                request_id=response.request_id,
                role=role_enum,
                scope=ProviderEventScope.weather,
                provider_name=weather_provider_name,
                runtime=None,
                status=weather_status,
                fallback_reason=response.context.fallback_reason,
                metadata_json={
                    "weather_condition": response.context.weather_condition,
                    "temperature_c": response.context.temperature_c,
                },
            )
            audit_repository.create_audit_event(
                event_type=AuditEventType.recommendation_request,
                user_id=request.user_id,
                request_id=response.request_id,
                role=role_enum,
                message="Recommendation request persisted",
                metadata_json={
                    "result_count": len(response.recommendations),
                    "degraded": response.context.degraded,
                    "user_location_region": user_location_region,
                },
            )
            session.commit()

    def _build_search_queries(self, query: str) -> list[str]:
        queries = [query.strip()]
        lowered = query.lower()
        for fallback in _FALLBACK_DISCOVERY_QUERIES:
            if fallback not in lowered:
                queries.append(f"{fallback} near me")
        return queries

    def _weather_fit_score(self, *, condition: str, place_types: list[str]) -> float:
        type_set = {place_type.lower() for place_type in place_types}
        if condition in _WEATHER_INDOOR_CONDITIONS:
            return 1.0 if type_set.intersection(_INDOOR_PLACE_TYPES) else 0.45
        if condition in {"clear", "partly_cloudy"}:
            return 1.0 if type_set.intersection(_OUTDOOR_PLACE_TYPES) else 0.6
        return 0.7

    def _preference_score(self, *, preference_tags: list[str], place_name: str, place_types: list[str]) -> float:
        if not preference_tags:
            return 0.5
        haystack = f"{place_name.lower()} {' '.join(place_types).lower()}"
        matches = sum(1 for tag in preference_tags if tag.lower() in haystack)
        return _clamp_score(matches / max(1, len(preference_tags)))

    def _query_relevance_score(self, *, query: str, place_name: str, place_types: list[str]) -> float:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return 0.0
        haystack = f"{place_name.lower()} {' '.join(place_types).lower()}"
        overlaps = sum(1 for token in query_tokens if token in haystack)
        return _clamp_score(overlaps / len(query_tokens))

    def _distance_score(self, *, distance_meters: int | None) -> float:
        if distance_meters is None:
            return 0.4
        if distance_meters <= 1000:
            return 1.0
        return _clamp_score(1 - (distance_meters / 12000))

    def _rating_score(self, *, rating: float | None) -> float:
        if rating is None:
            return 0.35
        return _clamp_score(rating / 5.0)

    def _review_volume_score(self, *, review_count: int | None) -> float:
        if not review_count:
            return 0.1
        return _clamp_score(math.log10(review_count + 1) / 3)

    def _total_fit_score(
        self,
        *,
        query: str,
        place_name: str,
        place_types: list[str],
        rating: float | None,
        review_count: int | None,
        distance_meters: int | None,
        condition: str,
        preference_tags: list[str]
    ) -> float:
        relevance = self._query_relevance_score(
            query=query,
            place_name=place_name,
            place_types=place_types
        )
        rating_score = self._rating_score(rating=rating)
        review_score = self._review_volume_score(review_count=review_count)
        distance_score = self._distance_score(distance_meters=distance_meters)
        weather_score = self._weather_fit_score(
            condition=condition, place_types=place_types)
        preference_score = self._preference_score(
            preference_tags=preference_tags,
            place_name=place_name,
            place_types=place_types
        )

        score = (
            (0.25 * relevance) +
            (0.20 * rating_score) +
            (0.15 * review_score) +
            (0.20 * distance_score) +
            (0.10 * weather_score) +
            (0.10 * preference_score)
        )
        return round(_clamp_score(score), 4)

    def _build_rationale(
        self,
        *,
        condition: str,
        place_types: list[str],
        rating: float | None,
        distance_text: str | None,
        duration_text: str | None,
        query: str
    ) -> str:
        reasons: list[str] = []
        if rating and rating >= 4.2:
            reasons.append("strong review score")
        if distance_text and duration_text:
            reasons.append(f"about {distance_text} away ({duration_text})")
        elif distance_text:
            reasons.append(f"about {distance_text} away")

        type_set = {place_type.lower() for place_type in place_types}
        if condition in _WEATHER_INDOOR_CONDITIONS and type_set.intersection(_INDOOR_PLACE_TYPES):
            reasons.append("indoor-friendly for current weather")
        elif condition in {"clear", "partly_cloudy"} and type_set.intersection(_OUTDOOR_PLACE_TYPES):
            reasons.append("great fit for outdoor weather")

        if not reasons:
            reasons.append("balanced option near your current area")

        return f"Matches '{query}' with {', '.join(reasons)}."

    def _fallback_recommendations(
        self,
        *,
        latitude: float,
        longitude: float,
        query: str
    ) -> list[RecommendationItem]:
        ranked: list[tuple[float, dict[str, Any], int]] = []
        for place in _HK_FALLBACK_PLACE_CATALOG:
            distance_meters = _approx_distance_meters(
                origin_latitude=latitude,
                origin_longitude=longitude,
                latitude=float(place["latitude"]),
                longitude=float(place["longitude"]),
            )
            query_score = self._query_relevance_score(
                query=query,
                place_name=str(place["name"]),
                place_types=[str(t) for t in list(place["types"])],
            )
            distance_score = self._distance_score(distance_meters=distance_meters)
            composite = _clamp_score((0.65 * query_score) + (0.35 * distance_score))
            ranked.append((round(composite, 4), place, distance_meters))

        ranked.sort(key=lambda item: item[0], reverse=True)
        top_candidates = ranked[:5]

        recommendations: list[RecommendationItem] = []
        for score, place, distance_meters in top_candidates:
            query_str = quote_plus(f"{place['name']} {place['address']}")
            recommendations.append(
                RecommendationItem(
                    place_id=str(place["place_id"]),
                    name=str(place["name"]),
                    address=str(place["address"]),
                    rating=None,
                    user_ratings_total=None,
                    types=[str(t) for t in list(place["types"])],
                    location=Coordinates(
                        latitude=float(place["latitude"]),
                        longitude=float(place["longitude"]),
                    ),
                    photo_url=None,
                    maps_uri=f"https://www.google.com/maps/search/?api=1&query={query_str}",
                    distance_text=_format_distance_text(distance_meters),
                    duration_text=_format_walking_duration_text(distance_meters),
                    fit_score=max(0.35, score),
                    rationale=(
                        f"Known Hong Kong option matched to '{query}' while live place data is limited."
                    ),
                )
            )
        return recommendations

    def get_history(
        self,
        *,
        user_id: str,
        role: str,
        request_ids: list[str],
    ) -> RecommendationHistoryResponse:
        if not request_ids:
            return RecommendationHistoryResponse(results=[])
        role_enum = RoleType(role)
        with SessionLocal() as session:
            recommendation_repository = RecommendationRepository(session)
            rows = recommendation_repository.list_requests_by_ids(
                user_id=user_id,
                role=role_enum,
                request_ids=request_ids,
            )

        rows_by_request_id = {row.request_id: row for row in rows}
        results: list[RecommendationResponse] = []
        for request_id in request_ids:
            row = rows_by_request_id.get(request_id)
            if row is None:
                continue
            items = sorted(row.items, key=lambda item: item.fit_score, reverse=True)
            recommendations = [
                RecommendationItem(
                    place_id=item.place_id,
                    name=item.name,
                    address=item.address,
                    rating=item.rating,
                    user_ratings_total=item.user_ratings_total,
                    types=item.types,
                    location=Coordinates(
                        latitude=item.place_latitude,
                        longitude=item.place_longitude,
                    ),
                    photo_url=item.photo_url,
                    maps_uri=item.maps_uri,
                    distance_text=item.distance_text,
                    duration_text=item.duration_text,
                    fit_score=item.fit_score,
                    rationale=item.rationale,
                )
                for item in items
            ]
            results.append(
                RecommendationResponse(
                    request_id=row.request_id,
                    recommendations=recommendations,
                    context=RecommendationContext(
                        weather_condition=row.weather_condition or "unknown",
                        temperature_c=row.temperature_c,
                        degraded=row.degraded,
                        fallback_reason=row.fallback_reason,
                    ),
                )
            )
        return RecommendationHistoryResponse(results=results)

    def generate_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        max_results = max(3, min(5, request.max_results))
        maps_provider = self._provider_router.resolve_maps_provider()
        weather_response = self._weather_service.get_current_weather(
            latitude=request.latitude,
            longitude=request.longitude,
            timezone="auto"
        )

        deduplicated_places: dict[str, dict[str, Any]] = {}
        for query in self._build_search_queries(request.query):
            candidates = maps_provider.search_places(
                query=query,
                latitude=request.latitude,
                longitude=request.longitude,
                radius_meters=settings.google_maps_default_radius_meters,
                language=settings.google_maps_language,
                max_results=max_results * 2
            )
            for place in candidates:
                place_id = str(place.get("place_id") or "")
                dedupe_key = place_id or f"{place.get('name')}-{place.get('address')}"
                if dedupe_key not in deduplicated_places:
                    deduplicated_places[dedupe_key] = place
            if len(deduplicated_places) >= max_results * 2:
                break

        live_candidate_count = len(deduplicated_places)
        scored_items: list[RecommendationItem] = []
        weather_condition = weather_response.weather.condition
        for place in deduplicated_places.values():
            destination_latitude = float(
                place.get("latitude", request.latitude))
            destination_longitude = float(
                place.get("longitude", request.longitude))
            route = maps_provider.get_route(
                origin_latitude=request.latitude,
                origin_longitude=request.longitude,
                destination_latitude=destination_latitude,
                destination_longitude=destination_longitude,
                travel_mode=request.travel_mode
            )
            distance_meters = None if route is None else route.get(
                "distance_meters")
            distance_text = None if route is None else route.get(
                "distance_text")
            duration_text = None if route is None else route.get(
                "duration_text")

            place_types = [str(value)
                           for value in list(place.get("types") or [])]
            rating = place.get("rating")
            review_count = place.get("user_ratings_total")
            fit_score = self._total_fit_score(
                query=request.query,
                place_name=str(place.get("name", "")),
                place_types=place_types,
                rating=None if rating is None else float(rating),
                review_count=None if review_count is None else int(
                    review_count),
                distance_meters=None if distance_meters is None else int(
                    distance_meters),
                condition=weather_condition,
                preference_tags=request.preference_tags
            )

            scored_items.append(
                RecommendationItem(
                    place_id=str(place.get("place_id") or ""),
                    name=str(place.get("name", "Unknown place")),
                    address=str(place.get("address", "Address unavailable")),
                    rating=None if rating is None else float(rating),
                    user_ratings_total=None if review_count is None else int(
                        review_count),
                    types=place_types,
                    location=Coordinates(
                        latitude=destination_latitude,
                        longitude=destination_longitude
                    ),
                    photo_url=(
                        None
                        if place.get("photo_url") is None
                        else str(place.get("photo_url"))
                    ),
                    maps_uri=(
                        None
                        if place.get("maps_uri") is None
                        else str(place.get("maps_uri"))
                    ),
                    distance_text=None if distance_text is None else str(
                        distance_text),
                    duration_text=None if duration_text is None else str(
                        duration_text),
                    fit_score=fit_score,
                    rationale=self._build_rationale(
                        condition=weather_condition,
                        place_types=place_types,
                        rating=None if rating is None else float(rating),
                        distance_text=None if distance_text is None else str(
                            distance_text),
                        duration_text=None if duration_text is None else str(
                            duration_text),
                        query=request.query
                    )
                )
            )

        scored_items.sort(key=lambda item: item.fit_score, reverse=True)
        recommendations = scored_items[:max_results]

        degraded = weather_response.degraded
        fallback_reason = weather_response.fallback_reason
        if maps_provider.provider_name == "maps-stub":
            degraded = True
            fallback_reason = "maps_provider_disabled_or_unavailable"

        if len(recommendations) < 3:
            degraded = True
            fallback_reason = fallback_reason or (
                "live_place_search_empty" if live_candidate_count == 0 else "insufficient_live_place_results"
            )
            recommendations = self._fallback_recommendations(
                latitude=request.latitude,
                longitude=request.longitude,
                query=request.query
            )[:max_results]

        request_id = request.chat_request_id or str(uuid4())
        response = RecommendationResponse(
            request_id=request_id,
            recommendations=recommendations,
            context=RecommendationContext(
                weather_condition=weather_condition,
                temperature_c=weather_response.weather.temperature_c,
                degraded=degraded,
                fallback_reason=fallback_reason
            )
        )
        try:
            self._persist_recommendation_result(
                request=request,
                response=response,
                maps_provider_name=maps_provider.provider_name,
                weather_provider_name=weather_response.weather.source,
            )
        except Exception:
            logger.exception(
                "recommendation_persistence_failed request_id=%s user_id=%s role=%s",
                response.request_id,
                request.user_id,
                request.role,
            )
        return response
