/** @type {import('tailwindcss').Config} */
/* Tokens from design-system (1).json — Sage Dashboard / Organic Minimal */
export default {
	content: ["./src/**/*.{html,js,svelte,ts}"],
	theme: {
		extend: {
			colors: {
				canvas: "#ECEAE4",
				card: "#FFFFFF",
				"card-alt": "#F5F4F0",
				sage: {
					DEFAULT: "#4A6741",
					mid: "#6A8F67",
					light: "#A8C0A5",
					ghost: "#E8EFE7"
				},
				ink: {
					DEFAULT: "#1A1A1A",
					body: "#3A3A3A",
					muted: "#8A8A8A",
					label: "#B0B0B0"
				},
				positive: {
					DEFAULT: "#4A6741",
					bg: "#E8EFE7"
				},
				negative: {
					DEFAULT: "#C0392B",
					bg: "#FDECEA"
				},
				"badge-neutral": {
					bg: "#F0F0EE",
					text: "#6A6A6A"
				},
				"icon-muted": "#AAAAAA"
			},
			fontFamily: {
				sans: ["Inter", "DM Sans", "Nunito Sans", "system-ui", "sans-serif"]
			},
			fontSize: {
				"2xs": ["11px", { lineHeight: "1.5" }],
				kpi: ["32px", { lineHeight: "1.1", letterSpacing: "-0.02em" }]
			},
			borderRadius: {
				card: "20px",
				btn: "12px",
				badge: "6px",
				icon: "12px"
			},
			boxShadow: {
				card: "0 2px 12px rgba(0, 0, 0, 0.06)",
				"card-hover": "0 6px 24px rgba(0, 0, 0, 0.10)",
				sagebtn: "0 2px 8px rgba(74, 103, 65, 0.25)"
			},
			maxWidth: {
				content: "72rem"
			},
			accentColor: {
				sage: "#4A6741"
			}
		}
	},
	plugins: []
};
