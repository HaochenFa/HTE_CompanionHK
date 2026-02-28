import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ChatShell } from "@/features/chat/chat-shell";
import * as chatApi from "@/lib/api/chat";
import * as recommendationApi from "@/lib/api/recommendations";

vi.mock("@/lib/api/chat", () => ({
  postChatMessage: vi.fn(),
  getChatHistory: vi.fn(),
}));

vi.mock("@/lib/api/recommendations", () => ({
  postRecommendations: vi.fn(),
  postRecommendationHistory: vi.fn(),
}));

vi.mock("@/components/weather-provider", () => ({
  useWeather: () => ({ condition: "unknown", isDay: true, temperatureC: null }),
  WeatherProvider: ({ children }: { children: React.ReactNode }) => children,
}));

describe("recommendation integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(chatApi.getChatHistory).mockImplementation(async ({ user_id, role, thread_id }) => ({
      user_id,
      role,
      thread_id: thread_id ?? `${user_id}-${role}-thread`,
      turns: [],
    }));
    vi.mocked(recommendationApi.postRecommendationHistory).mockResolvedValue({ results: [] });
    vi.mocked(chatApi.postChatMessage).mockResolvedValue({
      request_id: "local-guide-reply",
      thread_id: "demo-user-local_guide-thread",
      runtime: "simple",
      provider: "mock",
      reply: "Here are practical options for your route.",
      safety: {
        risk_level: "low",
        show_crisis_banner: false,
      },
    });
    vi.mocked(recommendationApi.postRecommendations).mockResolvedValue({
      request_id: "recommendation-request-1",
      recommendations: [
        {
          place_id: "place-1",
          name: "Harbour Cafe",
          address: "Tsim Sha Tsui, Hong Kong",
          rating: 4.6,
          user_ratings_total: 812,
          types: ["cafe", "food"],
          location: { latitude: 22.296, longitude: 114.172 },
          photo_url: null,
          maps_uri: "https://maps.google.com",
          distance_text: "1.2 km",
          duration_text: "16 mins",
          fit_score: 0.85,
          rationale: "Good review quality and close distance for your route.",
        },
        {
          place_id: "place-2",
          name: "Waterfront Park",
          address: "Tsim Sha Tsui, Hong Kong",
          rating: 4.4,
          user_ratings_total: 501,
          types: ["park", "point_of_interest"],
          location: { latitude: 22.294, longitude: 114.171 },
          photo_url: null,
          maps_uri: null,
          distance_text: "1.6 km",
          duration_text: "20 mins",
          fit_score: 0.74,
          rationale: "Outdoor option with practical travel time.",
        },
        {
          place_id: "place-3",
          name: "City Museum",
          address: "Tsim Sha Tsui, Hong Kong",
          rating: 4.2,
          user_ratings_total: 388,
          types: ["museum", "point_of_interest"],
          location: { latitude: 22.293, longitude: 114.173 },
          photo_url: null,
          maps_uri: null,
          distance_text: "2.0 km",
          duration_text: "24 mins",
          fit_score: 0.7,
          rationale: "Indoor alternative in case weather shifts.",
        },
      ],
      context: {
        weather_condition: "cloudy",
        temperature_c: 26,
        degraded: false,
        fallback_reason: null,
      },
    });
  });

  it("renders recommendation cards in local guide flow", async () => {
    render(<ChatShell />);
    fireEvent.click(screen.getByRole("button", { name: /Local Guide/i }));
    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "Plan a route with a cafe and a nearby park." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(recommendationApi.postRecommendations).toHaveBeenCalledTimes(1);
    });
    expect(vi.mocked(recommendationApi.postRecommendations).mock.calls[0]?.[0]).toMatchObject({
      chat_request_id: "local-guide-reply",
    });
    expect(await screen.findByText("Local Recommendations")).toBeInTheDocument();
    expect(await screen.findByText("Harbour Cafe")).toBeInTheDocument();
  });

  it("switches recommendation panel to newest assistant turn", async () => {
    vi.mocked(chatApi.postChatMessage)
      .mockResolvedValueOnce({
        request_id: "turn-1",
        thread_id: "demo-user-local_guide-thread",
        runtime: "simple",
        provider: "mock",
        reply: "Here are options for your first request.",
        safety: { risk_level: "low", show_crisis_banner: false },
      })
      .mockResolvedValueOnce({
        request_id: "turn-2",
        thread_id: "demo-user-local_guide-thread",
        runtime: "simple",
        provider: "mock",
        reply: "Updated route options for your new request.",
        safety: { risk_level: "low", show_crisis_banner: false },
      });
    vi.mocked(recommendationApi.postRecommendations)
      .mockResolvedValueOnce({
        request_id: "turn-1",
        recommendations: [
          {
            place_id: "first-place",
            name: "First Cafe",
            address: "Central, Hong Kong",
            rating: 4.1,
            user_ratings_total: 100,
            types: ["cafe"],
            location: { latitude: 22.281, longitude: 114.158 },
            photo_url: null,
            maps_uri: null,
            distance_text: "1.0 km",
            duration_text: "14 mins",
            fit_score: 0.7,
            rationale: "First set.",
          },
        ],
        context: {
          weather_condition: "cloudy",
          temperature_c: 26,
          degraded: false,
          fallback_reason: null,
        },
      })
      .mockResolvedValueOnce({
        request_id: "turn-2",
        recommendations: [
          {
            place_id: "second-place",
            name: "Second Park",
            address: "Wan Chai, Hong Kong",
            rating: 4.4,
            user_ratings_total: 220,
            types: ["park"],
            location: { latitude: 22.279, longitude: 114.169 },
            photo_url: null,
            maps_uri: null,
            distance_text: "1.4 km",
            duration_text: "19 mins",
            fit_score: 0.82,
            rationale: "Second set.",
          },
        ],
        context: {
          weather_condition: "clear",
          temperature_c: 27,
          degraded: false,
          fallback_reason: null,
        },
      });

    render(<ChatShell />);
    fireEvent.click(screen.getByRole("button", { name: /Local Guide/i }));

    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "First request" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(await screen.findByText("First Cafe")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "Second request" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("Second Park")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText("First Cafe")).not.toBeInTheDocument();
    });
  });

  it("loads missing linked recommendations when selecting a historical turn", async () => {
    vi.mocked(chatApi.getChatHistory).mockResolvedValue({
      user_id: "demo-user",
      role: "local_guide",
      thread_id: "demo-user-local_guide-thread",
      turns: [
        {
          request_id: "turn-1",
          thread_id: "demo-user-local_guide-thread",
          created_at: "2026-02-28T14:00:00Z",
          user_message: "parks near hung hom",
          assistant_reply: "Here are some nearby options.",
          safety: { risk_level: "low", show_crisis_banner: false },
        },
        {
          request_id: "turn-2",
          thread_id: "demo-user-local_guide-thread",
          created_at: "2026-02-28T14:02:00Z",
          user_message: "cafes near tsim sha tsui",
          assistant_reply: "Updated route ideas for cafe hopping.",
          safety: { risk_level: "low", show_crisis_banner: false },
        },
      ],
    });
    vi.mocked(recommendationApi.postRecommendationHistory).mockResolvedValue({
      results: [
        {
          request_id: "turn-2",
          recommendations: [
            {
              place_id: "history-place",
              name: "History Park",
              address: "Hung Hom, Hong Kong",
              rating: null,
              user_ratings_total: null,
              types: ["park"],
              location: { latitude: 22.302, longitude: 114.182 },
              photo_url: null,
              maps_uri: null,
              distance_text: "800 m",
              duration_text: "10 mins",
              fit_score: 0.6,
              rationale: "From history.",
            },
          ],
          context: {
            weather_condition: "cloudy",
            temperature_c: 24,
            degraded: false,
            fallback_reason: null,
          },
        },
      ],
    });
    vi.mocked(recommendationApi.postRecommendations).mockResolvedValueOnce({
      request_id: "turn-1",
      recommendations: [
        {
          place_id: "lazy-place",
          name: "Lazy Loaded Cafe",
          address: "Hung Hom, Hong Kong",
          rating: 4.0,
          user_ratings_total: 100,
          types: ["cafe"],
          location: { latitude: 22.304, longitude: 114.184 },
          photo_url: null,
          maps_uri: null,
          distance_text: "1.1 km",
          duration_text: "14 mins",
          fit_score: 0.66,
          rationale: "Loaded on selection.",
        },
      ],
      context: {
        weather_condition: "cloudy",
        temperature_c: 24,
        degraded: false,
        fallback_reason: null,
      },
    });

    render(<ChatShell initialRole="local_guide" />);

    expect(await screen.findByText("History Park")).toBeInTheDocument();
    fireEvent.click(await screen.findByRole("button", { name: /parks near hung hom/i }));

    await waitFor(() => {
      expect(recommendationApi.postRecommendations).toHaveBeenCalledWith(
        expect.objectContaining({
          query: "parks near hung hom",
          chat_request_id: "turn-1",
        }),
      );
    });
    expect(await screen.findByText("Lazy Loaded Cafe")).toBeInTheDocument();
  });
});
