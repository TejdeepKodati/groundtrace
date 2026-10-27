/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0B0F19",
        cardBg: "#111827",
        borderSubtle: "#1F2937",
        brandEmerald: "#10B981",
        brandCyan: "#06B6D4",
      },
    },
  },
  plugins: [],
};
