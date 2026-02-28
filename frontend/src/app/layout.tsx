import type { Metadata } from "next";
import "./globals.css";
import { CompanionThemeProvider } from "@/theme/theme-provider";

export const metadata: Metadata = {
  title: "CompanionHK",
  description: "Supportive AI friend for Hong Kong users",
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
