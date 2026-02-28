"use client";

import { SyntheticEvent, useRef, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import type { Role } from "@/features/chat/types";
import { postChatMessage } from "@/lib/api/chat";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
};

const ROLE_OPTIONS: Role[] = ["companion", "local_guide", "study_guide"];

const ROLE_LABELS: Record<Role, string> = {
  companion: "Companion",
  local_guide: "Local Guide",
  study_guide: "Study Guide",
};

const ROLE_DESCRIPTIONS: Record<Role, string> = {
  companion: "Share how you feel and get supportive daily companionship.",
  local_guide: "Ask about places, routes, neighborhoods, and local options.",
  study_guide: "Plan study sessions, break down topics, and review concepts.",
};

const ROLE_EMPTY_STATE: Record<Role, string> = {
  companion: "Start by sharing how you are feeling today.",
  local_guide: "Tell me what area or activity you want to explore.",
  study_guide: "Share what you want to study and your timeline.",
};

function buildInitialThreadMap(userId: string): Record<Role, string> {
  return {
    companion: `${userId}-companion-thread`,
    local_guide: `${userId}-local_guide-thread`,
    study_guide: `${userId}-study_guide-thread`,
  };
}

function buildInitialMessageMap(): Record<Role, ChatMessage[]> {
  return {
    companion: [],
    local_guide: [],
    study_guide: [],
  };
}

export function ChatShell() {
  const userId = "demo-user";
  const [activeRole, setActiveRole] = useState<Role>("companion");
  const threadIdRef = useRef<Record<Role, string>>(buildInitialThreadMap(userId));
  const [messagesByRole, setMessagesByRole] =
    useState<Record<Role, ChatMessage[]>>(buildInitialMessageMap());
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const activeMessages = messagesByRole[activeRole];

  const handleRoleChange = (_event: SyntheticEvent, nextRole: Role) => {
    setActiveRole(nextRole);
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isSubmitting) {
      return;
    }

    const roleAtSend = activeRole;
    const threadIdAtSend = threadIdRef.current[roleAtSend];
    setError(null);
    setInput("");
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      text: trimmed,
    };
    setMessagesByRole((previous) => ({
      ...previous,
      [roleAtSend]: [...previous[roleAtSend], userMessage],
    }));
    setIsSubmitting(true);

    try {
      const response = await postChatMessage({
        user_id: userId,
        role: roleAtSend,
        thread_id: threadIdAtSend,
        message: trimmed,
      });
      const assistantMessage: ChatMessage = {
        id: response.request_id,
        role: "assistant",
        text: response.reply,
      };
      setMessagesByRole((previous) => ({
        ...previous,
        [roleAtSend]: [...previous[roleAtSend], assistantMessage],
      }));
    } catch (chatError) {
      setError(chatError instanceof Error ? chatError.message : "Unable to send message.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Stack spacing={2}>
      <Typography variant="h4" sx={{ fontWeight: 700 }}>
        CompanionHK Chat
      </Typography>
      <Typography sx={{ color: "text.secondary" }}>
        Choose a role space to switch context between companionship, local guidance, and study help.
      </Typography>
      <Tabs
        value={activeRole}
        onChange={handleRoleChange}
        variant="fullWidth"
        aria-label="Role spaces"
      >
        {ROLE_OPTIONS.map((roleOption) => (
          <Tab key={roleOption} value={roleOption} label={ROLE_LABELS[roleOption]} />
        ))}
      </Tabs>
      <Typography sx={{ color: "text.secondary" }}>{ROLE_DESCRIPTIONS[activeRole]}</Typography>

      {error && <Alert severity="error">{error}</Alert>}

      <Paper
        variant="outlined"
        sx={{
          p: 2,
          borderRadius: 3,
          minHeight: 320,
          display: "flex",
          flexDirection: "column",
          gap: 1.25,
        }}
      >
        {activeMessages.length === 0 && (
          <Typography sx={{ color: "text.secondary" }}>{ROLE_EMPTY_STATE[activeRole]}</Typography>
        )}
        {activeMessages.map((message) => (
          <Box
            key={message.id}
            sx={{
              maxWidth: "85%",
              alignSelf: message.role === "user" ? "flex-end" : "flex-start",
              bgcolor: message.role === "user" ? "primary.main" : "grey.100",
              color: message.role === "user" ? "primary.contrastText" : "text.primary",
              px: 1.5,
              py: 1,
              borderRadius: 2,
            }}
          >
            <Typography>{message.text}</Typography>
          </Box>
        ))}
      </Paper>

      <Stack direction="row" spacing={1}>
        <TextField
          fullWidth
          label="Message input"
          value={input}
          disabled={isSubmitting}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void handleSend();
            }
          }}
        />
        <Button
          variant="contained"
          onClick={() => void handleSend()}
          disabled={isSubmitting || input.trim().length === 0}
        >
          Send
        </Button>
      </Stack>
    </Stack>
  );
}
