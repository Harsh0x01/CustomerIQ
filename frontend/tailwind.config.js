/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0a0a0f",
        panel: "#11121a",
        panelSoft: "#151722",
        stroke: "rgba(255,255,255,0.1)",
        cyan: "#00d4ff",
        purple: "#7c3aed",
        ink: "#f8fafc",
        muted: "#8b92a5",
        success: "#22c55e",
        warning: "#f59e0b",
        danger: "#ef4444"
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif"
        ],
        mono: [
          "JetBrains Mono",
          "SFMono-Regular",
          "Consolas",
          "Liberation Mono",
          "monospace"
        ]
      },
      boxShadow: {
        cyan: "0 0 32px rgba(0, 212, 255, 0.18)",
        purple: "0 0 32px rgba(124, 58, 237, 0.2)"
      }
    }
  },
  plugins: []
};
