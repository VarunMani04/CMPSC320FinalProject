import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
	const r = await fetch("/api/jobs");
	return { jobsPayload: r.ok ? await r.json() : { jobs: [] } };
};
