/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            // AQUÍ CENTRALIZAMOS LOS COLORES
            colors: {
                primary: {
                    DEFAULT: '#26AA9B', // Tu verde Inetum
                    hover: '#1f8c7f',   // Un tono más oscuro para hovers
                    light: '#e0f2f1'    // Un tono muy claro para fondos
                },
                dark: {
                    DEFAULT: '#232D4B', // Tu azul oscuro corporativo
                    light: '#334155'    // Un gris azulado para textos secundarios
                },
                // Semáforos para estados (ya no tendrás que recordar el hex del rojo)
                status: {
                    active: '#10b981',  // Emerald-500
                    warning: '#f59e0b', // Amber-500
                    danger: '#ef4444',  // Red-500
                    info: '#3b82f6'     // Blue-500
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'], // O la fuente que uses
            }
        },
    },
    plugins: [],
}