import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: {
          950: "#071a12",
          900: "#0b2e1f",
          800: "#124a32",
        },
        gold: "#f5c542",
      },
    },
  },
  plugins: [],
};

export default config;
