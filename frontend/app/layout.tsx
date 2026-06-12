import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WorldCup AI — אנליסט משחקים",
  description: "חיזוי וניתוח משחקי מונדיאל בעברית על בסיס נתונים אמיתיים",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="he" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
