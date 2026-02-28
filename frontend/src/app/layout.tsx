import type { Metadata } from "next";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";
import "./globals.css";
import { CompanionThemeProvider } from "@/theme/theme-provider";

export const metadata: Metadata = {
  title: "CompanionHK",
  description:
    "Multi-role AI companion for Hong Kong users: Companion, Local Guide, and Study Guide.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          <CompanionThemeProvider>{children}</CompanionThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
