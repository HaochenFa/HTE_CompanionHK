export type RiskLevel = "low" | "medium" | "high";
export type Role = "companion" | "local_guide" | "study_guide";

export interface SafetyMetadata {
  risk_level: RiskLevel;
  show_crisis_banner: boolean;
  emotion_label?: string | null;
  emotion_score?: number | null;
  policy_action?: "allow" | "supportive_refusal" | "escalate_banner";
  monitor_provider?: "minimax" | "rules";
  degraded?: boolean;
  fallback_reason?: string | null;
}

export interface ChatRequest {
  user_id: string;
  role: Role;
  thread_id?: string;
  message: string;
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
