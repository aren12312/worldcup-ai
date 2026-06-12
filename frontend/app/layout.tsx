import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WorldCup AI Analyst",
  description: "AI-powered World Cup match predictions and analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
