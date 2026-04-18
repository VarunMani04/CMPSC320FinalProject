<script lang="ts">
	import type { Snippet } from "svelte";
	import { page } from "$app/stores";
	import LogoutButton from "$lib/components/LogoutButton.svelte";
	import type { LayoutData } from "./$types";

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	const firstName = $derived(data.user.email.split("@")[0] ?? "there");

	const links = [
		{ href: "/app/dashboard", label: "Overview", icon: "grid" },
		{ href: "/app/profile", label: "Profile", icon: "user" },
		{ href: "/app/jobs", label: "Job postings", icon: "doc" },
		{ href: "/app/gap", label: "Gap report", icon: "chart" },
		{ href: "/app/roadmap", label: "Roadmap", icon: "path" }
	] as const;
</script>

<div class="min-h-screen bg-canvas">
	<!-- Desktop: 72px icon rail -->
	<aside
		class="fixed bottom-0 left-0 top-0 z-30 hidden w-[72px] flex-col items-center border-r border-[#EEEEEE] bg-card py-6 sm:flex"
		aria-label="Main navigation"
	>
		<a
			href="/app/dashboard"
			class="flex h-10 w-10 items-center justify-center rounded-full bg-sage-ghost text-xs font-bold text-sage"
			title="Home"
		>
			SG
		</a>
		<nav class="mt-10 flex flex-col items-center gap-5">
			{#each links as link}
				<a
					href={link.href}
					title={link.label}
					class="flex h-10 w-10 items-center justify-center rounded-full transition-colors duration-150 {$page.url.pathname === link.href
						? 'bg-ink text-white shadow-card'
						: 'text-icon-muted hover:bg-card-alt'}"
				>
					{#if link.icon === "grid"}
						<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"
							><path
								d="M4 4h7v7H4V4zm9 0h7v7h-7V4zM4 13h7v7H4v-7zm9 0h7v7h-7v-7z"
							/></svg
						>
					{:else if link.icon === "user"}
						<svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M16 14a4 4 0 10-8 0M4 20a8 8 0 0116 0"
							/></svg
						>
					{:else if link.icon === "doc"}
						<svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M9 12h6m-6 4h6M7 4h7l3 3v13a2 2 0 01-2 2H7a2 2 0 01-2-2V6a2 2 0 012-2z"
							/></svg
						>
					{:else if link.icon === "chart"}
						<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
							<rect x="4" y="14" width="4" height="6" rx="1" />
							<rect x="10" y="10" width="4" height="10" rx="1" />
							<rect x="16" y="6" width="4" height="14" rx="1" />
						</svg>
					{:else}
						<svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24"
							><path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M4 19h16M6 17V9l4-4 4 4v8M14 9h4v8"
							/></svg
						>
					{/if}
				</a>
			{/each}
		</nav>
		<div class="mt-auto flex flex-col items-center gap-3 pb-1">
			<div
				class="flex h-9 w-9 items-center justify-center rounded-full bg-sage-ghost text-[11px] font-semibold text-sage"
				title={data.user.email}
			>
				{(data.user.email[0] ?? "?").toUpperCase()}
			</div>
			<LogoutButton />
		</div>
	</aside>

	<div class="flex min-h-screen flex-col sm:pl-[72px]">
		<header
			class="flex min-h-[72px] items-center justify-between gap-4 border-b border-transparent px-5 py-4 sm:px-8"
		>
			<div>
				<p class="text-[12px] font-normal text-ink-muted">Skill gap workspace</p>
				<p class="text-[18px] font-bold tracking-tight text-ink">Hi, {firstName}</p>
			</div>
			<div class="hidden items-center gap-2 sm:flex">
				<span class="max-w-[220px] truncate text-[12px] text-ink-label" title={data.user.email}>{data.user.email}</span>
			</div>
		</header>

		<!-- Mobile top bar -->
		<div class="border-b border-[#EEEEEE] bg-card px-4 py-3 sm:hidden">
			<div class="flex items-center justify-between gap-2">
				<span class="text-sm font-bold text-ink">SG</span>
				<LogoutButton />
			</div>
			<nav class="mt-3 flex gap-2 overflow-x-auto pb-1" aria-label="Main navigation">
				{#each links as link}
					<a
						href={link.href}
						class="shrink-0 rounded-btn px-3 py-1.5 text-2xs font-semibold {$page.url.pathname === link.href
							? 'bg-ink text-white'
							: 'bg-card-alt text-ink-body'}"
					>
						{link.label}
					</a>
				{/each}
			</nav>
		</div>

		<main class="flex-1 px-5 pb-12 pt-2 sm:px-8">
			<div class="mx-auto max-w-content">
				{@render children()}
			</div>
		</main>
	</div>
</div>
