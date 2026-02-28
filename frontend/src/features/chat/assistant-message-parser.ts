export interface ParsedAssistantMessage {
  finalAnswer: string;
  thinking: string | null;
}

const THINK_BLOCK_PATTERN = /<think>([\s\S]*?)<\/think>/i;

export function parseAssistantMessage(rawMessage: string): ParsedAssistantMessage {
  const raw = rawMessage ?? "";
  const thinkMatch = THINK_BLOCK_PATTERN.exec(raw);
  const thinking = thinkMatch?.[1]?.trim() || null;

  let finalAnswer = raw;
  if (thinkMatch) {
    finalAnswer =
      raw.slice(0, thinkMatch.index) + raw.slice(thinkMatch.index + thinkMatch[0].length);
  }

  finalAnswer = finalAnswer.trim();
  if (!finalAnswer && thinking) {
    finalAnswer = raw.replace(/<\/?think>/gi, "").trim();
  }

  return {
    finalAnswer: finalAnswer || raw.trim(),
    thinking,
  };
}
