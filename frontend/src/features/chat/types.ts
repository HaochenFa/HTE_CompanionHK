export type RiskLevel = "low" | "medium" | "high";

export interface ChatRequest {
  user_id: string;
  thread_id?: string;
  message: string;
}

export interface ChatResponse {
  request_id: string;
  thread_id: string;
  runtime: string;
  provider: string;
  reply: string;
  safety: {
    risk_level: RiskLevel;
    show_crisis_banner: boolean;
  };
}
