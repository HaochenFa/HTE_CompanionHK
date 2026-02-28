import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn(), replace: vi.fn(), refresh: vi.fn() }),
  usePathname: () => "/chat/companion",
  useSearchParams: () => new URLSearchParams(),
}));

describe("ChatShell", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(chatApi.getChatHistory).mockImplementation(async ({ user_id, role, thread_id }) => ({
      user_id,
      role,
      thread_id: thread_id ?? `${user_id}-${role}-thread`,
      turns: [],
    }));
    vi.mocked(recommendationApi.postRecommendations).mockResolvedValue({
      request_id: "recommendation-request",
      recommendations: [],
      context: {
        weather_condition: "unknown",
        temperature_c: null,
        degraded: false,
        fallback_reason: null,
      },
    });
    vi.mocked(recommendationApi.postRecommendationHistory).mockResolvedValue({
      results: [],
    });
  });

  it("submits a message and renders the assistant response", async () => {
    vi.mocked(chatApi.postChatMessage).mockResolvedValue({
      request_id: "test-request",
      thread_id: "demo-user-companion-thread",
      runtime: "simple",
      provider: "mock",
      reply: "I am here with you.",
      safety: {
        show_crisis_banner: false,
      },
    });

    render(<ChatShell />);
    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "Today feels difficult." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(chatApi.postChatMessage).toHaveBeenCalledWith({
        user_id: "demo-user",
        role: "companion",
        thread_id: "demo-user-companion-thread",
        message: "Today feels difficult.",
      });
    });

    expect(await screen.findByText("I am here with you.")).toBeInTheDocument();
  });

  it("uses local guide role and role-scoped thread after switching tabs", async () => {
    vi.mocked(chatApi.postChatMessage).mockResolvedValue({
      request_id: "local-guide-request",
      thread_id: "demo-user-local_guide-thread",
      runtime: "simple",
      provider: "mock",
      reply: "Try Sheung Wan and PMQ for this route.",
      safety: {
        show_crisis_banner: false,
      },
    });

    render(<ChatShell />);
    fireEvent.click(screen.getByRole("button", { name: /Local Guide/i }));
    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "I want a half-day walk plan." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(chatApi.postChatMessage).toHaveBeenCalledWith({
        user_id: "demo-user",
        role: "local_guide",
        thread_id: "demo-user-local_guide-thread",
        message: "I want a half-day walk plan.",
      });
    });
    await waitFor(() => {
      expect(recommendationApi.postRecommendations).toHaveBeenCalledWith({
        user_id: "demo-user",
        role: "local_guide",
        query: "I want a half-day walk plan.",
        latitude: 22.3193,
        longitude: 114.1694,
        chat_request_id: "local-guide-request",
        max_results: 5,
        travel_mode: "walking",
      });
    });
  });

  it("keeps message history isolated across role spaces", async () => {
    vi.mocked(chatApi.postChatMessage)
      .mockResolvedValueOnce({
        request_id: "companion-request",
        thread_id: "demo-user-companion-thread",
        runtime: "simple",
        provider: "mock",
        reply: "Companion space reply.",
        safety: {
          risk_level: "low",
          show_crisis_banner: false,
        },
      })
      .mockResolvedValueOnce({
        request_id: "local-guide-request",
        thread_id: "demo-user-local_guide-thread",
        runtime: "simple",
        provider: "mock",
        reply: "Local guide space reply.",
        safety: {
          risk_level: "low",
          show_crisis_banner: false,
        },
      });

    render(<ChatShell />);

    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "I feel nervous about tomorrow." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(await screen.findByText("Companion space reply.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Local Guide/i }));
    await waitFor(() => {
      const localLog = screen.getByRole("log", { name: /Local Guide conversation/i });
      expect(within(localLog).queryByText("Companion space reply.")).not.toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "Plan a quick evening route." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect((await screen.findAllByText("Local guide space reply.")).length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole("button", { name: /Companion/i }));
    expect(await screen.findByText("Companion space reply.")).toBeInTheDocument();
    await waitFor(() => {
      const companionLog = screen.getByRole("log", { name: /Companion conversation/i });
      expect(within(companionLog).queryByText("Local guide space reply.")).not.toBeInTheDocument();
    });
  });

  it("shows crisis banner per role without leaking to other role spaces", async () => {
    vi.mocked(chatApi.postChatMessage)
      .mockResolvedValueOnce({
        request_id: "risk-request",
        thread_id: "demo-user-companion-thread",
        runtime: "simple",
        provider: "mock",
        reply: "Please reach out for support right now.",
        safety: {
          risk_level: "high",
          show_crisis_banner: true,
          emotion_label: "sad",
          emotion_score: 0.9,
          policy_action: "supportive_refusal",
          monitor_provider: "rules",
          degraded: false,
          fallback_reason: null,
        },
      })
      .mockResolvedValueOnce({
        request_id: "safe-request",
        thread_id: "demo-user-local_guide-thread",
        runtime: "simple",
        provider: "mock",
        reply: "Try this walking route.",
        safety: {
          risk_level: "low",
          show_crisis_banner: false,
          emotion_label: "calm",
          emotion_score: 0.6,
          policy_action: "allow",
          monitor_provider: "rules",
          degraded: false,
          fallback_reason: null,
        },
      });

    render(<ChatShell />);

    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "I cannot go on." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(await screen.findByText("You are not alone")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Local Guide/i }));
    await waitFor(() => {
      expect(screen.queryByText("You are not alone")).not.toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText("Message input"), {
      target: { value: "Suggest evening plan." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => {
      expect(screen.queryByText("You are not alone")).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Companion/i }));
    expect(await screen.findByText("You are not alone")).toBeInTheDocument();
  });

  it("hydrates history from backend on load", async () => {
    vi.mocked(chatApi.getChatHistory).mockResolvedValue({
      user_id: "demo-user",
      role: "companion",
      thread_id: "demo-user-companion-thread",
      turns: [
        {
          request_id: "turn-1",
          thread_id: "demo-user-companion-thread",
          created_at: "2026-02-28T09:00:00Z",
          user_message: "Hello there",
          assistant_reply: "Hi, I am here with you.",
          safety: {
            risk_level: "low",
            show_crisis_banner: false,
          },
        },
      ],
    });

    render(<ChatShell />);

    expect(await screen.findByText("Hello there")).toBeInTheDocument();
    expect(await screen.findByText("Hi, I am here with you.")).toBeInTheDocument();
  });
});
