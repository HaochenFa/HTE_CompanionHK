"use client";

import { use } from "react";
import { redirect } from "next/navigation";
import { ChatShell } from "@/features/chat/chat-shell";
import { useAuth } from "@/lib/auth-context";
import { slugToRole } from "@/features/chat/role-routing";

export default function ChatPage({ params }: { params: Promise<{ role: string }> }) {
  const { role } = use(params);
  const { user, isLoading } = useAuth();
  const initialRole = slugToRole(role);

  if (!isLoading && !user) redirect("/welcome");
  if (!initialRole) redirect("/");

  if (isLoading) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-background">
        <div className="size-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-dvh flex flex-col bg-background">
      <ChatShell initialRole={initialRole} userId={user!.username} />
    </div>
  );
}
