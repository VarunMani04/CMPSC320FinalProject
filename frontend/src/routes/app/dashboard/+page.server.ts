import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
	const [p, g, j, rm] = await Promise.all([
		fetch("/api/profile"),
		fetch("/api/gap-reports/latest"),
		fetch("/api/jobs"),
		fetch("/api/roadmap")
	]);
	return {
		profile: p.ok ? await p.json() : null,
		gap: g.ok ? await g.json() : null,
		jobs: j.ok ? await j.json() : { jobs: [] as unknown[] },
		roadmap: rm.ok ? await rm.json() : null
	};
};
