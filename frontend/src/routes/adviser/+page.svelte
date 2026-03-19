<script>
	import { onMount } from 'svelte';
	import { admin, adviser } from '$lib/api.js';
	import { selectedElectionId } from '$lib/stores/election.js';
	import { authSession } from '$lib/stores/auth.js';

	/** @type {any[]} */
	let elections = $state([]);
	let summary = $state({ candidates: 0, partylists: 0, totalVotes: 0 });

	async function loadSummary() {
		if (!$selectedElectionId) return;
		try {
			const [pRes, cRes, lRes] = await Promise.all([
				adviser.getPartylists($selectedElectionId),
				adviser.getCandidates($selectedElectionId),
				adviser.getLiveResults($selectedElectionId)
			]);
			const liveResults = lRes.data || {};
			let voteCount = 0;
			Object.values(liveResults).forEach(posVotes => {
				Object.values(/** @type {any} */(posVotes)).forEach(count => { voteCount += Number(count); });
			});
			summary = { partylists: (pRes.data || []).length, candidates: (cRes.data || []).length, totalVotes: voteCount };
		} catch (err) { console.error('Failed to load dashboard summary:', err); }
	}

	async function loadElections() {
		try {
			const res = await admin.getElections();
			elections = res.data || [];
			if (elections.length > 0 && !$selectedElectionId) { $selectedElectionId = elections[0].id; }
		} catch (err) { console.error('Failed to load elections:', err); }
	}

	onMount(async () => {
		await loadElections();
		if ($selectedElectionId) await loadSummary();
	});

	$effect(() => { if ($selectedElectionId) { loadSummary(); } });

	const navCards = [
		{ name: 'Candidates', path: '/adviser/candidates', desc: 'Manage and enlist election participants.', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
		{ name: 'Partylists', path: '/adviser/partylists', desc: 'Configure political organizations.', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
		{ name: 'Results', path: '/adviser/results', desc: 'Monitor real-time ballot counting.', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
		{ name: 'Audit Logs', path: '/adviser/audit', desc: 'Review all administrative activities.', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
	];
</script>

<svelte:head>
	<title>Adviser Overview | UniVote</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">

  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
    <div>
      <p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-1">Adviser</p>
      <h1 class="text-2xl font-semibold text-stone-900 dark:text-white">
        Hello, {$authSession?.full_name?.split(' ')[0] || 'Adviser'}
      </h1>
      <p class="text-stone-500 dark:text-stone-400 text-sm mt-0.5">Your election command center.</p>
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
        {/each}
      </select>
    </div>
  </div>

  <!-- Stats -->
  <div class="grid grid-cols-3 gap-4">
    {#each [{ label: 'Candidates', value: summary.candidates }, { label: 'Partylists', value: summary.partylists }, { label: 'Cast Ballots', value: summary.totalVotes }] as stat}
      <div class="bg-white dark:bg-stone-900 rounded-2xl border border-stone-200 dark:border-stone-700 p-5">
        <p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-2">{stat.label}</p>
        <p class="text-3xl font-semibold text-stone-900 dark:text-white">{stat.value}</p>
      </div>
    {/each}
  </div>

  <!-- Nav Cards -->
  <div>
    <p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-3">Management Console</p>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {#each navCards as card}
        <a 
          href={card.path}
          class="group bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-700 rounded-2xl p-5 hover:border-stone-300 dark:hover:border-stone-600 hover:-translate-y-[2px] hover:shadow-[0_8px_30px_-6px_rgba(0,0,0,0.08)] dark:hover:shadow-[0_8px_30px_-6px_rgba(0,0,0,0.3)] transition-all duration-200"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="w-10 h-10 bg-stone-100 dark:bg-stone-800 rounded-xl flex items-center justify-center group-hover:bg-stone-200 dark:group-hover:bg-stone-700 transition-colors">
              <svg class="w-5 h-5 text-stone-600 dark:text-stone-300" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d={card.icon}/>
              </svg>
            </div>
            <svg class="w-4 h-4 text-stone-300 dark:text-stone-600 group-hover:text-stone-600 dark:group-hover:text-stone-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M7 7h10v10"/></svg>
          </div>
          <h3 class="text-sm font-semibold text-stone-900 dark:text-white mb-0.5">{card.name}</h3>
          <p class="text-xs text-stone-500 dark:text-stone-400 leading-relaxed">{card.desc}</p>
        </a>
      {/each}
    </div>
  </div>

  <!-- Audit CTA -->
  <div class="bg-stone-900 dark:bg-stone-800 rounded-2xl p-7 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
    <div>
      <h2 class="text-base font-semibold text-white mb-1">Need to review activity?</h2>
      <p class="text-stone-400 text-sm">Every admin action is logged with precision timestamps.</p>
    </div>
    <a href="/adviser/audit" class="flex-shrink-0 px-5 py-2.5 bg-white text-stone-900 rounded-xl font-semibold text-xs hover:bg-stone-100 transition-colors">
      View Audit Logs
    </a>
  </div>
</div>
