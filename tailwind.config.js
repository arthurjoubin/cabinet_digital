/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './cabinet_digital/templates/**/*.html',
    './static/src/**/*.css',  // Ajout pour inclure vos fichiers CSS personnalisés
  ],
  theme: {
    extend: {
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
