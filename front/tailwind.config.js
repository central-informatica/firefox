/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand Colors
        'xfire-red': '#D32F2F',
        'xfire-orange': '#F57C00',

        // Dark Backgrounds
        'dark-primary': '#0F0F0F',
        'dark-secondary': '#1A1A1A',
        'dark-tertiary': '#222222',

        // Neutrals
        'neutral-100': '#F5F5F5',
        'neutral-200': '#E0E0E0',
        'neutral-300': '#BDBDBD',
        'neutral-400': '#9E9E9E',
        'neutral-500': '#757575',
        'neutral-600': '#616161',
        'neutral-700': '#424242',
        'neutral-800': '#303030',
        'neutral-900': '#2B2B2B',

        // Status Colors
        'status-permitido': '#2E7D32',
        'status-monitorado': '#1565C0',
        'status-alerta': '#FB8C00',
        'status-bloqueado': '#C62828',
        'status-expirando': '#F9A825',

        // Legacy (keeping for backward compatibility)
        primary: '#F57C00',
        secondary: '#D32F2F',
        success: '#2E7D32',
        danger: '#C62828',
        purple: '#642d61',
      },
      fontFamily: {
        'montserrat': ['Montserrat', 'system-ui', 'sans-serif'],
        'inter': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        'card': '12px',
        'button': '8px',
        'modal': '16px',
      },
      spacing: {
        '260': '260px',
      },
      animation: {
        fadeIn: 'fadeIn 0.5s ease-in-out',
        slideUp: 'slideUp 0.6s ease-out',
        slideInLeft: 'slideInLeft 0.8s ease-out',
        blob: 'blob 7s infinite',
        float: 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        blob: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}
