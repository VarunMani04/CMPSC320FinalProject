<svelte:head>
	<title>Profile · PostingPal</title>
</svelte:head>

<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import type { PageData } from "./$types";

	let { data }: { data: PageData } = $props();

	type Skill = { id?: number; name: string; proficiency: string };

	let full_name = $state("");
	let education = $state("");
	let experience = $state("");
	let skills = $state<Skill[]>([]);
	let message = $state<string | null>(null);
	let err = $state<string | null>(null);
	let saving = $state(false);
	let resumeParsing = $state(false);
	let resumeFileKey = $state(0);

	$effect(() => {
		if (data.profile) {
			full_name = data.profile.full_name;
			education = data.profile.education;
			experience = data.profile.experience;
			skills = data.profile.skills?.length
				? data.profile.skills.map((s: Skill) => ({ ...s }))
				: [{ name: "", proficiency: "beginner" }];
		}
	});

	function addSkill() {
		skills = [...skills, { name: "", proficiency: "beginner" }];
	}

	function removeSkill(index: number) {
		skills = skills.filter((_, i) => i !== index);
		if (!skills.length) skills = [{ name: "", proficiency: "beginner" }];
	}

	async function fillFromResume(pdf: File | undefined) {
		if (!pdf) {
			err = "Choose a PDF résumé first.";
			return;
		}
		message = null;
		err = null;
		resumeParsing = true;
		const fd = new FormData();
		fd.append("file", pdf);
		const res = await fetch("/api/profile/parse-resume", {
			method: "POST",
			credentials: "include",
			body: fd
		});
		resumeParsing = false;
		const body = (await res.json().catch(() => ({}))) as {
			error?: string;
			full_name?: string;
			education?: string;
			experience?: string;
			skills?: { name: string; proficiency: string }[];
		};
		if (!res.ok) {
			err = body.error || "Could not parse résumé";
			return;
		}
		if (body.full_name != null && body.full_name !== "") full_name = body.full_name;
		if (body.education != null && body.education !== "") education = body.education;
		if (body.experience != null && body.experience !== "") experience = body.experience;
		if (body.skills?.length) {
			skills = body.skills.map((s) => ({
				name: s.name || "",
				proficiency: s.proficiency || "beginner"
			}));
		}
		message = "Loaded from résumé—review the fields and click Save profile.";
		resumeFileKey += 1;
	}

	async function save(e: Event) {
		e.preventDefault();
		message = null;
		err = null;
		saving = true;
		const body = {
			full_name,
			education,
			experience,
			skills: skills
				.map((s) => ({
					name: s.name.trim(),
					proficiency: s.proficiency
				}))
				.filter((s) => s.name.length > 0)
		};
		const res = await fetch("/api/profile", {
			method: "PUT",
			credentials: "include",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(body)
		});
		saving = false;
		if (!res.ok) {
			const raw = await res.text();
			try {
				const b = JSON.parse(raw) as { error?: string };
				err = b.error || raw || "Save failed";
			} catch {
				err = raw || "Save failed";
			}
			return;
		}
		message = "Saved.";
		await invalidateAll();
	}
</script>

<div class="mx-auto max-w-2xl">
	<h1 class="page-title">Your profile</h1>
		<p class="page-sub">This is what the gap analyzer compares to job postings.</p>

	{#if data.error}
		<p class="mt-4 rounded-badge bg-negative-bg px-3 py-2 text-[12px] font-medium text-negative">{data.error}</p>
	{:else}
		<form class="card mt-8 space-y-5 shadow-card" onsubmit={save}>
			<div class="rounded-btn bg-card-alt p-4">
				<p class="label">Optional · PDF résumé</p>
				<p class="mt-1 text-[12px] leading-relaxed text-ink-muted">
					Upload a PDF (max 4&nbsp;MB) to pre-fill the fields below. Review and edit before saving.
				</p>
				<label class="btn-secondary mt-3 inline-flex cursor-pointer text-2xs">
					{resumeParsing ? "Parsing…" : "Choose PDF"}
					<input
						key={resumeFileKey}
						class="sr-only"
						type="file"
						accept=".pdf,application/pdf"
						disabled={resumeParsing}
						onchange={(e) => {
							const f = e.currentTarget.files?.[0];
							void fillFromResume(f);
							e.currentTarget.value = "";
						}}
					/>
				</label>
			</div>

			<div>
				<label class="label" for="full_name">Full name</label>
				<input id="full_name" class="field" bind:value={full_name} required />
			</div>
			<div>
				<label class="label" for="education">Education</label>
				<textarea id="education" class="field min-h-[100px]" bind:value={education}></textarea>
			</div>
			<div>
				<label class="label" for="experience">Experience & projects</label>
				<textarea id="experience" class="field min-h-[120px]" bind:value={experience}></textarea>
			</div>

			<div>
				<div class="flex items-center justify-between">
					<p class="label">Skills</p>
					<button type="button" class="btn-ghost text-xs" onclick={addSkill}>+ Add skill</button>
				</div>
				<ul class="mt-2 space-y-3">
					{#each skills as s, i (i)}
						<li
							class="flex flex-wrap items-end gap-2 rounded-card border-0 bg-card-alt p-4 shadow-none"
						>
							<div class="min-w-[140px] flex-1">
								<label class="text-[11px] text-ink-label" for={"sn" + i}>Name</label>
								<input id={"sn" + i} class="field" bind:value={s.name} placeholder="e.g. Python" />
							</div>
							<div class="w-40">
								<label class="text-[11px] text-ink-label" for={"sp" + i}>Level</label>
								<select id={"sp" + i} class="field" bind:value={s.proficiency}>
									<option value="beginner">Beginner</option>
									<option value="intermediate">Intermediate</option>
									<option value="advanced">Advanced</option>
								</select>
							</div>
							<button type="button" class="btn-ghost text-2xs text-negative" onclick={() => removeSkill(i)}>
								Remove
							</button>
						</li>
					{/each}
				</ul>
			</div>

			{#if err}
				<p class="rounded-badge bg-negative-bg px-3 py-2 text-[12px] font-medium text-negative">{err}</p>
			{/if}
			{#if message}
				<p class="rounded-badge bg-positive-bg px-3 py-2 text-[12px] font-medium text-positive">{message}</p>
			{/if}

			<button class="btn-primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save profile"}</button>
		</form>
	{/if}
</div>
