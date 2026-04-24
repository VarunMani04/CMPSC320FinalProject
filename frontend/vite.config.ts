import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig, loadEnv } from "vite";

/** Match `PORT` in `backend/.env` (default 5000). On macOS, AirPlay often uses 5000 — use 5001. */
export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, ".", "");
	const flaskPort = env.FLASK_PORT || "5000";
	const target = `http://127.0.0.1:${flaskPort}`;

	return {
		plugins: [sveltekit()],
		server: {
			proxy: {
				"/api": {
					target,
					changeOrigin: true
				}
			}
		},
		preview: {
			proxy: {
				"/api": {
					target,
					changeOrigin: true
				}
			}
		}
	};
});
