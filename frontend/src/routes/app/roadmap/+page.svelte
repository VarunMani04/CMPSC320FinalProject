<svelte:head>
	<title>Roadmap · PostingPal</title>
</svelte:head>

<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import type { PageData } from "./$types";

	let { data }: { data: PageData } = $props();

	let busy = $state(false);
	let err = $state<string | null>(null);

	const rm = $derived(data.roadmapPayload?.roadmap);

	async function generate() {
		err = null;
		busy = true;
		const res = await fetch("/api/roadmap/generate", {
			method: "POST",
			credentials: "include"
		});
		busy = false;
		if (!res.ok) {
			const t = await res.json().catch(() => ({}));
			err = (t as { error?: string }).error || (await res.text());
			return;
		}
		await invalidateAll();
	}

	async function toggle(milestoneId: string, completed: boolean) {
		const res = await fetch(`/api/roadmap/milestones/${encodeURIComponent(milestoneId)}`, {
			method: "PATCH",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ completed })
		});
		if (!res.ok) {
			err = await res.text();
			return;
		}
		await invalidateAll();
	}
</script>

<div class="mx-auto max-w-3xl">
	<div class="flex flex-wrap items-end justify-between gap-4">
		<div>
			<h1 class="page-title">Learning roadmap</h1>
			<p class="page-sub">
				Built from your latest gap report. Generating again replaces this roadmap for your account.
			</p>
		</div>
		<button class="btn-primary" type="button" disabled={busy} onclick={generate}>
			{busy ? "Building…" : "Generate roadmap"}
		</button>
	</div>

	{#if err}
		<p class="mt-4 rounded-badge bg-negative-bg px-4 py-3 text-[12px] font-medium text-negative">{err}</p>
	{/if}

	{#if rm?.intro}
		<p class="mt-8 text-[13px] leading-relaxed text-ink-body">{rm.intro}</p>
	{/if}

	{#if rm?.milestones?.length}
		<ul class="mt-6 grid gap-4">
			{#each rm.milestones as m}
				<li class="card flex gap-4 shadow-card">
					<input
						type="checkbox"
						class="mt-1 h-4 w-4 rounded border-0 accent-sage shadow-card"
						checked={m.completed}
						onchange={(e) => toggle(m.id, (e.currentTarget as HTMLInputElement).checked)}
					/>
					<div class="min-w-0 flex-1">
						<p class="text-[15px] font-semibold text-ink">{m.title}</p>
						<p class="mt-1 text-[12px] leading-relaxed text-ink-muted">{m.description}</p>
						<div class="mt-2 flex flex-wrap gap-2 text-2xs text-ink-label">
							<span>~{m.weeks_estimate} wk</span>
							{#if m.resource_url}
								<a class="link-quiet text-2xs" href={m.resource_url} target="_blank" rel="noreferrer">Resource</a>
							{/if}
						</div>
					</div>
				</li>
			{/each}
		</ul>
	{:else}
		<p class="mt-8 text-[12px] text-ink-muted">No roadmap yet.</p>
	{/if}
</div>
