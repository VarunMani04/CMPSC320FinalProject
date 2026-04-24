<svelte:head>
	<title>PostingPal</title>
</svelte:head>

<main class="mx-auto flex min-h-screen max-w-5xl flex-col px-5 py-14 sm:px-8">
	<header class="flex flex-wrap items-end justify-between gap-8">
		<div class="max-w-xl">
			<p class="text-[12px] font-normal tracking-wide text-ink-muted">Career info you can trust</p>
			<h1 class="mt-2 text-[32px] font-bold leading-tight tracking-tight text-ink sm:text-[36px]">
				PostingPal
			</h1>
			<p class="mt-4 text-[13px] leading-relaxed text-ink-body">
				Paste real job descriptions, and get tailored advice you can follow.

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
			<p class="mt-2 text-[12px] leading-relaxed text-ink-muted">
				Your experience and credentials in one place 
			</p>
		</div>
		<div class="card-interactive flex flex-col">
			<div
				class="mb-4 flex h-10 w-10 items-center justify-center rounded-icon bg-sage-ghost text-[13px] font-bold text-sage"
			>
				2
			</div>
			<h2 class="text-[16px] font-bold text-ink">Job Posts</h2>
			<p class="mt-2 text-[12px] leading-relaxed text-ink-muted">One or many postings, parsed and saved together.</p>
		</div>
		<div class="card-interactive flex flex-col">
			<div
				class="mb-4 flex h-10 w-10 items-center justify-center rounded-icon bg-sage-ghost text-[13px] font-bold text-sage"
			>
				3
			</div>
			<h2 class="text-[16px] font-bold text-ink">Gap Analyzer</h2>
			<p class="mt-2 text-[12px] leading-relaxed text-ink-muted">
				See how you line up against your dream roles.
			</p>
		</div>
	</section>
</main>
