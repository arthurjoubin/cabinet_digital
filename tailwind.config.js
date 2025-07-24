/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './cabinet_digital/templates/**/*.html',
    './integrations/templates/**/*.html',
    './static/src/**/*.css',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      '.custom-header-emerald': {
        '@apply text-3xl font-bold text-gray-900 mb-8 border-b border-emerald-200 pb-4': {},
      },
      screens: {
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
  // Optimisation pour la production
  purge: {
    enabled: process.env.NODE_ENV === 'production',
    content: [
      './templates/**/*.html',
      './cabinet_digital/templates/**/*.html',
      './integrations/templates/**/*.html',
      './static/src/**/*.css',
      './static/js/**/*.js',
    ],
    options: {
      safelist: [
        'prose',
        'prose-lg',
        'prose-xl',
        // Classes dynamiques courantes
        /^bg-.*$/,
        /^text-.*$/,
        /^border-.*$/,
        /^hover:.*$/,
        /^focus:.*$/,
        /^active:.*$/,
        // Classes spécifiques au projet
        'custom-header-emerald',
      ],
    },
  },
};
