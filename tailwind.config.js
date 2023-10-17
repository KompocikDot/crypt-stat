/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./backend/assets/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [
      require('@tailwindcss/forms'),
  ],
}
