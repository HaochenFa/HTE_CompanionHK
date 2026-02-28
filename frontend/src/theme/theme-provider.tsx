"use client";

import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import type { PropsWithChildren } from "react";
import { companionTheme } from "./theme";

export function CompanionThemeProvider({ children }: PropsWithChildren) {
  return (
    <ThemeProvider theme={companionTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
