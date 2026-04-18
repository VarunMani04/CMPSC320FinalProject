import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
	const r = await fetch("/api/roadmap");
	return { roadmapPayload: r.ok ? await r.json() : { roadmap: null } };
};
