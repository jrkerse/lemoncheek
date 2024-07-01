/** @type {import('tailwindcss').Config} */

const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    './assets/templates/*.{html,js,tmpl}',
    './assets/templates/**/*.{html,js,tmpl}',
  ],
  theme: {
    extend: {
      fontFamily: {
        primary: ['Poppins', ...defaultTheme.fontFamily.sans],
        secondary: ['"Open Sans"', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        'lemon': '#FFD700',
        'charcoal': '#36454F',
        'cream': '#F9F9F9',
        'mint': '#98FB98',
        'coral': '#FF7F50',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}

