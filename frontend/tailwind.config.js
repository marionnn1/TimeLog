/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#26AA9B', // Tu verde Inetum
                    hover: '#1f8c7f',
                    light: '#e0f2f1'
                },
                dark: {
                    DEFAULT: '#232D4B', // Tu azul oscuro corporativo
                    light: '#334155'
                },
                status: {
                    active: '#10b981',
                    warning: '#f59e0b',
                    danger: '#ef4444',
                    info: '#3b82f6'
                },
                // --- NUEVOS COLORES CENTRALIZADOS (CALENDARIO & DASHBOARD) ---
                absence: {
                    vacation: '#10b981', // Verde Esmeralda (Vacaciones)
                    festivo: '#f97316',  // Naranja Intenso (Festivo)
                    personal: '#3b82f6'  // Azul (Asuntos Propios)
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}