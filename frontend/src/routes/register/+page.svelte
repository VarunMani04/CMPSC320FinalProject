<svelte:head>
	<title>Register · PostingPal</title>
</svelte:head>

<script lang="ts">
	import { goto } from "$app/navigation";

	let email = $state("");
	let password = $state("");
	let otp = $state("");
	let challengeId = $state<string | null>(null);
	let step = $state<1 | 2>(1);
	let error = $state<string | null>(null);
	let loading = $state(false);

	async function submitRegister(e: Event) {
		e.preventDefault();
		error = null;
		loading = true;
		const res = await fetch("/api/auth/register", {
			method: "POST",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ email, password })
		});
		loading = false;
		if (!res.ok) {
			const b = await res.json().catch(() => ({}));
			error = (b as { error?: string }).error || "Could not register";
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
		await goto("/app/profile");
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
	<h1 class="page-title mt-6">Create your account</h1>
	<p class="page-sub">Takes a minute—then you’ll verify your email and set up your profile.</p>

	{#if step === 1}
		<form class="card mt-8 space-y-5 shadow-card" onsubmit={submitRegister}>
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
					autocomplete="new-password"
					minlength="8"
					bind:value={password}
					required
				/>
				<p class="mt-1 text-[11px] text-ink-label">At least 8 characters.</p>
			</div>
			{#if error}
				<p class="rounded-badge bg-negative-bg px-3 py-2 text-[12px] font-medium text-negative">{error}</p>
			{/if}
			<button class="btn-primary w-full" type="submit" disabled={loading}>
				{loading ? "Sending code…" : "Create account"}
			</button>
		</form>
	{:else}
		<form class="card mt-8 space-y-5 shadow-card" onsubmit={submitOtp}>
			<p class="text-[12px] leading-relaxed text-ink-muted">
				Enter the <strong class="text-ink-body">6-digit code</strong> we emailed to <strong class="text-ink-body">{email}</strong>.
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
				{loading ? "Verifying…" : "Verify and continue"}
			</button>
			<button type="button" class="btn-secondary w-full text-2xs" disabled={loading} onclick={resend}>
				Resend code
			</button>
		</form>
	{/if}

	<p class="mt-8 text-center text-[12px] text-ink-muted">
		Already have an account?
		<a class="link-quiet" href="/login">Log in</a>
	</p>
</main>
