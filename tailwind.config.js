/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './cabinet_digital/templates/**/*.html',
    './static/src/**/*.css', // Inclure les fichiers CSS personnalisés
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
