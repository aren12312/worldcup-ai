import { ImageResponse } from "next/og";

export const alt = "WorldCup AI — אנליסט משחקי מונדיאל מבוסס AI";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #050a07 0%, #0f2419 100%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div
            style={{
              width: 90,
              height: 90,
              borderRadius: 24,
              border: "4px solid #f5c542",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 48,
            }}
          >
            ⚽
          </div>
          <div style={{ fontSize: 72, fontWeight: 800, color: "#f5c542" }}>WorldCup AI</div>
        </div>
        <div style={{ fontSize: 38, marginTop: 28, color: "rgba(255,255,255,0.85)" }}>
          אנליסט משחקי מונדיאל מבוסס AI
        </div>
        <div style={{ fontSize: 26, marginTop: 16, color: "rgba(255,255,255,0.55)" }}>
          Dixon-Coles · Monte Carlo · Value Engine
        </div>
      </div>
    ),
    { ...size }
  );
}
