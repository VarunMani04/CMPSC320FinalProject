import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
	const r = await fetch("/api/profile");
	if (!r.ok) {
		return { profile: null, error: await r.text() };
	}
	return { profile: await r.json(), error: null as string | null };
};
