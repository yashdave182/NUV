/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        agri: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        gold: {
          400: '#facc15',
          500: '#eab308',
          600: '#ca8a04',
        },
        teal: {
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
        },
        navy: {
          800: '#0a1628',
          900: '#060d1a',
        },
        glass: 'rgba(255,255,255,0.05)',
        glassBorder: 'rgba(255,255,255,0.12)',
      },
      backgroundImage: {
        'agri-gradient': 'linear-gradient(135deg, #0a1628 0%, #052e16 50%, #0a1628 100%)',
        'card-gradient': 'linear-gradient(135deg, rgba(22,101,52,0.15) 0%, rgba(20,184,166,0.08) 100%)',
        'hero-gradient': 'linear-gradient(135deg, #0f2a1a 0%, #0a1628 60%, #0d2b2b 100%)',
        'gold-gradient': 'linear-gradient(135deg, #ca8a04 0%, #facc15 100%)',
      },
      backdropBlur: { xs: '2px' },
      boxShadow: {
        glass: '0 4px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)',
        glow: '0 0 20px rgba(34,197,94,0.25)',
        'glow-teal': '0 0 20px rgba(20,184,166,0.25)',
        'glow-gold': '0 0 20px rgba(234,179,8,0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        pulse2: 'pulse2 2s cubic-bezier(0.4,0,0.6,1) infinite',
        shimmer: 'shimmer 2s infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(16px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideInRight: { from: { opacity: '0', transform: 'translateX(24px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        pulse2: { '0%,100%': { opacity: '1' }, '50%': { opacity: '0.5' } },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
        float: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-8px)' } },
      },
    },
  },
  plugins: [],
}
