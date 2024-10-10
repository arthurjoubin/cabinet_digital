/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './cabinet_digital/templates/**/*.html',
  ],
  theme: {
    extend: {},
    
  },
  plugins: [require('@tailwindcss/typography')],
}

