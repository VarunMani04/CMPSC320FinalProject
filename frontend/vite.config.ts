import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			"/api": {
				target: "http://127.0.0.1:5000",
				changeOrigin: true
			}
		}
	},
	// Explicit preview proxy (defaults to server.proxy, but keeps POST /api working after `vite build && vite preview`)
	preview: {
		proxy: {
			"/api": {
				target: "http://127.0.0.1:5000",
				changeOrigin: true
			}
		}
	}
});
