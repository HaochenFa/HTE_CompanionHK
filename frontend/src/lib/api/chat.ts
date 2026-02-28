import type {
  ChatHistoryResponse,
  ChatRequest,
  ChatResponse,
  ClearHistoryResponse,
  Role,
} from "@/features/chat/types";
import { apiBaseUrl } from "@/lib/api/base-url";

const API_BASE_URL = apiBaseUrl();
const ROLE_CHAT_PATH: Record<Role, string> = {
  companion: "chat/companion",
  local_guide: "chat/guide",
  study_guide: "chat/study",
};
const ROLE_HISTORY_PATH: Record<Role, string> = {
  companion: "chat/companion/history",
  local_guide: "chat/guide/history",
  study_guide: "chat/study/history",
};

export async function postChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const body: Record<string, unknown> = {
    user_id: payload.user_id,
    thread_id: payload.thread_id,
    message: payload.message,
  };
  if (payload.attachment) {
    body.attachment = payload.attachment;
  }

  const response = await fetch(`${API_BASE_URL}/${ROLE_CHAT_PATH[payload.role]}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  return (await response.json()) as ChatResponse;
}

export async function getChatHistory(params: {
  user_id: string;
  role: Role;
  thread_id?: string;
  limit?: number;
}): Promise<ChatHistoryResponse> {
  const queryParams = new URLSearchParams();
  queryParams.set("user_id", params.user_id);
  if (params.thread_id) queryParams.set("thread_id", params.thread_id);
  if (params.limit != null) queryParams.set("limit", String(params.limit));
  const response = await fetch(
    `${API_BASE_URL}/${ROLE_HISTORY_PATH[params.role]}?${queryParams.toString()}`,
    {
      method: "GET",
      cache: "no-store",
    },
  );
  if (!response.ok) {
    throw new Error(`Chat history request failed with status ${response.status}`);
  }
  return (await response.json()) as ChatHistoryResponse;
}

export async function clearChatHistory(params: {
  user_id: string;
  role: Role;
  thread_id?: string;
}): Promise<ClearHistoryResponse> {
  const response = await fetch(`${API_BASE_URL}/${ROLE_HISTORY_PATH[params.role]}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({
      user_id: params.user_id,
      role: params.role,
      thread_id: params.thread_id,
    }),
  });
  if (!response.ok) {
    throw new Error(`Clear history request failed with status ${response.status}`);
  }
  return (await response.json()) as ClearHistoryResponse;
}
