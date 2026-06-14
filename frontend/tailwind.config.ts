import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: { 950: "#060d09", 900: "#0a1a12", 800: "#124a32" },
        gold: "#f5c542",
        accent: "#10b981",
      },
      fontFamily: { heebo: ["Heebo", "sans-serif"] },
    },
  },
  plugins: [],
};

export default config;
