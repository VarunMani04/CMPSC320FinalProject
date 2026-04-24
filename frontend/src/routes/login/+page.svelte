<svelte:head>
	<title>Log in · PostingPal</title>
</svelte:head>

<script lang="ts">
	import { goto } from "$app/navigation";
	import { page } from "$app/stores";
	import { get } from "svelte/store";

	let email = $state("");
	let password = $state("");
	let otp = $state("");
	let challengeId = $state<string | null>(null);
	let step = $state<1 | 2>(1);
	let error = $state<string | null>(null);
	let loading = $state(false);

	async function submitPassword(e: Event) {
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
		const body = (await res.json()) as { otp_required?: boolean; challenge_id?: string };
		if (body.otp_required && body.challenge_id) {
			challengeId = body.challenge_id;
			step = 2;
			otp = "";
			return;
		}
		error = "Unexpected response from server.";
	}

	async function submitOtp(e: Event) {
		e.preventDefault();
		if (!challengeId) return;
		error = null;
		loading = true;
		const res = await fetch("/api/auth/verify-email-otp", {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ challenge_id: challengeId, code: otp.replace(/\s/g, "") })
		});
		loading = false;
		if (!res.ok) {
			const b = await res.json().catch(() => ({}));
			error = (b as { error?: string }).error || "Invalid code";
			return;
		}
		const next = get(page).url.searchParams.get("next") || "/app/dashboard";
		await goto(next);
	}

	async function resend() {
		if (!challengeId) return;
		error = null;
		loading = true;
		const res = await fetch("/api/auth/resend-email-otp", {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ challenge_id: challengeId })
		});
		loading = false;
		if (!res.ok) {
			const b = await res.json().catch(() => ({}));
			error = (b as { error?: string }).error || "Could not resend";
			return;
		}
		const body = (await res.json()) as { challenge_id?: string };
		if (body.challenge_id) challengeId = body.challenge_id;
	}
</script>

<main class="mx-auto flex min-h-screen max-w-md flex-col justify-center px-5 py-12">
	<a class="text-[12px] text-ink-muted transition hover:text-ink-body" href="/">← Back home</a>
	<h1 class="page-title mt-6">Welcome back</h1>
	<p class="page-sub">Log in to continue with PostingPal.</p>

	{#if step === 1}
		<form class="card mt-8 space-y-5 shadow-card" onsubmit={submitPassword}>
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
				{loading ? "Continuing…" : "Continue"}
			</button>
		</form>
	{:else}
		<form class="card mt-8 space-y-5 shadow-card" onsubmit={submitOtp}>
			<p class="text-[12px] leading-relaxed text-ink-muted">
				We sent a <strong class="text-ink-body">6-digit code</strong> to <strong class="text-ink-body">{email}</strong>.
				Enter it below to finish signing in.
			</p>
			<div>
				<label class="label" for="otp">Verification code</label>
				<input
					id="otp"
					class="field tracking-widest"
					type="text"
					inputmode="numeric"
					autocomplete="one-time-code"
					maxlength="8"
					bind:value={otp}
					placeholder="123456"
					required
				/>
			</div>
			{#if error}
				<p class="rounded-badge bg-negative-bg px-3 py-2 text-[12px] font-medium text-negative">{error}</p>
			{/if}
			<button class="btn-primary w-full" type="submit" disabled={loading}>
				{loading ? "Verifying…" : "Verify and sign in"}
			</button>
			<button
				type="button"
				class="btn-secondary w-full text-2xs"
				disabled={loading}
				onclick={resend}
			>
				Resend code
			</button>
			<button
				type="button"
				class="link-quiet w-full text-center text-[12px]"
				onclick={() => {
					step = 1;
					challengeId = null;
					error = null;
				}}
			>
				← Use a different email
			</button>
		</form>
	{/if}

	<p class="mt-8 text-center text-[12px] text-ink-muted">
		New here?
		<a class="link-quiet" href="/register">Create an account</a>
	</p>
</main>
