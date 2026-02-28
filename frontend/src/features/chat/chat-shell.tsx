"use client";

import { useRef, useState } from "react";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { postChatMessage } from "@/lib/api/chat";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
};

export function ChatShell() {
  const userId = "demo-user";
  const threadIdRef = useRef("demo-user-main-thread");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isSubmitting) {
      return;
    }

    setError(null);
    setInput("");
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      text: trimmed,
    };
    setMessages((previous) => [...previous, userMessage]);
    setIsSubmitting(true);

    try {
      const response = await postChatMessage({
        user_id: userId,
        thread_id: threadIdRef.current,
        message: trimmed,
      });
      const assistantMessage: ChatMessage = {
        id: response.request_id,
        role: "assistant",
        text: response.reply,
      };
      setMessages((previous) => [...previous, assistantMessage]);
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
        A supportive chat shell with adapter-ready backend integration.
      </Typography>

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
        {messages.length === 0 && (
          <Typography sx={{ color: "text.secondary" }}>
            Start by sharing how you are feeling today.
          </Typography>
        )}
        {messages.map((message) => (
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
