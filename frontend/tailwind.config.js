/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A0E1A",
        foreground: "#FFFFFF",
        primary: {
          DEFAULT: "#3B82F6",
          dark: "#2563EB",
        },
        success: "#10B981",
        danger: "#EF4444",
        warning: "#F59E0B",
        card: "#1A1F2E",
        "card-hover": "#232938",
      },
    },
  },
  plugins: [],
};
