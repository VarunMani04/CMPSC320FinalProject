<script lang="ts">
	import { goto } from "$app/navigation";

	async function logout() {
		await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
		await goto("/");
	}
</script>

<button
	type="button"
	class="flex h-10 w-10 items-center justify-center rounded-full text-icon-muted transition hover:bg-card-alt hover:text-ink-body"
	title="Log out"
	onclick={logout}
>
	<span class="sr-only">Log out</span>
	<svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24" aria-hidden="true">
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			d="M15 12H3m4-4-4 4 4 4M9 5h7a2 2 0 012 2v10a2 2 0 01-2 2H9"
		/>
	</svg>
</button>
