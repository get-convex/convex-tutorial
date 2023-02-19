const defaultTheme = require('tailwindcss/defaultTheme')
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/*.{jsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['DM Sans', ...defaultTheme.fontFamily.sans],
      },
    },
    colors: {
      white: '#F5F1F1',
      green: '#3F5E5A',
      blue: '#6F9CEB',

    }
  },
  plugins: [],
}
