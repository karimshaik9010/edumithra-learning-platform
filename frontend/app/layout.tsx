import "./globals.css";
import React from "react";
import { AuthProvider } from "../lib/auth";
import MainLayoutContent from "./MainLayoutContent";

export const metadata = {
  title: "EDUMITHRA -- AI Learning Copilot",
  description: "Personalized, AI-driven learning roadmap tracker and coding tutor.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground selection:bg-indigo-500/30">
        <AuthProvider>
          <MainLayoutContent>{children}</MainLayoutContent>
        </AuthProvider>
      </body>
    </html>
  );
}
