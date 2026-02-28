import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ChatShell } from "@/features/chat/chat-shell";
import * as chatApi from "@/lib/api/chat";

vi.mock("@/lib/api/chat", () => ({
  postChatMessage: vi.fn(),
}));

describe("ChatShell", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("submits a message and renders the assistant response", async () => {
    vi.mocked(chatApi.postChatMessage).mockResolvedValue({
      request_id: "test-request",
      thread_id: "demo-user-main-thread",
      runtime: "simple",
      provider: "mock",
      reply: "I am here with you.",
      safety: {
        risk_level: "low",
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
        thread_id: "demo-user-main-thread",
        message: "Today feels difficult.",
      });
    });

    expect(await screen.findByText("I am here with you.")).toBeInTheDocument();
  });
});
