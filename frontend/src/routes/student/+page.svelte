<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import { fade, fly } from 'svelte/transition';

  let isLoading = $state(true);
  /** @type {any[]} */
  let elections = $state([]);
  let voterName = $state('');

  // Vote summary state (for viewing after voting)
  let selectedSummaryElection = $state(/** @type {string | null} */ (null));
  let summaryLoading = $state(false);
  let receiptId = $state('');
  let votedAt = $state('');
  /** @type {any[]} */
  let voteDetails = $state([]);

  onMount(() => {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    voterName = session?.full_name || 'Student';
    elections = session?.elections || [];
    isLoading = false;
  });

  /** @param {string} electionId */
  async function loadVoteSummary(electionId) {
    const session = $voterSession;
    if (!session) return;
    if (selectedSummaryElection === electionId) {
      selectedSummaryElection = null;
      return;
    }
    selectedSummaryElection = electionId;
    summaryLoading = true;
    try {
      const data = await studentApi.getVoteSummary(session.student_id, electionId);
      receiptId = data.receipt_id || '';
      votedAt = data.voted_at || '';
      voteDetails = data.votes || [];
    } catch (err) {
      console.error('Failed to load vote summary:', err);
    } finally {
      summaryLoading = false;
    }
  }
</script>

<svelte:head>
  <title>Student Dashboard | UniVote</title>
</svelte:head>

<div class="max-w-2xl mx-auto w-full px-5 md:px-8 py-8">

  <!-- Header -->
  <div class="mb-8" in:fly={{ y: -10, duration: 300 }}>
    <p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Student Dashboard</p>
    <h1 class="text-2xl font-semibold text-stone-900">Welcome, {voterName.split(' ')[0]} 👋</h1>
    <p class="text-stone-500 text-sm mt-1">Select an election to cast your vote or view your ballot receipt.</p>
  </div>

  {#if isLoading}
    <div class="py-20 flex flex-col items-center justify-center gap-3">
      <div class="w-6 h-6 border-2 border-stone-300 border-t-stone-900 rounded-full animate-spin"></div>
      <p class="text-stone-400 text-sm">Loading dashboard...</p>
    </div>
  {:else if elections.length === 0}
    <div class="py-16 flex flex-col items-center text-center" in:fade={{ duration: 300 }}>
      <div class="w-14 h-14 bg-stone-100 rounded-2xl flex items-center justify-center mb-4">
        <svg class="w-7 h-7 text-stone-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
      </div>
      <h3 class="text-base font-semibold text-stone-900 mb-1">No active elections</h3>
      <p class="text-stone-500 text-sm max-w-xs">There are no elections currently in progress. Check back later.</p>
    </div>
  {:else}
    <div class="space-y-4" in:fade={{ duration: 300 }}>
      <p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase">
        {elections.length} Active Election{elections.length !== 1 ? 's' : ''}
      </p>

      {#each elections as election, idx}
        <div class="bg-white border border-stone-200 rounded-2xl overflow-hidden" in:fly={{ y: 12, duration: 300, delay: idx * 60 }}>
          <div class="p-5">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 {election.has_voted ? 'bg-emerald-100' : 'bg-stone-100'} rounded-xl flex items-center justify-center">
                  {#if election.has_voted}
                    <svg class="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                  {:else}
                    <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  {/if}
                </div>
                <div>
                  <h2 class="text-sm font-semibold text-stone-900">{election.name}</h2>
                  <span class="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide {election.has_voted ? 'text-emerald-600' : 'text-amber-600'}">
                    <span class="w-1.5 h-1.5 rounded-full {election.has_voted ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'}"></span>
                    {election.has_voted ? 'Voted' : 'Not yet voted'}
                  </span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2">
              {#if election.has_voted}
                <button
                  onclick={() => loadVoteSummary(election.id)}
                  class="flex items-center gap-2 bg-stone-100 text-stone-700 rounded-xl px-4 py-2 text-xs font-semibold hover:bg-stone-200 transition-all"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>
                  {selectedSummaryElection === election.id ? 'Hide Receipt' : 'View Receipt'}
                </button>
                <a href="/student/results?election={election.id}" class="flex items-center gap-2 bg-white border border-stone-200 text-stone-700 rounded-xl px-4 py-2 text-xs font-semibold hover:bg-stone-50 transition-all">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                  Results
                </a>
              {:else}
                <a href="/student/ballot?election={election.id}" class="flex items-center gap-2 bg-stone-900 text-white rounded-xl px-5 py-2.5 text-xs font-semibold hover:bg-stone-800 transition-all">
                  Cast Your Vote
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
                </a>
                <a href="/student/results?election={election.id}" class="flex items-center gap-2 bg-white border border-stone-200 text-stone-700 rounded-xl px-4 py-2 text-xs font-semibold hover:bg-stone-50 transition-all">
                  Results
                </a>
              {/if}
            </div>
          </div>

          <!-- Expandable vote receipt -->
          {#if selectedSummaryElection === election.id}
            <div class="border-t border-stone-200 p-5 bg-stone-50" in:fly={{ y: -8, duration: 200 }}>
              {#if summaryLoading}
                <div class="py-4 flex items-center justify-center gap-2">
                  <div class="w-4 h-4 border-2 border-stone-300 border-t-stone-900 rounded-full animate-spin"></div>
                  <span class="text-stone-400 text-xs">Loading receipt...</span>
                </div>
              {:else}
                <!-- Receipt ID -->
                <div class="flex items-center justify-between bg-white border border-stone-200 rounded-xl px-4 py-3 mb-3">
                  <div>
                    <p class="text-[10px] font-semibold text-stone-400 uppercase tracking-widest">Verification ID</p>
                    <code class="text-sm font-mono font-bold text-stone-900 tracking-widest">{receiptId}</code>
                  </div>
                  <button 
                    onclick={() => navigator.clipboard.writeText(receiptId)}
                    class="text-stone-400 hover:text-stone-700 transition-colors p-1"
                    title="Copy"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/></svg>
                  </button>
                </div>
                {#if votedAt}
                  <p class="text-xs text-stone-400 mb-3">Submitted on {new Date(votedAt).toLocaleString()}</p>
                {/if}
                <!-- Votes -->
                <div class="space-y-2">
                  {#each voteDetails as vote}
                    <div class="flex items-center justify-between p-3 bg-white rounded-xl border border-stone-100">
                      <div>
                        <p class="text-[10px] font-semibold text-stone-400 uppercase tracking-widest">{vote.position}</p>
                        <p class="text-sm font-medium text-stone-900 mt-0.5">{vote.candidates?.students?.full_name || 'Unknown'}</p>
                        <p class="text-xs text-stone-400">{vote.candidates?.partylists?.name || 'Independent'}</p>
                      </div>
                      <div class="w-5 h-5 bg-emerald-100 rounded-full flex items-center justify-center">
                        <svg class="w-3 h-3 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
