<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import { page } from '$app/state';
  import { fade, fly } from 'svelte/transition';
  import { sortPositions, calculateWinners } from '$lib/constants.js';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';

  const SSE_BASE = 'http://localhost:8000/api/results/stream';

  let isLoading = $state(true);
  /** @type {Record<string, Record<string, number>>} */
  let results = $state({});
  /** @type {any[]} */
  let candidates = $state([]);
  let electionId = $state('');
  let electionStatus = $state('');
  let lastUpdated = $state('');

  /** @type {any[]} */
  let availableElections = $state([]);

  /** @type {EventSource | null} */
  let eventSource = null;

  /** @type {string[]} */
  const positions = $derived(sortPositions(Object.keys(results)));
  
  let isCompleted = $derived(electionStatus === 'completed');
  let winnersData = $derived(isCompleted ? calculateWinners(results, candidates) : {});

  onMount(() => {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    availableElections = session.elections || [];

    // Pick election from URL or default to first
    const urlId = page.url.searchParams.get('election');
    const defaultId = session.elections?.[0]?.id ?? '';
    const targetId = urlId || defaultId;

    if (targetId) {
      loadResults(targetId);
    } else {
      isLoading = false;
    }

    // Cleanup SSE on component destroy
    return () => closeSSE();
  });

  /** Close any existing SSE connection. */
  function closeSSE() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  }

  /**
   * Open an SSE stream for vote count updates.
   * @param {string} targetId
   */
  function openSSE(targetId) {
    closeSSE();
    eventSource = new EventSource(`${SSE_BASE}/${targetId}`);
    eventSource.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        if (payload.tallies) {
          results = payload.tallies;
          electionStatus = payload.status;
        } else {
          results = payload;
        }
        const now = new Date();
        lastUpdated = now.toLocaleTimeString();
      } catch (err) {
        console.error('SSE parse error:', err);
      }
    };
    eventSource.onerror = () => {
      // Browser will auto-reconnect; no action needed
      console.warn('SSE connection lost, retrying...');
    };
  }

  /**
   * @param {string} targetId
   */
  async function loadResults(targetId = electionId) {
    if (!targetId) return;
    electionId = targetId;

    try {
      const [resData, candData] = await Promise.all([
        studentApi.getResults(targetId),
        studentApi.getCandidates(targetId)
      ]);
      const fetched = resData.data || {};
      if (fetched.tallies) {
        results = fetched.tallies;
        electionStatus = fetched.status;
      } else {
        results = fetched;
      }
      candidates = candData.data || [];
      lastUpdated = new Date().toLocaleTimeString();
    } catch (err) {
      console.error('Failed to load results:', err);
    } finally {
      isLoading = false;
      // Open SSE stream after initial load so candidate names are resolved
      openSSE(targetId);
    }
  }

  /** @param {Event} e */
  async function handleElectionChange(e) {
    const newId = /** @type {HTMLSelectElement} */ (e.target).value;
    if (!newId) return;
    isLoading = true;
    await loadResults(newId);
  }

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
    const posVotes = results[position] || {};
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
  <title>Election Results | UniVote</title>
</svelte:head>

<div class="max-w-5xl mx-auto w-full px-5 md:px-8 py-8">

  <!-- Header -->
  <div class="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4" in:fly={{ y: -10, duration: 300 }}>
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-3 mb-1.5">
        <p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase">Select Election</p>
        <div class="relative inline-flex items-center group">
          <select 
            class="appearance-none bg-stone-100 dark:bg-stone-800 border-none rounded-full pl-4 pr-9 py-1.5 text-[10px] font-bold text-stone-600 dark:text-stone-300 uppercase tracking-widest focus:ring-2 focus:ring-stone-200 dark:focus:ring-stone-700 cursor-pointer transition-all hover:bg-stone-200 dark:hover:bg-stone-700 hover:text-stone-900 dark:hover:text-white"
            bind:value={electionId}
            onchange={handleElectionChange}
          >
            {#each availableElections as e}
              <option value={e.id}>{e.name}</option>
            {/each}
          </select>
          <div class="absolute right-3 pointer-events-none text-stone-400 group-hover:text-stone-600 dark:group-hover:text-stone-300 transition-colors">
            <svg class="w-2.5 h-2.5" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg>
          </div>
        </div>
      </div>
      <h1 class="text-2xl font-semibold text-stone-900 dark:text-white truncate">
        {availableElections.find(e => e.id === electionId)?.name || 'Election Results'}
      </h1>
    </div>
    <div class="flex items-center gap-3">
      <!-- SSE live indicator + last updated -->
      <div class="flex items-center gap-2 bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl px-3 py-2 shadow-sm">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span class="text-[10px] font-semibold text-stone-500 dark:text-stone-400 uppercase tracking-widest">
          {lastUpdated ? `Updated ${lastUpdated}` : 'Connecting...'}
        </span>
      </div>
    </div>
  </div>

  {#if isLoading}
    <div class="py-20 flex flex-col items-center justify-center gap-3">
      <div class="w-6 h-6 border-2 border-stone-300 dark:border-stone-600 border-t-stone-900 dark:border-t-white rounded-full animate-spin"></div>
      <p class="text-stone-400 dark:text-stone-500 text-sm">Loading results...</p>
    </div>
  {:else if positions.length === 0}
    <div class="py-16 flex flex-col items-center text-center" in:fade={{ duration: 300 }}>
      <div class="w-14 h-14 bg-stone-100 dark:bg-stone-800 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-7 h-7 text-stone-400 dark:text-stone-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
      </div>
      <h3 class="text-base font-semibold text-stone-900 dark:text-white mb-1">No results yet</h3>
      <p class="text-stone-500 dark:text-stone-400 text-sm max-w-xs">No votes have been cast yet. Check back after voting begins.</p>
    </div>
  {:else}
    {#if isCompleted}
      <div class="mb-12" in:fade={{ duration: 300 }}>
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
                        <p class="text-[11px] text-stone-500 font-medium">{winner.partylists?.name || 'Independent'} • <span class="text-stone-700 dark:text-stone-300">{(results[position] || {})[winner.id] || 0} votes</span></p>
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

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6" in:fade={{ duration: 300 }}>
      {#each positions as position, idx}
        {@const { entries, totalVotes } = getPositionResults(position)}
        <div class="bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-700 rounded-2xl p-5" in:fly={{ y: 12, duration: 300, delay: idx * 60 }}>
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
                      <span class="w-4 h-4 bg-emerald-100 dark:bg-emerald-900/30 rounded-full flex items-center justify-center">
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
