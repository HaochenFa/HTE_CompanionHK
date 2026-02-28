"use client";

import { use } from "react";
import { redirect } from "next/navigation";
import { ChatShell } from "@/features/chat/chat-shell";
import { useAuth } from "@/lib/auth-context";
import type { Role } from "@/features/chat/types";

const VALID_ROLES: Role[] = ["companion", "local_guide", "study_guide"];

export default function ChatPage({ params }: { params: Promise<{ role: string }> }) {
  const { role } = use(params);
  const { user, isLoading } = useAuth();

  if (!isLoading && !user) redirect("/login");
  if (!VALID_ROLES.includes(role as Role)) redirect("/");

  if (isLoading) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-background">
        <div className="size-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-dvh flex flex-col bg-background">
      <ChatShell initialRole={role as Role} userId={user!.username} />
    </div>
  );
}
