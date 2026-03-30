<script>
	import { onMount } from 'svelte';
	import { admin, adviser } from '$lib/api.js';
	import { selectedElectionId } from '$lib/stores/election.js';
	import { POSITION_ORDER, sortPositions } from '$lib/constants.js';

	/** @type {any[]} */
	let elections = $state([]);
	/** @type {any[]} */
	let candidates = $state([]);
	/** @type {any[]} */
	let partylists = $state([]);

	let newCandidate = $state({ student_id: '', position: '', partylist_id: '' });
	let customPosition = $state('');
	let isSubmitting = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');

	async function loadElections() {
		try {
			const res = await adviser.getElections();
			elections = res.data || [];
		} catch (err) {
			console.error('Failed to load elections:', err);
		}
	}

	async function loadData() {
		if (!$selectedElectionId) return;
		try {
			const [pRes, cRes] = await Promise.all([
				adviser.getPartylists($selectedElectionId),
				adviser.getCandidates($selectedElectionId)
			]);
			partylists = pRes.data || [];
			candidates = cRes.data || [];
		} catch (err) {
			console.error('Failed to load data:', err);
		}
	}

	onMount(async () => {
		await loadElections();
		if ($selectedElectionId) await loadData();
	});

	$effect(() => {
		if ($selectedElectionId) {
			loadData();
		}
	});

	/** @param {SubmitEvent} e */
	async function handleAddCandidate(e) {
		e.preventDefault();
		if (!newCandidate.student_id || !newCandidate.position || !$selectedElectionId) {
			errorMessage = 'Please fill in all required fields.';
			return;
		}
		isSubmitting = true;
		errorMessage = '';
		successMessage = '';
		try {
			const finalPosition =
				newCandidate.position === 'Other' ? customPosition : newCandidate.position;
			if (!finalPosition) {
				errorMessage = 'Please provide a position name.';
				isSubmitting = false;
				return;
			}

			await adviser.createCandidate($selectedElectionId, {
				student_id: newCandidate.student_id,
				position: finalPosition,
				partylist_id: newCandidate.partylist_id || null
			});
			newCandidate = { student_id: '', position: '', partylist_id: '' };
			customPosition = '';
			successMessage = 'Candidate added successfully!';
			await loadData();
		} catch (/** @type {any} */ err) {
			errorMessage = err.message || 'Failed to add candidate.';
		} finally {
			isSubmitting = false;
		}
	}

	// Group candidates by position and sort the positions
	const groupedCandidates = $derived(() => {
		/** @type {Record<string, any[]>} */
		const g = {};
		candidates.forEach((c) => {
			const pos = c.position || 'Unassigned';
			if (!g[pos]) g[pos] = [];
			g[pos].push(c);
		});

		const sortedKeys = sortPositions(Object.keys(g));
		/** @type {Record<string, any[]>} */
		const sortedG = {};
		sortedKeys.forEach((key) => {
			sortedG[key] = g[key];
		});
		return sortedG;
	});

	const selectedElection = $derived(() =>
		elections.find(/** @param {any} e */ (e) => e.id === $selectedElectionId)
	);
	const isModifiable = $derived(() => selectedElection()?.status === 'upcoming');

	/** @param {string} id */
	async function handleDeleteCandidate(id) {
		if (!confirm('Are you sure you want to delete this candidate?')) return;
		try {
			await adviser.deleteCandidate(id);
			successMessage = 'Candidate deleted successfully.';
			await loadData();
		} catch (/** @type {any} */ err) {
			errorMessage = err.message || 'Failed to delete candidate.';
		}
	}
</script>

<svelte:head><title>Candidates | UniVote</title></svelte:head>

<div class="dash">
	<div class="dash-header">
		<div>
			<p class="dash-eyebrow"><span class="prefix">Pages /</span> Candidates</p>
			<h1 class="dash-title">Candidates</h1>
		</div>
		<div style="display:flex;align-items:center;gap:0.75rem;">
			<label for="election-select" class="field-label" style="margin-bottom:0;line-height:1;"
				>Election</label
			>
			<select
				id="election-select"
				bind:value={$selectedElectionId}
				class="input-base"
				style="width:220px;padding:0.375rem 0.75rem;font-size:0.8125rem;"
			>
				<option value="" disabled>Select Election...</option>
				{#each elections as election}
					<option value={election.id}>{election.name}</option>
				{/each}
			</select>
		</div>
	</div>

	{#if !$selectedElectionId}
		<div class="empty-state">
			Please select an election from the dropdown above to manage candidates.
		</div>
	{:else}
		<div class="bento-grid" style="grid-template-columns: 1fr 2.5fr; gap: 1rem;">
			<!-- Add Candidate Form -->
			<div class="admin-card" style="padding:1.25rem;height:fit-content;">
				<div style="margin-bottom:1.25rem;">
					<h2 style="font-size:0.875rem;font-weight:600;color:var(--text-main);">Add Candidate</h2>
				</div>

				<form onsubmit={handleAddCandidate} style="display:flex;flex-direction:column;gap:1rem;">
					<div>
						<label class="field-label" for="student-id">Student ID *</label>
						<input
							id="student-id"
							type="text"
							bind:value={newCandidate.student_id}
							class="input-base"
							placeholder="e.g. 2021-00123"
						/>
					</div>

					<div>
						<label class="field-label" for="position">Position *</label>
						<select id="position" bind:value={newCandidate.position} class="input-base">
							<option value="" disabled>Select Role...</option>
							{#each POSITION_ORDER as pos}
								<option value={pos}>{pos}</option>
							{/each}
							<option value="Other">Other (Custom)</option>
						</select>
					</div>

					{#if newCandidate.position === 'Other'}
						<div>
							<label class="field-label" for="custom-position">Custom Position</label>
							<input
								id="custom-position"
								type="text"
								bind:value={customPosition}
								class="input-base"
								placeholder="e.g. Sgt. at Arms"
							/>
						</div>
					{/if}

					<div>
						<label class="field-label" for="party">Partylist</label>
						<select id="party" bind:value={newCandidate.partylist_id} class="input-base">
							<option value="">Independent</option>
							{#each partylists as party}
								<option value={party.id}>{party.name}</option>
							{/each}
						</select>
					</div>

					{#if errorMessage}
						<div
							style="color:var(--status-danger-fg);font-size:0.75rem;padding:0.5rem;background:var(--status-danger-bg);border-radius:4px;"
						>
							{errorMessage}
						</div>
					{/if}
					{#if successMessage}
						<div
							style="color:var(--status-success-fg);font-size:0.75rem;padding:0.5rem;background:var(--status-success-bg);border-radius:4px;"
						>
							{successMessage}
						</div>
					{/if}

					<button
						type="submit"
						disabled={isSubmitting || !isModifiable()}
						class="btn-primary"
						style="margin-top:0.5rem;"
					>
						{isSubmitting ? 'Adding...' : 'Add Candidate'}
					</button>
				</form>
			</div>

			<!-- Candidates List -->
			<div class="admin-card" style="padding:1.5rem;display:flex;flex-direction:column;gap:1.5rem;">
				<div
					style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border-subtle);padding-bottom:0.75rem;"
				>
					<h2 style="font-size:0.875rem;font-weight:600;color:var(--text-main);">
						Registered Candidates
					</h2>
					<span class="pill pill-neutral">{candidates.length} candidates</span>
				</div>

				{#if candidates.length === 0}
					<div class="empty-state" style="border:none;">
						No candidates registered for this election yet.
					</div>
				{:else}
					{#each Object.entries(groupedCandidates()) as [position, list]}
						<div>
							<h3 class="section-label" style="margin-bottom:0.75rem;">
								{position} ({list.length})
							</h3>
							<div class="bento-grid bento-2col" style="gap:0.75rem;">
								{#each list as candidate}
									{@const name = candidate.students?.full_name || 'Unknown'}
									{@const partyName = candidate.partylist_id
										? partylists.find((p) => p.id === candidate.partylist_id)?.name ||
											'Unknown Partylist'
										: 'Independent'}
									<div
										class="profile-card"
										style="padding:0.75rem 1rem;display:flex;align-items:center;gap:1rem;border-color:var(--border-subtle);box-shadow:none;"
									>
										<div class="avatar-initial" style="width:36px;height:36px;flex-shrink:0;">
											{(name || '??')
												.split(' ')
												.slice(0, 2)
												.map(/** @param {string} w */ (w) => w[0]?.toUpperCase() || '')
												.join('')}
										</div>
										<div style="flex:1;min-width:0;">
											<p
												style="font-size:0.8125rem;font-weight:600;color:var(--text-main);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
												title={name}
											>
												{name}
											</p>
											<p style="font-size:0.6875rem;color:var(--text-muted);margin-top:0.125rem;">
												{partyName}
											</p>
										</div>
										{#if isModifiable()}
											<button
												onclick={() => handleDeleteCandidate(candidate.id)}
												class="btn-icon-danger flex-shrink-0"
												title="Remove candidate"
											>
												<svg
													class="h-4 w-4"
													fill="none"
													stroke="currentColor"
													stroke-width="2"
													viewBox="0 0 24 24"
													><path
														stroke-linecap="round"
														stroke-linejoin="round"
														d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
													/></svg
												>
											</button>
										{/if}
									</div>
								{/each}
							</div>
						</div>
					{/each}
				{/if}
			</div>
		</div>
	{/if}
</div>
