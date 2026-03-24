<script>
	import { onMount } from 'svelte';
	import { admin, adviser } from '$lib/api.js';
	import { selectedElectionId } from '$lib/stores/election.js';
	import GlassCard from '$lib/components/GlassCard.svelte';
	import { sortPositions, calculateWinners } from '$lib/constants.js';
	import { BASE } from '$lib/api.js';

	const SSE_BASE = `${BASE}/api/results/adviser/stream`;

	/** @type {any[]} */
	let elections = $state([]);
	/** @type {any[]} */
	let candidates = $state([]);
	/** @type {Record<string, any>} */
	let liveResults = $state({});
	let electionStatus = $state('');
	let sseConnected = $state(false);
	let lastUpdated = $state('');

	/** @type {EventSource | null} */
	let eventSource = null;

	async function loadElections() {
		try {
			const res = await admin.getElections();
			elections = res.data || [];
		} catch (err) { console.error('Failed to load elections:', err); }
	}

	async function loadCandidates(electionId = $selectedElectionId) {
		if (!electionId) return;
		try {
			const cRes = await adviser.getCandidates(electionId);
			candidates = cRes.data || [];
		} catch (err) { console.error('Failed to load candidates:', err); }
	}

	function closeSSE() {
		if (eventSource) {
			eventSource.close();
			eventSource = null;
			sseConnected = false;
		}
	}

	/** @param {string} electionId */
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
				lastUpdated = new Date().toLocaleTimeString();
			} catch (err) { console.error('SSE parse error:', err); }
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

	/** @param {string} candidateId */
	function getCandidateInfo(candidateId) {
		const c = candidates.find(/** @param {any} c */ c => c.id === candidateId);
		return {
			name: c?.students?.full_name || 'Unknown',
			party: c?.partylists?.name || 'Independent'
		};
	}

	/** @param {string} position */
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

<svelte:head><title>Live Tally | UniVote Admin</title></svelte:head>

<GlassCard
	title={elections.find(e => e.id === $selectedElectionId)?.name || 'Live Results & Tally'}
	subtitle="Live Election Returns"
>
	{#snippet headerExtra()}
		<div style="display:flex;align-items:center;gap:1rem;">
			<!-- Live Indicator -->
			{#if $selectedElectionId}
				<div class="pill {sseConnected ? 'pill-success' : 'pill-warning'} pill-dot">
					{sseConnected ? (lastUpdated ? `Live Feed: ${lastUpdated}` : 'Connected') : 'Connecting...'}
				</div>
			{/if}

			<!-- Election Selector -->
			<div style="display:flex;align-items:center;gap:0.75rem;">
				<label for="election-select" class="field-label" style="margin-bottom:0;line-height:1;">Election</label>
				<select 
					id="election-select"
					bind:value={$selectedElectionId}
					class="input-base btn-sm"
					style="width:220px;"
				>
					<option value="" disabled>Select Session</option>
					{#each elections as election}
						<option value={election.id}>{election.name}</option>
					{/each}
				</select>
			</div>
		</div>
	{/snippet}

	{#if !$selectedElectionId}
		<div class="empty-state">Please select an election from the top right to view real-time results.</div>
	{:else if positions.length === 0}
		<div class="empty-state">No votes have been cast yet. Live tallies will appear here automatically.</div>
	{:else}
		<div style="display:flex;flex-direction:column;gap:2rem;">

			<!-- Certified Winners (if completed) -->
			{#if isCompleted}
				<div>
					<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;">
						<div class="pill pill-success pill-dot" style="font-size:0.8125rem;">Election Certified</div>
						<h2 style="font-size:1rem;font-weight:700;color:var(--text-main);">Official Winners</h2>
					</div>
					<div class="bento-grid bento-3col">
						{#each positions as position}
							{#if winnersData[position] && winnersData[position].length > 0}
								<div class="admin-card" style="padding:1.5rem;display:flex;flex-direction:column;align-items:center;text-align:center;">
									<p class="section-label" style="margin-bottom:1rem;">{position}</p>
									{#each winnersData[position] as winner}
										<div class="avatar-initial" style="width:64px;height:64px;border-radius:12px;font-size:1.5rem;margin-bottom:0.75rem;color:var(--brand-primary);border-color:var(--brand-glow);background-color:var(--bg-elevated);">
											{winner.students?.full_name?.charAt(0) || '?'}
										</div>
										<h3 style="font-size:1rem;font-weight:700;color:var(--text-main);">{winner.students?.full_name || 'Unknown'}</h3>
										<p style="font-size:0.6875rem;color:var(--text-muted);margin-top:0.25rem;">{winner.partylists?.name || 'Independent'}</p>
										<div class="pill pill-info" style="margin-top:0.75rem;">
											{(liveResults[position] || {})[winner.id] || 0} Votes
										</div>
									{/each}
								</div>
							{/if}
						{/each}
					</div>
				</div>
				<hr />
			{/if}

			<!-- Detailed Tally -->
			<div>
				<h2 style="font-size:1rem;font-weight:700;color:var(--text-main);margin-bottom:1rem;">Detailed Tally Returns</h2>
				
				<div class="bento-grid bento-2col">
					{#each positions as position, idx}
						{@const { entries, totalVotes } = getPositionResults(position)}
						<div class="admin-card" style="padding:1.5rem;">
							
							<!-- Header -->
							<div style="display:flex;align-items:flex-start;justify-content:space-between;border-bottom:1px solid var(--border-main);padding-bottom:1rem;margin-bottom:1.25rem;">
								<div style="display:flex;align-items:center;gap:0.75rem;">
									<div class="avatar-initial" style="width:24px;height:24px;border-radius:6px;font-size:0.6875rem;">{idx + 1}</div>
									<h2 style="font-size:0.875rem;font-weight:700;color:var(--text-main);">{position}</h2>
								</div>
								<div style="text-align:right;">
									<span class="section-label">{totalVotes} Total Votes</span>
								</div>
							</div>

							<!-- Bars -->
							<div style="display:flex;flex-direction:column;gap:1.25rem;">
								{#each entries as candidate, ci}
									{@const pct = totalVotes > 0 ? Math.round((candidate.votes / totalVotes) * 100) : 0}
									{@const isLeading = ci === 0 && candidate.votes > 0}
									<div>
										<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
											<div style="display:flex;align-items:center;gap:0.75rem;">
												<div class="avatar-initial" style="width:28px;height:28px;border-radius:6px;font-size:0.6875rem;{isLeading ? 'background-color:var(--status-success-bg);color:var(--status-success-fg);border-color:var(--status-success-bg);' : ''}">
													{candidate.name.charAt(0)}
												</div>
												<div>
													<p style="font-size:0.8125rem;font-weight:700;color:var(--text-main);line-height:1.2;">{candidate.name}</p>
													<p style="font-size:0.6875rem;color:var(--text-muted);margin-top:0.125rem;">{candidate.party}</p>
												</div>
											</div>
											<div style="text-align:right;">
												<span style="display:block;font-size:0.875rem;font-weight:700;color:var(--text-main);line-height:1.2;">{candidate.votes}</span>
												<span style="display:block;font-size:0.6875rem;color:var(--text-subtle);margin-top:0.125rem;">{pct}%</span>
											</div>
										</div>
										
										<!-- Progress Bar -->
										<div style="height:6px;background-color:var(--border-subtle);border-radius:3px;overflow:hidden;">
											<div 
												style="height:100%;border-radius:3px;background-color:{isLeading ? 'var(--status-success-fg)' : 'var(--text-muted)'};width:{pct}%;transition:width 1s ease-out;"
											></div>
										</div>
									</div>
								{/each}
							</div>

						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</GlassCard>
