import type { Handle } from "@sveltejs/kit";
import { env } from "$env/dynamic/private";

/**
 * Proxy /api/* to Flask so browser POSTs never hit a static file server (which often returns 403).
 * Set API_ORIGIN in .env for production (e.g. https://your-api.example.com). Defaults to local Flask.
 */
export const handle: Handle = async ({ event, resolve }) => {
	const path = event.url.pathname;
	if (!path.startsWith("/api")) {
		return resolve(event);
	}

	const origin = (env.API_ORIGIN ?? "http://127.0.0.1:5000").replace(/\/$/, "");
	const target = `${origin}${path}${event.url.search}`;

	const headers = new Headers();
	event.request.headers.forEach((value, key) => {
		const k = key.toLowerCase();
		if (k === "host" || k === "connection") return;
		headers.set(key, value);
	});

	const init: RequestInit = {
		method: event.request.method,
		headers,
		redirect: "manual"
	};

	if (event.request.method !== "GET" && event.request.method !== "HEAD") {
		const buf = await event.request.arrayBuffer();
		if (buf.byteLength > 0) {
			init.body = buf;
		}
	}

	const upstream = await fetch(target, init);
	const outHeaders = new Headers(upstream.headers);
	return new Response(upstream.body, {
		status: upstream.status,
		statusText: upstream.statusText,
		headers: outHeaders
	});
};
