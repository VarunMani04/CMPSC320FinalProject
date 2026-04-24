<svelte:head>
	<title>Job postings · PostingPal</title>
</svelte:head>

<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import type { PageData } from "./$types";

	let { data }: { data: PageData } = $props();

	let raw = $state("");
	let busy = $state(false);
	let err = $state<string | null>(null);

	function splitPostings(text: string): string[] {
		const parts = text
			.split(/\n\s*---\s*\n/)
			.map((s) => s.trim())
			.filter(Boolean);
		if (parts.length) return parts;
		const t = text.trim();
		return t ? [t] : [];
	}

	async function analyze(e: Event) {
		e.preventDefault();
		err = null;
		const postings = splitPostings(raw);
		if (!postings.length) {
			err = "Paste at least one job description.";
			return;
		}
		busy = true;
		const res = await fetch("/api/jobs/analyze", {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ postings })
		});
		busy = false;
		if (!res.ok) {
			err = await res.text();
			return;
		}
		raw = "";
		await invalidateAll();
	}
</script>

<div class="mx-auto max-w-3xl">
	<h1 class="page-title">Job postings</h1>
	<p class="page-sub">
		Paste one or more full postings. Separate them with a line containing only <code
			class="rounded-badge bg-card-alt px-1.5 py-0.5 text-2xs font-semibold text-ink-body">---</code
		>. Each run replaces your saved postings.
	</p>

	<form class="card mt-8 space-y-5 shadow-card" onsubmit={analyze}>
		<div>
			<label class="label" for="raw">Job description text</label>
			<textarea
				id="raw"
				class="field min-h-[220px] font-mono text-2xs leading-relaxed"
				bind:value={raw}
				placeholder="Paste posting(s) here…"
			></textarea>
		</div>
		{#if err}
			<p class="rounded-badge bg-negative-bg px-3 py-2 text-[12px] font-medium text-negative">{err}</p>
		{/if}
		<button class="btn-primary" type="submit" disabled={busy}>{busy ? "Analyzing…" : "Analyze & save"}</button>
	</form>

	<section class="mt-12">
		<h2 class="text-[12px] font-semibold uppercase tracking-wide text-ink-label">Saved postings</h2>
		{#if !data.jobsPayload.jobs?.length}
			<p class="mt-2 text-[12px] leading-relaxed text-ink-muted">No saved postings yet.</p>
		{:else}
			<ul class="mt-4 grid gap-4">
				{#each data.jobsPayload.jobs as job}
					<li class="card shadow-card">
						<div class="flex flex-wrap items-center justify-between gap-2">
							<p class="text-[14px] font-semibold text-ink">
								{job.parsed?.title_guess || "Untitled role"}
							</p>
							{#if job.vague}
								<span class="badge-warn">Vague posting</span>
							{/if}
						</div>
						{#if job.parse_error}
							<p class="mt-2 text-2xs font-medium text-negative">Parse note: {job.parse_error}</p>
						{/if}
						{#if job.parsed}
							<div class="mt-4 grid gap-4 text-[13px] sm:grid-cols-2">
								<div>
									<p class="text-[11px] font-semibold uppercase tracking-wide text-ink-label">Required skills</p>
									<ul class="mt-2 list-inside list-disc text-ink-body">
										{#each job.parsed.required_skills?.slice(0, 12) ?? [] as sk}
											<li>{sk}</li>
										{/each}
									</ul>
								</div>
								<div>
									<p class="text-[11px] font-semibold uppercase tracking-wide text-ink-label">Preferred</p>
									<ul class="mt-2 list-inside list-disc text-ink-body">
										{#each job.parsed.preferred_skills?.slice(0, 8) ?? [] as sk}
											<li>{sk}</li>
										{/each}
									</ul>
								</div>
							</div>
						{/if}
						<details class="mt-4 text-[11px] text-ink-muted">
							<summary class="cursor-pointer font-medium text-ink-muted hover:text-ink-body">Raw text</summary>
							<pre
								class="mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded-btn bg-card-alt p-3 text-ink-body"
								>{job.raw_text}</pre
							>
						</details>
					</li>
				{/each}
			</ul>
		{/if}
	</section>
</div>
