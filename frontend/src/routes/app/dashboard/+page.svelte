<svelte:head>
	<title>Overview · PostingPal</title>
</svelte:head>

<script lang="ts">
	import type { PageData } from "./$types";

	let { data }: { data: PageData } = $props();

	const c = $derived(data.profile?.completeness);
	const profileReady = $derived(
		Boolean(c?.has_name && c?.has_education && (c?.skill_count ?? 0) > 0)
	);
	const jobsCount = $derived(data.jobs?.jobs?.length ?? 0);
	const hasGap = $derived(Boolean(data.gap?.report));
	const hasRoadmap = $derived(Boolean(data.roadmap?.roadmap?.milestones?.length));

	const doneCount = $derived(
		[profileReady, jobsCount > 0, hasGap, hasRoadmap].filter(Boolean).length
	);
</script>

<div class="mx-auto max-w-3xl">
	<h1 class="page-title">Overview</h1>
	<p class="page-sub">Your checklist from profile to roadmap—small steps, visible progress.</p>

	<section class="mt-8 rounded-card bg-sage p-6 text-white shadow-sagebtn sm:p-8">
		<p class="text-[12px] font-normal text-white/85">Progress</p>
		<p class="mt-1 text-kpi font-bold text-white">
			{doneCount}<span class="text-[20px] font-semibold text-white/75">/4</span>
		</p>
		<p class="mt-2 max-w-md text-[12px] leading-relaxed text-white/90">
			Complete each step in order when you can—nothing here is urgent, just structured.
		</p>
	</section>

	<ul class="mt-6 grid gap-4">
		<li class="card flex gap-4 shadow-card">
			<div class="w-1 shrink-0 self-stretch rounded-sm bg-sage-light" aria-hidden="true"></div>
			<div class="min-w-0 flex-1">
				<p class="text-[12px] text-ink-muted">{profileReady ? "Done" : "Step 1"}</p>
				<p class="text-[16px] font-bold text-ink">Student profile</p>
				<p class="mt-1 text-[12px] leading-relaxed text-ink-muted">Name, education, and at least one skill.</p>
				<a class="btn-secondary mt-4 inline-flex text-2xs" href="/app/profile">Open profile</a>
			</div>
			<span class="shrink-0 text-[20px] text-ink-label" aria-hidden="true">{profileReady ? "✓" : "○"}</span>
		</li>
		<li class="card flex gap-4 shadow-card">
			<div class="w-1 shrink-0 self-stretch rounded-sm bg-sage-light" aria-hidden="true"></div>
			<div class="min-w-0 flex-1">
				<p class="text-[12px] text-ink-muted">{jobsCount ? "Done" : "Step 2"}</p>
				<p class="text-[16px] font-bold text-ink">Job descriptions parsed</p>
				<p class="mt-1 text-[12px] leading-relaxed text-ink-muted">
					{jobsCount ? `${jobsCount} saved.` : "Paste one or more postings."}
				</p>
				<a class="btn-secondary mt-4 inline-flex text-2xs" href="/app/jobs">Open parser</a>
			</div>
			<span class="shrink-0 text-[20px] text-ink-label" aria-hidden="true">{jobsCount ? "✓" : "○"}</span>
		</li>
		<li class="card flex gap-4 shadow-card">
			<div class="w-1 shrink-0 self-stretch rounded-sm bg-sage-light" aria-hidden="true"></div>
			<div class="min-w-0 flex-1">
				<p class="text-[12px] text-ink-muted">{hasGap ? "Done" : "Step 3"}</p>
				<p class="text-[16px] font-bold text-ink">Gap analysis</p>
				<p class="mt-1 text-[12px] leading-relaxed text-ink-muted">Compare your profile to what employers ask for.</p>
				<a class="btn-secondary mt-4 inline-flex text-2xs" href="/app/gap">Open gap report</a>
			</div>
			<span class="shrink-0 text-[20px] text-ink-label" aria-hidden="true">{hasGap ? "✓" : "○"}</span>
		</li>
		<li class="card flex gap-4 shadow-card">
			<div class="w-1 shrink-0 self-stretch rounded-sm bg-sage-light" aria-hidden="true"></div>
			<div class="min-w-0 flex-1">
				<p class="text-[12px] text-ink-muted">{hasRoadmap ? "Done" : "Step 4"}</p>
				<p class="text-[16px] font-bold text-ink">Learning roadmap</p>
				<p class="mt-1 text-[12px] leading-relaxed text-ink-muted">Milestones you can tick off as you level up.</p>
				<a class="btn-secondary mt-4 inline-flex text-2xs" href="/app/roadmap">Open roadmap</a>
			</div>
			<span class="shrink-0 text-[20px] text-ink-label" aria-hidden="true">{hasRoadmap ? "✓" : "○"}</span>
		</li>
	</ul>
</div>
