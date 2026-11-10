/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        app: "#F8F9FC",
        surface: "#FFFFFF",
        primaryText: "#172033",
        secondaryText: "#667085",
        accent: {
          DEFAULT: "#6258F5",
          hover: "#5146E5",
          light: "#F0EFFF",
        },
        border: "#E7EAF0",
        success: {
          DEFAULT: "#16865C",
          bg: "#ECFDF3",
          border: "#A6F4C5",
        },
        warning: {
          DEFAULT: "#D99422",
          bg: "#FFFAEB",
          border: "#FEDF89",
        },
        danger: {
          DEFAULT: "#D94A4A",
          bg: "#FEF3F2",
          border: "#FECDCA",
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(16, 24, 40, 0.04), 0 1px 2px -1px rgba(16, 24, 40, 0.02)",
        subtle: "0 1px 2px 0 rgba(16, 24, 40, 0.05)",
        drawer: "-4px 0 24px -2px rgba(16, 24, 40, 0.12)",
      }
    },
  },
  plugins: [],
}

