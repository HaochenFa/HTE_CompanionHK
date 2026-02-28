export type Role = "companion" | "local_guide" | "study_guide";

export type TTSProvider = "auto" | "elevenlabs" | "cantoneseai";

export interface SafetyMetadata {
  show_crisis_banner: boolean;
  emotion_label?: string | null;
  emotion_score?: number | null;
  policy_action?: "allow" | "supportive_refusal" | "escalate_banner";
  monitor_provider?: "minimax" | "rules";
  degraded?: boolean;
  fallback_reason?: string | null;
}

export interface ImageAttachment {
  mime_type: "image/jpeg" | "image/png" | "image/webp";
  base64_data: string;
  filename?: string;
  size_bytes?: number;
}

export interface ChatRequest {
  user_id: string;
  role: Role;
  thread_id?: string;
  message: string;
  attachment?: ImageAttachment;
}

export interface ChatResponse {
  request_id: string;
  thread_id: string;
  runtime: string;
  provider: string;
  reply: string;
  safety: SafetyMetadata;
}

export interface ChatHistoryTurn {
  request_id: string;
  thread_id: string;
  created_at: string;
  user_message: string;
  assistant_reply: string;
  safety: SafetyMetadata;
}

export interface ChatHistoryResponse {
  user_id: string;
  role: Role;
  thread_id: string;
  turns: ChatHistoryTurn[];
}

export interface ClearHistoryResponse {
  user_id: string;
  role: Role;
  cleared_thread_id: string;
  new_thread_id: string;
  cleared_message_count: number;
  cleared_memory_count: number;
  cleared_recommendation_count: number;
}
