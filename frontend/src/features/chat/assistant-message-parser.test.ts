import { describe, expect, it } from "vitest";
import { parseAssistantMessage } from "@/features/chat/assistant-message-parser";

describe("parseAssistantMessage", () => {
  it("extracts collapsed reasoning from think blocks", () => {
    const raw = "<think>hidden chain</think>\n\nFinal answer in markdown";
    const parsed = parseAssistantMessage(raw);
    expect(parsed.thinking).toBe("hidden chain");
    expect(parsed.finalAnswer).toBe("Final answer in markdown");
  });

  it("returns original content when no think block exists", () => {
    const parsed = parseAssistantMessage("Normal response");
    expect(parsed.thinking).toBeNull();
    expect(parsed.finalAnswer).toBe("Normal response");
  });
});
