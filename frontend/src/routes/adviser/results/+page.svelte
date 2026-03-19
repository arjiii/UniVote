<script>
	import { onMount } from 'svelte';
	import { admin, adviser } from '$lib/api.js';
	import { selectedElectionId } from '$lib/stores/election.js';

	/** @type {any[]} */
	let elections = $state([]);
	/** @type {any[]} */
	let candidates = $state([]);
	/** @type {Record<string, any>} */
	let liveResults = $state({});

	async function loadElections() {
		try {
			const res = await admin.getElections();
			elections = res.data || [];
		} catch (err) {
			console.error('Failed to load elections:', err);
		}
	}

	async function loadResults() {
		if (!$selectedElectionId) return;
		try {
			const [cRes, lRes] = await Promise.all([
				adviser.getCandidates($selectedElectionId),
				adviser.getLiveResults($selectedElectionId)
			]);
			candidates = cRes.data || [];
			liveResults = lRes.data || {};
		} catch (err) {
			console.error('Failed to load results:', err);
		}
	}

	onMount(() => {
		async function init() {
			await loadElections();
			if ($selectedElectionId) await loadResults();
		}
		
		init();
		
		const interval = setInterval(() => {
			if ($selectedElectionId) loadResults();
		}, 5000);

		return () => clearInterval(interval);
	});

	$effect(() => {
		if ($selectedElectionId) {
			loadResults();
		}
	});

	/** @type {string[]} */
	const positions = $derived(Object.keys(liveResults));

	/**
	 * @param {string} candidateId
	 */
	function getCandidateInfo(candidateId) {
		const c = candidates.find(/** @param {any} c */ c => c.id === candidateId);
		return {
			name: c?.students?.full_name || 'Unknown',
			party: c?.partylists?.name || 'Independent'
		};
	}

	/**
	 * @param {string} position
	 */
	function getPositionResults(position) {
		const posVotes = liveResults[position] || {};
		const entries = Object.entries(posVotes).map(([candId, count]) => ({
			id: candId,
			...getCandidateInfo(candId),
			votes: Number(count)
		}));
		entries.sort((a, b) => b.votes - a.votes);
		const totalVotes = entries.reduce((sum, e) => sum + e.votes, 0);
		return { entries, totalVotes };
	}
</script>

<svelte:head>
	<title>Live Election Results | UniVote</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Adviser</p>
			<h1 class="text-2xl font-semibold text-stone-900">Live Results</h1>
			<div class="flex items-center gap-2 mt-1">
				<span class="relative flex h-2 w-2">
					<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
					<span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
				</span>
				<p class="text-stone-500 text-sm">Real-time ballot stream · auto-refreshes every 5s</p>
			</div>
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
				{:else}
					<option disabled>No elections found</option>
				{/each}
			</select>
		</div>
	</div>

	{#if !$selectedElectionId}
		<div class="flex flex-col items-center justify-center py-20 text-center border-2 border-dashed border-stone-200 rounded-2xl">
			<div class="w-14 h-14 bg-stone-100 rounded-2xl flex items-center justify-center mb-4">
				<svg class="w-7 h-7 text-stone-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
			</div>
			<h2 class="font-semibold text-stone-900 mb-1">No election selected</h2>
			<p class="text-stone-400 text-sm max-w-xs">Select an election from the dropdown to view live results.</p>
		</div>
	{:else if positions.length === 0}
		<div class="flex flex-col items-center justify-center py-20 text-center border-2 border-dashed border-stone-200 rounded-2xl">
			<div class="w-14 h-14 bg-stone-100 rounded-2xl flex items-center justify-center mb-4">
				<svg class="w-7 h-7 text-stone-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
			</div>
			<h2 class="font-semibold text-stone-900 mb-1">No votes yet</h2>
			<p class="text-stone-400 text-sm max-w-xs">No ballots have been cast for this election. Results will appear here automatically.</p>
		</div>
	{:else}
		<div class="space-y-5">
			{#each positions as position, idx}
				{@const { entries, totalVotes } = getPositionResults(position)}
				<div class="bg-white border border-stone-200 rounded-2xl p-5">
					<div class="flex items-center justify-between mb-4">
						<div class="flex items-center gap-3">
							<div class="w-6 h-6 bg-stone-200 rounded-md flex items-center justify-center text-stone-600 text-xs font-semibold">{idx + 1}</div>
							<h2 class="text-sm font-semibold text-stone-900 capitalize">{position}</h2>
						</div>
						<span class="text-[10px] text-stone-400 font-semibold">{totalVotes} vote{totalVotes !== 1 ? 's' : ''}</span>
					</div>
					<div class="space-y-3">
						{#each entries as candidate, ci}
							{@const pct = totalVotes > 0 ? Math.round((candidate.votes / totalVotes) * 100) : 0}
							{@const isLeading = ci === 0 && candidate.votes > 0}
							<div>
								<div class="flex items-center justify-between mb-1.5">
									<div class="flex items-center gap-2">
										{#if isLeading}
											<span class="w-4 h-4 bg-emerald-100 rounded-full flex items-center justify-center">
												<svg class="w-2.5 h-2.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
											</span>
										{/if}
										<p class="text-sm font-medium text-stone-900">{candidate.name}</p>
										<p class="text-xs text-stone-400">{candidate.party}</p>
									</div>
									<div class="flex items-center gap-2">
										<span class="text-xs font-semibold text-stone-900">{candidate.votes}</span>
										<span class="text-[10px] text-stone-400 w-8 text-right">{pct}%</span>
									</div>
								</div>
								<div class="h-1.5 bg-stone-100 rounded-full overflow-hidden">
									<div 
										class="h-full rounded-full transition-all duration-700 ease-out {isLeading ? 'bg-stone-900' : 'bg-stone-300'}"
										style="width: {pct}%"
									></div>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
