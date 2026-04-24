<svelte:head>
	<title>Log in · PostingPal</title>
</svelte:head>

<script lang="ts">
	import { goto } from "$app/navigation";
	import { page } from "$app/stores";
	import { get } from "svelte/store";

	let email = $state("");
	let password = $state("");
	let error = $state<string | null>(null);
	let loading = $state(false);

	async function submit(e: Event) {
		e.preventDefault();
		error = null;
		loading = true;
		const res = await fetch("/api/auth/login", {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ email, password })
		});
		loading = false;
		if (!res.ok) {
			const b = await res.json().catch(() => ({}));
			error = (b as { error?: string }).error || "Could not log in";
			return;
		}
		const next = get(page).url.searchParams.get("next") || "/app/dashboard";
		await goto(next);
	}
</script>

<main class="mx-auto flex min-h-screen max-w-md flex-col justify-center px-5 py-12">
	<a class="text-[12px] text-ink-muted transition hover:text-ink-body" href="/">← Back home</a>
	<h1 class="page-title mt-6">Welcome back</h1>

	<form class="card mt-8 space-y-5 shadow-card" onsubmit={submit}>
		<div>
			<label class="label" for="email">Email</label>
			<input id="email" class="field" type="email" autocomplete="email" bind:value={email} required />
		</div>
		<div>
			<label class="label" for="password">Password</label>
			<input
				id="password"
				class="field"
				type="password"
				autocomplete="current-password"
				bind:value={password}
				required
			/>
		</div>
		{#if error}
			<p class="rounded-badge bg-negative-bg px-3 py-2 text-[12px] font-medium text-negative">{error}</p>
		{/if}
		<button class="btn-primary w-full" type="submit" disabled={loading}>
			{loading ? "Signing in…" : "Log in"}
		</button>
	</form>
	<p class="mt-8 text-center text-[12px] text-ink-muted">
		New here?
		<a class="link-quiet" href="/register">Create an account</a>
	</p>
</main>
