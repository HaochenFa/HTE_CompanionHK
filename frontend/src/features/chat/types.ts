export type Role = "companion" | "local_guide" | "study_guide";

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
  safety: {
    show_crisis_banner: boolean;
  };
}
