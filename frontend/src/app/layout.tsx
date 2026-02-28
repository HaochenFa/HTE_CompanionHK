import type { Metadata } from "next";
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
        <CompanionThemeProvider>{children}</CompanionThemeProvider>
      </body>
    </html>
  );
}
