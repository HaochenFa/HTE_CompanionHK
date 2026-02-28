import type { TTSProvider } from "@/features/chat/types";
import { apiBaseUrl } from "@/lib/api/base-url";

const API_BASE_URL = apiBaseUrl();

export interface TTSRequest {
  text: string;
  language?: string;
  preferred_provider?: TTSProvider;
}

export interface TTSResponse {
  request_id: string;
  provider: string;
  audio_base64: string;
  mime_type: string;
  degraded: boolean;
  fallback_reason: string | null;
}

export async function postTTS(payload: TTSRequest): Promise<TTSResponse> {
  const response = await fetch(`${API_BASE_URL}/voice/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({
      text: payload.text,
      language: payload.language ?? "en",
      preferred_provider: payload.preferred_provider ?? "auto",
    }),
  });

  if (!response.ok) {
    throw new Error(`TTS request failed with status ${response.status}`);
  }

  return (await response.json()) as TTSResponse;
}
