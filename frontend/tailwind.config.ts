import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: { 950: "#050a07", 900: "#0a1410", 800: "#0f2419", 700: "#14492f" },
        gold: "#f5c542",
        accent: "#10b981",
        ice: "#38bdf8",
        magenta: "#a855f7",
      },
      fontFamily: { heebo: ["Heebo", "sans-serif"] },
      boxShadow: {
        glow: "0 0 40px rgba(245, 197, 66, 0.18)",
        "glow-emerald": "0 0 50px rgba(16, 185, 129, 0.2)",
      },
      backgroundImage: {
        "grid-faint":
          "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
      },
      keyframes: {
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.6s infinite",
        "fade-up": "fade-up 0.5s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
