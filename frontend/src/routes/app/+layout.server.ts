import { redirect } from "@sveltejs/kit";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch, url }) => {
	const r = await fetch("/api/auth/me");
	const j = (await r.json()) as { user: { id: number; email: string } | null };
	if (!j.user) {
		const next = encodeURIComponent(url.pathname + url.search);
		throw redirect(303, `/login?next=${next}`);
	}
	return { user: j.user };
};
