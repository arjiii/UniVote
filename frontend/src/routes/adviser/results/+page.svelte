<script>
	import { onMount } from 'svelte';
	import { admin, adviser } from '$lib/api.js';
	import { selectedElectionId } from '$lib/stores/election.js';
	import { sortPositions, calculateWinners } from '$lib/constants.js';

	const SSE_BASE = 'http://localhost:8000/api/results/stream';

	/** @type {any[]} */
	let elections = $state([]);
	/** @type {any[]} */
	let candidates = $state([]);
	/** @type {Record<string, any>} */
	let liveResults = $state({});
	let electionStatus = $state('');
	let sseConnected = $state(false);

	/** @type {EventSource | null} */
	let eventSource = null;

	async function loadElections() {
		try {
			const res = await admin.getElections();
			elections = res.data || [];
		} catch (err) {
			console.error('Failed to load elections:', err);
		}
	}

	async function loadCandidates(electionId = $selectedElectionId) {
		if (!electionId) return;
		try {
			const cRes = await adviser.getCandidates(electionId);
			candidates = cRes.data || [];
		} catch (err) {
			console.error('Failed to load candidates:', err);
		}
	}

	/** Close any existing SSE connection. */
	function closeSSE() {
		if (eventSource) {
			eventSource.close();
			eventSource = null;
			sseConnected = false;
		}
	}

	/**
	 * Open an SSE stream for the given election.
	 * @param {string} electionId
	 */
	function openSSE(electionId) {
		closeSSE();
		eventSource = new EventSource(`${SSE_BASE}/${electionId}`);
		eventSource.onopen = () => { sseConnected = true; };
		eventSource.onmessage = (e) => {
			try {
				const payload = JSON.parse(e.data);
				if (payload.tallies) {
					liveResults = payload.tallies;
					electionStatus = payload.status;
				} else {
					liveResults = payload;
				}
				sseConnected = true;
			} catch (err) {
				console.error('SSE parse error:', err);
			}
		};
		eventSource.onerror = () => {
			sseConnected = false;
			console.warn('SSE connection lost, retrying...');
		};
	}

	onMount(() => {
		async function init() {
			await loadElections();
			if ($selectedElectionId) {
				await loadCandidates($selectedElectionId);
				openSSE($selectedElectionId);
			}
		}
		init();

		// Cleanup SSE on component destroy
		return () => closeSSE();
	});

	$effect(() => {
		const id = $selectedElectionId;
		if (id) {
			loadCandidates(id);
			openSSE(id);
		} else {
			closeSSE();
			liveResults = {};
		}
	});

	/** @type {string[]} */
	const positions = $derived(sortPositions(Object.keys(liveResults)));

	let isCompleted = $derived(electionStatus === 'completed');
	let winnersData = $derived(isCompleted ? calculateWinners(liveResults, candidates) : {});

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
			<p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-1">Adviser</p>
			<h1 class="text-2xl font-semibold text-stone-900 dark:text-white">Live Results</h1>
			<div class="flex items-center gap-2 mt-1">
				<span class="relative flex h-2 w-2">
					<span class="animate-ping absolute inline-flex h-full w-full rounded-full {sseConnected ? 'bg-emerald-400' : 'bg-amber-400'} opacity-75"></span>
					<span class="relative inline-flex rounded-full h-2 w-2 {sseConnected ? 'bg-emerald-500' : 'bg-amber-500'}"></span>
				</span>
				<p class="text-stone-500 dark:text-stone-400 text-sm">{sseConnected ? 'Connected · Live' : 'Reconnecting...'}</p>
			</div>
		</div>

		<div class="flex items-center gap-3 bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl px-4 py-2.5 w-fit">
			<label for="election-select" class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 uppercase tracking-widest whitespace-nowrap">Election</label>
			<select 
				id="election-select"
				bind:value={$selectedElectionId}
				class="bg-transparent border-none text-sm font-semibold text-stone-900 dark:text-white focus:outline-none cursor-pointer min-w-[180px]"
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
			<h2 class="font-semibold text-stone-900 dark:text-white mb-1">No election selected</h2>
			<p class="text-stone-400 dark:text-stone-500 text-sm max-w-xs">Select an election from the dropdown to view live results.</p>
		</div>
	{:else if positions.length === 0}
		<div class="flex flex-col items-center justify-center py-20 text-center border-2 border-dashed border-stone-200 rounded-2xl">
			<div class="w-14 h-14 bg-stone-100 rounded-2xl flex items-center justify-center mb-4">
				<svg class="w-7 h-7 text-stone-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
			</div>
			<h2 class="font-semibold text-stone-900 dark:text-white mb-1">No votes yet</h2>
			<p class="text-stone-400 dark:text-stone-500 text-sm max-w-xs">No ballots have been cast for this election. Results will appear here automatically.</p>
		</div>

		{:else}
			{#if isCompleted}
				<div class="mb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
					<div class="flex items-center gap-3 mb-6">
						<div class="p-2 bg-brand-primary/10 dark:bg-brand-primary/20 rounded-xl text-brand-primary">
							<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
						</div>
						<div>
							<h2 class="text-xl font-bold text-stone-900 dark:text-white">Official Election Winners</h2>
							<p class="text-xs text-stone-500 font-medium mt-0.5">The final verified results for this election.</p>
						</div>
					</div>
					
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
						{#each positions as position}
							{#if winnersData[position] && winnersData[position].length > 0}
								<div class="card-themed p-5 border-l-4 border-l-brand-primary">
									<p class="text-[10px] font-bold tracking-widest uppercase text-stone-400 dark:text-stone-500 mb-3">{position}</p>
									<div class="space-y-3">
										{#each winnersData[position] as winner}
											<div class="flex items-center gap-3">
												<div class="w-10 h-10 rounded-full bg-stone-100 dark:bg-stone-800 flex items-center justify-center font-bold text-brand-primary text-sm shadow-inner">
													{winner.students?.full_name?.charAt(0) || '?'}
												</div>
												<div>
													<h3 class="text-sm font-bold text-stone-900 dark:text-white truncate max-w-[140px]">{winner.students?.full_name || 'Unknown'}</h3>
													<p class="text-[11px] text-stone-500 font-medium">{winner.partylists?.name || 'Independent'} • <span class="text-stone-700 dark:text-stone-300">{(liveResults[position] || {})[winner.id] || 0} votes</span></p>
												</div>
											</div>
										{/each}
									</div>
								</div>
							{/if}
						{/each}
					</div>
				</div>
				
				<div class="mb-6 flex items-center justify-between">
					<h2 class="text-lg font-bold text-stone-900 dark:text-white">Detailed Tally</h2>
				</div>
			{/if}

			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
				{#each positions as position, idx}
				{@const { entries, totalVotes } = getPositionResults(position)}
				<div class="bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-700 rounded-2xl p-5">
					<div class="flex items-center justify-between mb-4">
						<div class="flex items-center gap-3">
							<div class="w-6 h-6 bg-stone-200 dark:bg-stone-700 rounded-md flex items-center justify-center text-stone-600 dark:text-stone-300 text-xs font-semibold">{idx + 1}</div>
							<h2 class="text-sm font-semibold text-stone-900 dark:text-white capitalize">{position}</h2>
						</div>
						<span class="text-[10px] text-stone-400 dark:text-stone-500 font-semibold">{totalVotes} vote{totalVotes !== 1 ? 's' : ''}</span>
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
										<p class="text-sm font-medium text-stone-900 dark:text-white">{candidate.name}</p>
										<p class="text-xs text-stone-400 dark:text-stone-500">{candidate.party}</p>
									</div>
									<div class="flex items-center gap-2">
										<span class="text-xs font-semibold text-stone-900 dark:text-white">{candidate.votes}</span>
										<span class="text-[10px] text-stone-400 dark:text-stone-500 w-8 text-right">{pct}%</span>
									</div>
								</div>
								<div class="h-1.5 bg-stone-100 dark:bg-stone-800 rounded-full overflow-hidden">
									<div 
										class="h-full rounded-full transition-all duration-700 ease-out"
										style="background-color: {isLeading ? 'var(--text-main)' : 'var(--border-main)'}; width: {pct}%;"
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
