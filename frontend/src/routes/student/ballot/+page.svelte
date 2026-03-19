<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import { page } from '$app/state';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { elasticOut } from 'svelte/easing';

  let isSubmitting = $state(false);
  let hasSubmitted = $state(false);
  let isLoading = $state(true);
  let errorMessage = $state('');
  let showConfirm = $state(false);
  let toastMessage = $state('');
  let toastVisible = $state(false);
  let alreadyVoted = $state(false);
  let electionId = $state('');

  /** @type {Record<string, any[]>} */
  let candidatesGrouped = $state({});
  /** @type {Record<string, string | null>} */
  let selectedVotes = $state({});
  
  let voterName = $state('');
  let electionName = $state('');

  /** @type {string[]} */
  const positionOrder = $derived(Object.keys(candidatesGrouped));
  const selectedCount = $derived(Object.values(selectedVotes).filter(v => v).length);
  const totalPositions = $derived(positionOrder.length);
  const progressPercent = $derived(totalPositions > 0 ? Math.round((selectedCount / totalPositions) * 100) : 0);
  const allSelected = $derived(selectedCount === totalPositions && totalPositions > 0);

  /** @param {string} name */
  function getMonogram(name) {
    return name.split(' ').slice(0, 2).map(w => w[0]?.toUpperCase() || '').join('');
  }

  /** @return {Array<{position: string, candidate: any}>} */
  function getReviewList() {
    return positionOrder
      .filter(pos => selectedVotes[pos])
      .map(pos => ({
        position: pos,
        candidate: (candidatesGrouped[pos] || []).find(c => c.id === selectedVotes[pos])
      }))
      .filter(r => r.candidate);
  }

  /** @param {string} msg */
  function showToast(msg) {
    toastMessage = msg;
    toastVisible = true;
    setTimeout(() => { toastVisible = false; }, 3500);
  }

  onMount(async () => {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    voterName = session?.full_name || 'Voter';

    electionId = page.url.searchParams.get('election') || '';
    if (!electionId) { goto('/student'); return; }

    const electionInfo = (session.elections || []).find(/** @param {any} e */ e => e.id === electionId);
    electionName = electionInfo?.name || 'Election';
    if (electionInfo?.has_voted) {
      alreadyVoted = true;
      isLoading = false;
      return;
    }

    try {
      const res = await studentApi.getCandidates(electionId);
      const data = res.data || [];
      
      /** @type {Record<string, any[]>} */
      const grouped = {};
      data.forEach(/** @param {any} c */ c => {
        if (!grouped[c.position]) grouped[c.position] = [];
        grouped[c.position].push({ id: c.id, name: c.students?.full_name || 'Unknown', party: c.partylists?.name || 'Independent' });
      });
      
      candidatesGrouped = grouped;
      const initialVotes = /** @type {Record<string, null>} */ ({});
      Object.keys(grouped).forEach(pos => { initialVotes[pos] = null; });
      selectedVotes = initialVotes;

    } catch (err) {
      errorMessage = 'Failed to load the ballot. Please contact an administrator.';
    } finally {
      isLoading = false;
    }
  });

  async function submitVote() {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    isSubmitting = true;
    errorMessage = '';
    const votes = Object.entries(selectedVotes)
      .filter(([_, id]) => id)
      .map(([position, candidate_id]) => ({ candidate_id, position }));
    try {
      await studentApi.vote(session.student_id ?? '', electionId, votes);
      voterSession.markVoted(electionId);
      showConfirm = false;
      hasSubmitted = true;
      showToast('Your vote has been submitted successfully!');
      setTimeout(() => goto(`/student/results?election=${electionId}`), 2000);
    } catch (/** @type {any} */ err) {
      errorMessage = err.message ?? 'Failed to submit ballot.';
      showConfirm = false;
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Official Ballot | UniVote</title>
</svelte:head>

<div class="min-h-screen bg-[#f9f8f6]">

  {#if alreadyVoted}
    <!-- ========== ALREADY VOTED STATE ========== -->
    <div class="min-h-[80vh] flex items-center justify-center p-6" in:fade={{ duration: 400 }}>
      <div class="text-center max-w-sm">
        <div class="w-16 h-16 bg-stone-100 rounded-2xl flex items-center justify-center mx-auto mb-5">
          <svg class="w-8 h-8 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <h2 class="text-xl font-semibold text-stone-900 mb-2">You've already voted</h2>
        <p class="text-stone-500 text-sm mb-6 leading-relaxed">Your ballot for this election has been recorded. You cannot vote again in the same election.</p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
          <a href="/student" class="inline-flex items-center gap-2 bg-stone-900 text-white rounded-xl px-5 py-2.5 text-sm font-semibold hover:bg-stone-800 transition-all">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            Dashboard
          </a>
          <a href="/student/results" class="inline-flex items-center gap-2 bg-white border border-stone-200 text-stone-700 rounded-xl px-5 py-2.5 text-sm font-semibold hover:bg-stone-50 transition-all">
            View Results
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>
    </div>
  {:else if hasSubmitted}
    <!-- ========== SUCCESS STATE ========== -->
    <div class="min-h-screen flex items-center justify-center p-6" in:fade={{ duration: 600 }}>
      <div class="text-center max-w-md">
        <div class="relative mx-auto w-28 h-28 mb-8" in:scale={{ duration: 700, easing: elasticOut, delay: 200 }}>
          <div class="absolute inset-0 bg-emerald-400/20 rounded-[2rem] animate-ping"></div>
          <div class="relative w-28 h-28 bg-stone-900 rounded-[2rem] flex items-center justify-center shadow-2xl">
            <svg class="w-14 h-14 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
        </div>

        <div in:fly={{ y: 20, duration: 500, delay: 400 }}>
          <p class="text-xs font-semibold text-stone-400 tracking-widest uppercase mb-2">Ballot Submitted</p>
          <h1 class="text-2xl font-semibold text-stone-900 mb-3">Your vote has been cast!</h1>
          <p class="text-stone-500 text-sm leading-relaxed">Your ballot has been securely encrypted and recorded. Results will be available after the election period ends.</p>
        </div>

        <div class="mt-8 flex gap-3 justify-center" in:fly={{ y: 20, duration: 500, delay: 600 }}>
          <a href="/" class="px-5 py-2.5 bg-white border border-stone-200 text-stone-700 font-medium text-sm rounded-xl hover:bg-stone-50 transition-colors">
            Return Home
          </a>
          <div class="px-5 py-2.5 bg-emerald-50 border border-emerald-200 text-emerald-700 font-medium text-sm rounded-xl flex items-center gap-2">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
            Securely Counted
          </div>
        </div>
      </div>
    </div>

  {:else if isLoading}
    <!-- ========== LOADING STATE ========== -->
    <div class="min-h-screen flex flex-col items-center justify-center gap-4">
      <LoadingSpinner />
      <p class="text-stone-400 font-medium text-sm animate-pulse">Loading secure ballot...</p>
    </div>

  {:else}
    <!-- ========== MAIN BALLOT ========== -->
    <div class="max-w-2xl mx-auto w-full px-5 md:px-8 py-8">

      <!-- Header -->
      <div class="mb-8" in:fly={{ y: -10, duration: 300 }}>
        <p class="text-xs font-semibold text-stone-400 tracking-widest uppercase mb-1">Official Ballot · {electionName}</p>
        <div class="flex items-start justify-between gap-4">
          <h1 class="text-2xl font-semibold text-stone-900">Hi, {voterName.split(' ')[0]} 👋</h1>
          <!-- Selection counter -->
          <div class="flex-shrink-0 bg-white border border-stone-200 rounded-xl px-4 py-2 text-center">
            <p class="text-xs font-semibold text-stone-900">{selectedCount}/{totalPositions}</p>
            <p class="text-[10px] text-stone-400 mt-0.5">Selected</p>
          </div>
        </div>
        <p class="text-stone-500 text-sm mt-1">Select your preferred candidate for each position below.</p>
      </div>

      <!-- Progress -->
      <div class="mb-8" in:fly={{ y: -10, duration: 300, delay: 60 }}>
        <div class="flex items-center justify-between mb-2">
          <p class="text-xs text-stone-500 font-medium">{selectedCount} of {totalPositions} positions completed</p>
          <p class="text-xs font-semibold text-stone-900">{progressPercent}%</p>
        </div>
        <div class="h-1.5 bg-stone-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-stone-900 rounded-full transition-all duration-500 ease-out"
            style="width: {progressPercent}%"
          ></div>
        </div>
      </div>

      <!-- Ballot Errors -->
      {#if errorMessage}
        <div class="mb-5 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-2.5 text-red-700 text-sm" in:fly={{ y: -5, duration: 200 }}>
          <svg class="w-4 h-4 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
          <p class="font-medium">{errorMessage}</p>
        </div>
      {/if}

      {#if totalPositions === 0}
        <!-- Empty state -->
        <div class="py-16 flex flex-col items-center text-center" in:fade={{ duration: 300 }}>
          <div class="w-14 h-14 bg-stone-100 rounded-2xl flex items-center justify-center mb-4">
            <svg class="w-7 h-7 text-stone-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V19.5a2.25 2.25 0 002.25 2.25h.75"/></svg>
          </div>
          <h3 class="text-base font-semibold text-stone-900 mb-1">No candidates listed</h3>
          <p class="text-stone-500 text-sm max-w-xs">The adviser hasn't added candidates yet. Check back later.</p>
        </div>
      {:else}
        <!-- Positions + Candidates -->
        <div class="space-y-8 mb-8">
          {#each positionOrder as position, idx}
            {@const list = candidatesGrouped[position] || []}
            {@const isComplete = !!selectedVotes[position]}

            <div in:fly={{ y: 12, duration: 350, delay: 100 + idx * 60 }}>
              <!-- Position label -->
              <div class="flex items-center gap-3 mb-3">
                <div class="w-6 h-6 bg-stone-200 rounded-md flex items-center justify-center text-stone-600 text-xs font-semibold">{idx + 1}</div>
                <h2 class="text-base font-semibold text-stone-900 capitalize">{position}</h2>
                {#if isComplete}
                  <span class="text-[10px] font-semibold text-emerald-600 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">Selected</span>
                {:else}
                  <span class="text-[10px] text-stone-400 border border-stone-200 px-2 py-0.5 rounded-full">Choose one</span>
                {/if}
              </div>

              <!-- Candidate cards grid -->
              <div class="grid grid-cols-1 sm:grid-cols-{Math.min(list.length, 3)} gap-2.5">
                {#each list as candidate}
                  {@const isSelected = selectedVotes[position] === candidate.id}

                  <label class="cursor-pointer select-none group">
                    <input type="radio" name={position} value={candidate.id} bind:group={selectedVotes[position]} class="sr-only" />

                    <div class="rounded-2xl border p-4 flex items-center gap-3 transition-all duration-200
                      {isSelected 
                        ? 'bg-stone-900 border-stone-900' 
                        : 'bg-white border-stone-200 hover:border-stone-300 hover:bg-stone-50'}"
                    >
                      <!-- Avatar -->
                      <div class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0 transition-colors duration-200
                        {isSelected ? 'bg-white text-stone-900' : 'bg-stone-100 text-stone-600'}">
                        {getMonogram(candidate.name)}
                      </div>

                      <!-- Name + Party -->
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-semibold truncate transition-colors duration-200
                          {isSelected ? 'text-white' : 'text-stone-900'}">{candidate.name}</p>
                        <p class="text-xs truncate transition-colors duration-200
                          {isSelected ? 'text-stone-400' : 'text-stone-400'}">{candidate.party}</p>
                      </div>

                      <!-- Radio indicator -->
                      <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all duration-200
                        {isSelected ? 'border-white' : 'border-stone-300'}">
                        <div class="w-2 h-2 rounded-full transition-all duration-200
                          {isSelected ? 'bg-white scale-100 opacity-100' : 'bg-white scale-40 opacity-0'}"></div>
                      </div>
                    </div>
                  </label>
                {/each}
              </div>
            </div>
          {/each}
        </div>

        <!-- Submit section -->
        <div class="pb-8" in:fly={{ y: 12, duration: 350, delay: 300 }}>
          <div class="bg-white border border-stone-200 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <div class="flex-1">
              <p class="text-sm font-semibold text-stone-900 mb-0.5">
                {allSelected ? 'Ready to submit?' : 'Complete your ballot'}
              </p>
              <p class="text-xs text-stone-500">
                {allSelected 
                  ? 'You\'ve selected candidates for all positions. Your vote is final once submitted.' 
                  : `Select candidates for all ${totalPositions} positions to submit your ballot.`}
              </p>
            </div>
            <button 
              onclick={() => showConfirm = true}
              disabled={!allSelected}
              class="bg-stone-900 text-white rounded-xl px-6 py-2.5 text-sm font-semibold flex items-center gap-2 flex-shrink-0 whitespace-nowrap transition-all duration-200 hover:bg-stone-800 active:scale-[0.99] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Submit Ballot
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>
      {/if}
    </div>

    <!-- ========== CONFIRM MODAL ========== -->
    {#if showConfirm}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div 
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4"
        style="background:rgba(0,0,0,0.3);backdrop-filter:blur(4px)"
        in:fade={{ duration: 200 }}
        onclick={(e) => { if (e.target === e.currentTarget) showConfirm = false; }}
        onkeydown={() => {}}
      >
        <div class="bg-white rounded-2xl w-full max-w-md p-6" in:fly={{ y: 16, duration: 250 }}>
          <div class="w-10 h-10 bg-stone-100 rounded-xl flex items-center justify-center mb-4">
            <svg class="w-5 h-5 text-stone-700" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/></svg>
          </div>
          <h3 class="text-lg font-semibold text-stone-900 mb-1">Confirm your ballot</h3>
          <p class="text-sm text-stone-500 mb-5">Your vote is anonymous and cannot be changed once submitted. Are you sure you want to proceed?</p>
          
          <!-- Summary -->
          <div class="bg-stone-50 rounded-xl p-4 mb-5 space-y-2 max-h-48 overflow-y-auto">
            {#each getReviewList() as item}
              <div class="flex items-center justify-between">
                <p class="text-xs text-stone-500 capitalize">{item.position}</p>
                <p class="text-xs font-semibold text-stone-900">{item.candidate?.name}</p>
              </div>
            {/each}
          </div>

          {#if errorMessage}
            <div class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium">
              {errorMessage}
            </div>
          {/if}

          <div class="flex gap-3">
            <button 
              onclick={() => showConfirm = false}
              class="flex-1 bg-stone-100 text-stone-700 rounded-xl py-2.5 text-sm font-medium hover:bg-stone-200 transition-colors"
            >
              Go Back
            </button>
            <button 
              onclick={submitVote}
              disabled={isSubmitting}
              class="flex-1 bg-stone-900 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-800 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {#if isSubmitting}
                <LoadingSpinner />
                Submitting...
              {:else}
                Submit Vote
              {/if}
            </button>
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<!-- ========== TOAST ========== -->
{#if toastVisible}
  <div 
    class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-stone-900 text-white text-sm px-5 py-3 rounded-2xl flex items-center gap-2.5 shadow-xl z-[60]"
    in:fly={{ y: 16, duration: 300 }}
    out:fade={{ duration: 200 }}
  >
    <svg class="w-4 h-4 text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
    <span>{toastMessage}</span>
  </div>
{/if}

<style>
  .scale-40 { transform: scale(0.4); }
</style>
