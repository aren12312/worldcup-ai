import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "WorldCup AI — אנליסט משחקי מונדיאל",
    short_name: "WorldCup AI",
    description: "חיזוי וניתוח משחקי מונדיאל מבוסס AI בעברית",
    start_url: "/",
    display: "standalone",
    background_color: "#050a07",
    theme_color: "#050a07",
    lang: "he",
    dir: "rtl",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
