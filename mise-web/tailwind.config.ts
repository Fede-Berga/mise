import type { Config } from "tailwindcss";
import forms from "@tailwindcss/forms";

/**
 * Mise Tailwind Configuration
 *
 * Brand token reference:
 *   Primary accent : amber-500  (#F59E0B)
 *   Background     : neutral-950 (#0A0A0A)
 *   Surface        : neutral-900 (#141414)
 *   Surface raised : neutral-800 (#1C1C1C)
 *   Border         : neutral-700 (#2A2A2A)
 *   Text primary   : neutral-50  (#FAFAFA)
 *   Text muted     : neutral-400 (#A3A3A3)
 *
 * All semantic colours are exposed through the `mise` key so that components
 * reference `mise-*` rather than raw Tailwind shades. This makes a future
 * theme swap (e.g. white-label) a single-file change.
 */
const config: Config = {
    // Restrict Tailwind's content scan to source files only
    content: [
        "./app/**/*.{ts,tsx}",
        "./components/**/*.{ts,tsx}",
        "./lib/**/*.{ts,tsx}",
        "./hooks/**/*.{ts,tsx}",
    ],

    theme: {
        extend: {
            // ─── Brand colour palette ───────────────────────────────────────
            colors: {
                mise: {
                    // Accent / CTA
                    amber: {
                        DEFAULT: "#F59E0B",
                        light: "#FCD34D",
                        dark: "#B45309",
                    },
                    // Backgrounds
                    bg: "#0A0A0A",
                    surface: "#141414",
                    raised: "#1E1E1E",
                    // Borders
                    border: "#2A2A2A",
                    // Text
                    text: {
                        DEFAULT: "#F5F5F5",
                        muted: "#A3A3A3",
                        faint: "#525252",
                    },
                    // Status colours
                    status: {
                        new: "#6366F1", // indigo
                        preparing: "#F59E0B", // amber
                        ready: "#22C55E", // green
                        closed: "#71717A", // zinc
                    },
                },
            },

            // ─── Typography ─────────────────────────────────────────────────
            fontFamily: {
                sans: ["Inter", "system-ui", "sans-serif"],
                display: ["Playfair Display", "Georgia", "serif"],
            },

            // ─── Spacing / sizing extras ─────────────────────────────────────
            spacing: {
                "18": "4.5rem",
                "72": "18rem",
                "84": "21rem",
                "96": "24rem",
            },

            // ─── Animation ──────────────────────────────────────────────────
            keyframes: {
                "fade-in": {
                    "0%": { opacity: "0", transform: "translateY(4px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                "slide-in": {
                    "0%": { opacity: "0", transform: "translateX(-8px)" },
                    "100%": { opacity: "1", transform: "translateX(0)" },
                },
                "pulse-amber": {
                    "0%, 100%": { boxShadow: "0 0 0 0 rgba(245,158,11,0.4)" },
                    "50%": { boxShadow: "0 0 0 6px rgba(245,158,11,0)" },
                },
            },
            animation: {
                "fade-in": "fade-in 0.2s ease-out both",
                "slide-in": "slide-in 0.2s ease-out both",
                "pulse-amber": "pulse-amber 2s ease-in-out infinite",
            },

            // ─── Border radii ───────────────────────────────────────────────
            borderRadius: {
                DEFAULT: "0.5rem",
                "xl": "0.75rem",
                "2xl": "1rem",
            },
        },
    },

    plugins: [
        forms({ strategy: "class" }), // opt-in form styles per element
    ],
};

export default config;
