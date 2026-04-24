<svelte:head>
	<title>Gap report · PostingPal</title>
</svelte:head>

<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import type { PageData } from "./$types";

	let { data }: { data: PageData } = $props();

	let busy = $state(false);
	let err = $state<string | null>(null);

	const report = $derived(data.latest?.report);

	function badgeClass(match: string | undefined) {
		if (match === "strong") return "badge-positive";
		if (match === "partial") return "badge-neutral";
		return "badge-negative";
	}

	async function generate(e: Event) {
		e.preventDefault();
		err = null;
		busy = true;
		const res = await fetch("/api/gap-reports/generate", {
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
</script>

<div class="mx-auto max-w-4xl">
	<div class="flex flex-wrap items-end justify-between gap-4">
		<div>
			<h1 class="page-title">Gap analysis</h1>
			<p class="page-sub">
				Uses your profile and saved job postings. Generate a fresh report whenever your inputs change.
			</p>
		</div>
		<button class="btn-primary" type="button" disabled={busy} onclick={generate}>
			{busy ? "Working…" : "Generate report"}
		</button>
	</div>

	{#if err}
		<p class="mt-4 rounded-badge bg-negative-bg px-4 py-3 text-[12px] font-medium text-negative">{err}</p>
	{/if}

	{#if report}
		<div class="card mt-8 space-y-4 shadow-card">
			{#if report.llm_error}
				<p class="badge-warn inline-flex">Note: {report.llm_error}</p>
			{/if}
			<p class="text-[13px] leading-relaxed text-ink-body">{report.summary ?? ""}</p>
			<div class="overflow-x-auto">
				<table class="min-w-full text-left text-[13px]">
					<thead>
						<tr class="border-b border-badge-neutral-bg text-[11px] font-semibold uppercase text-ink-label">
							<th class="py-3 pr-4">Requirement</th>
							<th class="py-3 pr-4">Match</th>
							<th class="py-3">Rationale</th>
						</tr>
					</thead>
					<tbody>
						{#each report.rows ?? [] as row}
							<tr class="border-b border-badge-neutral-bg align-top">
								<td class="py-3 pr-4 font-medium text-ink">{row.requirement}</td>
								<td class="py-3 pr-4">
									<span class={badgeClass(row.match)}>{row.match}</span>
								</td>
								<td class="py-3 text-ink-muted">{row.rationale}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{:else}
		<p class="mt-8 text-[12px] text-ink-muted">No report yet—save job postings first, then generate.</p>
	{/if}
</div>
