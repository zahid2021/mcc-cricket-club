/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        mcc: {
          green: "#1a7a2e",
          lime: "#39ff14",
          neon: "#7CFF3A",
          forest: "#0d3d18",
          gold: "#F5C518",
          amber: "#E8A317",
          dark: "#06140a",
          night: "#0a1f10",
          cream: "#f4f7f2",
        },
      },
      fontFamily: {
        display: ["var(--font-bebas)", "Impact", "sans-serif"],
        heading: ["var(--font-oswald)", "Arial Narrow", "sans-serif"],
        body: ["var(--font-dm-sans)", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "stadium-glow":
          "radial-gradient(ellipse at 50% 0%, rgba(57,255,20,0.18) 0%, transparent 55%), radial-gradient(ellipse at 80% 100%, rgba(245,197,24,0.12) 0%, transparent 40%)",
      },
      boxShadow: {
        glow: "0 0 40px rgba(57,255,20,0.25)",
        gold: "0 0 30px rgba(245,197,24,0.35)",
      },
    },
  },
  plugins: [],
};
