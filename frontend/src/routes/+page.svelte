<svelte:head>
	<title>Student Skill Gap Analyzer</title>
</svelte:head>

<main class="mx-auto flex min-h-screen max-w-5xl flex-col px-5 py-14 sm:px-8">
	<header class="flex flex-wrap items-end justify-between gap-8">
		<div class="max-w-xl">
			<p class="text-[12px] font-normal tracking-wide text-ink-muted">Career clarity, without the noise</p>
			<h1 class="mt-2 text-[32px] font-bold leading-tight tracking-tight text-ink sm:text-[36px]">
				Student Skill Gap Analyzer
			</h1>
			<p class="mt-4 text-[13px] leading-relaxed text-ink-body">
				Paste real job descriptions, see where you shine or need a boost, and get a calm roadmap you can
				follow—built for demos and busy semesters.
			</p>
		</div>
		<div class="flex flex-wrap gap-3">
			<a class="btn-primary" href="/register">Create account</a>
			<a class="btn-secondary" href="/login">Log in</a>
		</div>
	</header>

	<section class="mt-12 grid gap-4 sm:grid-cols-3 sm:gap-4">
		<div class="card-interactive flex flex-col">
			<div
				class="mb-4 flex h-10 w-10 items-center justify-center rounded-icon bg-sage-ghost text-[13px] font-bold text-sage"
			>
				1
			</div>
			<h2 class="text-[16px] font-bold text-ink">Profile</h2>
			<p class="mt-2 text-[12px] leading-relaxed text-ink-muted">Skills, school, and experience in one form.</p>
		</div>
		<div class="card-interactive flex flex-col">
			<div
				class="mb-4 flex h-10 w-10 items-center justify-center rounded-icon bg-sage-ghost text-[13px] font-bold text-sage"
			>
				2
			</div>
			<h2 class="text-[16px] font-bold text-ink">Job posts</h2>
			<p class="mt-2 text-[12px] leading-relaxed text-ink-muted">One or many postings—parsed and saved together.</p>
		</div>
		<div class="card-interactive flex flex-col">
			<div
				class="mb-4 flex h-10 w-10 items-center justify-center rounded-icon bg-sage-ghost text-[13px] font-bold text-sage"
			>
				3
			</div>
			<h2 class="text-[16px] font-bold text-ink">Gaps → path</h2>
			<p class="mt-2 text-[12px] leading-relaxed text-ink-muted">Gap view, then milestones you can check off.</p>
		</div>
	</section>

	<div class="mt-10 rounded-card bg-sage p-6 text-white shadow-sagebtn sm:p-8">
		<p class="text-[12px] font-medium text-white/85">Anchor card</p>
		<p class="mt-1 text-[18px] font-bold leading-snug">Everything stays calm until you’re ready for the next step.</p>
		<p class="mt-2 max-w-lg text-[13px] leading-relaxed text-white/90">
			No urgent reds by default—just sage accents, soft cards, and a clear path from profile to roadmap.
		</p>
	</div>
</main>
