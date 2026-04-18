import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
	const r = await fetch("/api/gap-reports/latest");
	return { latest: r.ok ? await r.json() : { report: null } };
};
