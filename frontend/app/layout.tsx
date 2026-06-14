import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "./providers";

const SITE = process.env.NEXT_PUBLIC_SITE_URL || "https://worldcup-ai-web-999264609001.us-central1.run.app";

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: {
    default: "WorldCup AI — אנליסט משחקי מונדיאל מבוסס AI",
    template: "%s | WorldCup AI",
  },
  description:
    "חיזוי וניתוח משחקי מונדיאל בעברית: מודל Dixon-Coles, סימולציית Monte Carlo, מנוע ערך מול השוק, השפעת שחקנים והסבר-AI מלא.",
  keywords: ["מונדיאל", "חיזוי כדורגל", "ניתוח כדורגל", "World Cup", "xG", "Monte Carlo", "AI"],
  applicationName: "WorldCup AI",
  manifest: "/manifest.webmanifest",
  openGraph: {
    type: "website",
    locale: "he_IL",
    siteName: "WorldCup AI",
    title: "WorldCup AI — אנליסט משחקי מונדיאל מבוסס AI",
    description: "מודל מתקדם, מנוע ערך מול השוק, וסימולציה אינטראקטיבית — בעברית.",
  },
  twitter: {
    card: "summary_large_image",
    title: "WorldCup AI",
    description: "אנליסט משחקי מונדיאל מבוסס AI — בעברית.",
  },
  icons: { icon: "/icon.svg" },
};

export const viewport: Viewport = {
  themeColor: "#050a07",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="he" dir="rtl">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
