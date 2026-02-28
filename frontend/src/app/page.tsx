import { Box, Paper } from "@mui/material";
import { ChatShell } from "@/features/chat/chat-shell";

export default function Home() {
  return (
    <Box sx={{ display: "flex", justifyContent: "center", p: 3 }}>
      <Paper
        elevation={0}
        sx={{
          width: "100%",
          maxWidth: 900,
          p: 3,
          borderRadius: 3,
          border: "1px solid",
          borderColor: "divider",
        }}
      >
        <ChatShell />
      </Paper>
    </Box>
  );
}
