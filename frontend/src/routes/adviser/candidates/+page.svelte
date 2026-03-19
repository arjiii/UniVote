<script>
	import { onMount } from 'svelte';
	import { admin, adviser } from '$lib/api.js';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import { selectedElectionId } from '$lib/stores/election.js';

	/** @type {any[]} */
	let elections = $state([]);
	/** @type {any[]} */
	let candidates = $state([]);
	/** @type {any[]} */
	let partylists = $state([]);

	let newCandidate = $state({ student_id: '', position: '', partylist_id: '' });
	let isSubmitting = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');

	async function loadElections() {
		try {
			const res = await admin.getElections();
			elections = res.data || [];
		} catch (err) { console.error('Failed to load elections:', err); }
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
		} catch (err) { console.error('Failed to load data:', err); }
	}

	onMount(async () => {
		await loadElections();
		if ($selectedElectionId) await loadData();
	});

	$effect(() => { if ($selectedElectionId) { loadData(); } });

	/** @param {SubmitEvent} e */
	async function handleAddCandidate(e) {
		e.preventDefault();
		if (!newCandidate.student_id || !newCandidate.position || !$selectedElectionId) {
			errorMessage = 'Please fill in all required fields.'; return;
		}
		isSubmitting = true;
		errorMessage = ''; successMessage = '';
		try {
			await adviser.createCandidate($selectedElectionId, {
				student_id: newCandidate.student_id,
				position: newCandidate.position,
				partylist_id: newCandidate.partylist_id || null
			});
			newCandidate = { student_id: '', position: '', partylist_id: '' };
			successMessage = 'Candidate added successfully!';
			await loadData();
		} catch (/** @type {any} */ err) {
			errorMessage = err.message || 'Failed to add candidate.';
		} finally {
			isSubmitting = false;
		}
	}

	/** @param {string} name */
	function getMonogram(name) {
		return (name || '??').split(' ').slice(0, 2).map(/** @param {string} w */ w => w[0]?.toUpperCase() || '').join('');
	}

	// Group candidates by position
	const groupedCandidates = $derived(() => {
		/** @type {Record<string, any[]>} */
		const g = {};
		candidates.forEach(c => {
			const pos = c.position || 'Unassigned';
			if (!g[pos]) g[pos] = [];
			g[pos].push(c);
		});
		return g;
	});

	const selectedElection = $derived(() => elections.find(/** @param {any} e */ e => e.id === $selectedElectionId));
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

<svelte:head>
	<title>Candidates Management | UniVote</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Adviser</p>
			<h1 class="text-2xl font-semibold text-stone-900">Candidates</h1>
			<p class="text-stone-500 text-sm mt-0.5">Enlist and manage official candidates for the selected election.</p>
		</div>

		<div class="flex items-center gap-3 bg-white border border-stone-200 rounded-xl px-4 py-2.5 w-fit">
			<label for="election-select" class="text-[10px] font-semibold text-stone-400 uppercase tracking-widest whitespace-nowrap">Election</label>
			<select 
				id="election-select"
				bind:value={$selectedElectionId}
				class="bg-transparent border-none text-sm font-semibold text-stone-900 focus:outline-none cursor-pointer min-w-[180px]"
			>
				<option value="" disabled>Select election</option>
				{#each elections as election}
					<option value={election.id}>{election.name}</option>
				{/each}
			</select>
		</div>
	</div>

	{#if !$selectedElectionId}
		<div class="flex flex-col items-center justify-center py-24 text-center border-2 border-dashed border-stone-200 rounded-2xl">
			<div class="w-14 h-14 bg-stone-100 rounded-2xl flex items-center justify-center mb-4">
				<svg class="w-7 h-7 text-stone-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
			</div>
			<h2 class="font-semibold text-stone-900 mb-1">No Election Selected</h2>
			<p class="text-stone-400 text-sm max-w-xs">Select an election from the dropdown above to view and manage candidates.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
			<!-- Enlistment Form -->
			<div class="lg:col-span-4">
				<div class="bg-white rounded-2xl border border-stone-200 p-6 sticky top-6">
					<div class="flex items-center gap-3 mb-5">
						<div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
							<svg class="w-4 h-4 text-stone-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
						</div>
						<h2 class="text-sm font-semibold text-stone-900">Enlist Candidate</h2>
					</div>

					<form onsubmit={handleAddCandidate} class="space-y-4">
						<div>
							<label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5" for="student-id">Student ID</label>
							<input id="student-id" type="text" bind:value={newCandidate.student_id} placeholder="e.g. 2021-00123" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 placeholder-stone-300 font-mono focus:outline-none focus:border-stone-900 focus:ring-[3px] focus:ring-stone-900/[0.06] transition-all"/>
							<p class="text-[10px] text-stone-400 mt-1">Must exist in the voter database.</p>
						</div>

						<div>
							<label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5" for="position">Position</label>
							<input id="position" type="text" bind:value={newCandidate.position} placeholder="e.g. President" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 placeholder-stone-300 focus:outline-none focus:border-stone-900 focus:ring-[3px] focus:ring-stone-900/[0.06] transition-all"/>
						</div>

						<div>
							<label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5" for="party">Partylist</label>
							<select id="party" bind:value={newCandidate.partylist_id} class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 cursor-pointer focus:outline-none focus:border-stone-900 focus:ring-[3px] focus:ring-stone-900/[0.06] transition-all">
								<option value="">Independent</option>
								{#each partylists as party}
									<option value={party.id}>{party.name}</option>
								{/each}
							</select>
						</div>

						{#if errorMessage}
							<div class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
								<svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
								{errorMessage}
							</div>
						{/if}

						{#if successMessage}
							<div class="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold flex items-center gap-2">
								<svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
								{successMessage}
							</div>
						{/if}

						<button type="submit" disabled={isSubmitting} class="w-full bg-stone-900 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-800 active:scale-[0.99] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
							{#if isSubmitting}
								<LoadingSpinner />
								Adding...
							{:else}
								<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/></svg>
								Enlist Candidate
							{/if}
						</button>
					</form>
				</div>
			</div>

			<!-- Candidate Roster -->
			<div class="lg:col-span-8 space-y-5">
				<div class="flex items-center justify-between">
					<h2 class="text-sm font-semibold text-stone-900">Official Roster</h2>
					<span class="text-xs font-semibold text-stone-400 bg-stone-100 px-3 py-1 rounded-lg">{candidates.length} registered</span>
				</div>

				{#if candidates.length === 0}
					<div class="flex flex-col items-center justify-center py-20 text-center border-2 border-dashed border-stone-200 rounded-2xl">
						<div class="w-12 h-12 bg-stone-100 rounded-2xl flex items-center justify-center mb-3">
							<svg class="w-6 h-6 text-stone-300" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
						</div>
						<p class="font-semibold text-stone-600 text-sm">No candidates yet</p>
						<p class="text-stone-400 text-xs mt-0.5">Use the form to enlist the first candidate.</p>
					</div>
				{:else}
					{#each Object.entries(groupedCandidates()) as [position, list]}
						<div class="bg-white rounded-2xl border border-stone-200 overflow-hidden">
							<div class="px-5 py-3 border-b border-stone-100 flex items-center justify-between bg-stone-50">
								<div class="flex items-center gap-2">
									<div class="w-6 h-6 bg-stone-200 rounded-md flex items-center justify-center">
										<svg class="w-3 h-3 text-stone-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
									</div>
									<h3 class="text-sm font-semibold text-stone-900 capitalize">{position}</h3>
								</div>
								<span class="text-[10px] font-semibold text-stone-400 uppercase tracking-widest">{list.length} candidate{list.length !== 1 ? 's' : ''}</span>
							</div>

							<div class="p-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
								{#each list as candidate}
									{@const name = candidate.students?.full_name || 'Unknown'}
									{@const partyName = candidate.partylist_id ? (partylists.find(/** @param {any} p */ p => p.id === candidate.partylist_id)?.name || 'Unknown Party') : 'Independent'}
									<div class="flex items-center gap-3.5 p-4 rounded-xl bg-stone-50 border border-stone-100 hover:bg-white hover:border-stone-300 transition-all">
										<div class="w-10 h-10 bg-stone-200 text-stone-700 rounded-xl flex items-center justify-center font-semibold text-sm shrink-0">
											{getMonogram(name)}
										</div>
										<div class="flex-1 min-w-0">
											<p class="font-semibold text-stone-900 text-sm truncate">{name}</p>
											<p class="text-[10px] font-semibold text-stone-500 uppercase tracking-wide mt-0.5 truncate">{partyName}</p>
											<p class="text-[10px] font-mono text-stone-400 mt-0.5">{candidate.students?.student_id}</p>
										</div>

										{#if isModifiable()}
											<button 
												onclick={() => handleDeleteCandidate(candidate.id)} 
												class="p-2 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
												title="Delete Candidate"
											>
												<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
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
