<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import { page } from '$app/state';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { elasticOut } from 'svelte/easing';
  import { sortPositions } from '$lib/constants.js';

  let isSubmitting = $state(false);
  let hasSubmitted = $state(false);
  let isLoading = $state(true);
  let errorMessage = $state('');
  let showConfirm = $state(false);
  let toastMessage = $state('');
  let toastVisible = $state(false);
  let alreadyVoted = $state(false);
  let electionId = $state('');
  let receiptId = $state('');

  /** @type {Record<string, any[]>} */
  let candidatesGrouped = $state({});
  /** @type {Record<string, string | null>} */
  let selectedVotes = $state({});
  
  let voterName = $state('');
  let electionName = $state('');

  /** @type {string[]} */
  const positionOrder = $derived(sortPositions(Object.keys(candidatesGrouped)));
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

  onMount(() => {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    voterName = session?.full_name || 'Voter';
  });

  $effect(() => {
    const session = $voterSession;
    if (!session) return;

    const id = page.url.searchParams.get('election') || '';
    electionId = id;

    if (!id) {
      isLoading = false;
      alreadyVoted = false;
      candidatesGrouped = {};
      selectedVotes = {};
      errorMessage = '';
      return;
    }

    // Reset state for new election
    isLoading = true;
    alreadyVoted = false;
    hasSubmitted = false;
    errorMessage = '';
    candidatesGrouped = {};
    selectedVotes = {};

    const electionInfo = (session.elections || []).find(/** @param {any} e */ e => e.id === id);
    electionName = electionInfo?.name || 'Election';

    if (electionInfo?.has_voted) {
      alreadyVoted = true;
      isLoading = false;
      return;
    }

    studentApi.getCandidates(id).then(res => {
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
    }).catch(() => {
      errorMessage = 'Failed to load the ballot. Please contact an administrator.';
    }).finally(() => {
      isLoading = false;
    });
  });

  async function submitVote() {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    isSubmitting = true;
    errorMessage = '';
    const votes = Object.entries(selectedVotes)
      .filter(([_, id]) => id)
      .map(([position, candidate_id]) => ({ candidate_id: /** @type {string} */ (candidate_id), position }));
    try {
      const resp = await studentApi.vote(session.student_id ?? '', electionId, votes);
      if (resp && resp.receipt_id) {
          receiptId = resp.receipt_id;
      }
      voterSession.markVoted(electionId);
      showConfirm = false;
      hasSubmitted = true;
      showToast('Your vote has been submitted successfully!');
      setTimeout(() => goto(`/student`), 5000);
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

<div class="min-h-screen" style="background-color: var(--bg-main);">

  {#if alreadyVoted}
    <!-- ========== ALREADY VOTED STATE ========== -->
    <div class="min-h-[80vh] flex items-center justify-center p-6" in:fade={{ duration: 400 }}>
      <div class="text-center max-w-sm">
        <div class="w-16 h-16 bg-stone-100 dark:bg-stone-800 rounded-2xl flex items-center justify-center mx-auto mb-5">
          <svg class="w-8 h-8 text-stone-600 dark:text-stone-300" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <h2 class="text-xl font-semibold text-stone-900 dark:text-white mb-2">You've already voted</h2>
        <p class="text-stone-500 dark:text-stone-400 text-sm mb-6 leading-relaxed">Your ballot for this election has been recorded. You cannot vote again in the same election.</p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
          <a href="/student" class="inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold hover:opacity-90 transition-all"
             style="background-color: var(--text-main); color: var(--bg-main);">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
            Dashboard
          </a>
          <a href="/student/results" class="inline-flex items-center gap-2 bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 text-stone-700 dark:text-stone-200 rounded-xl px-5 py-2.5 text-sm font-semibold hover:bg-stone-50 dark:hover:bg-stone-700 transition-all">
            View Results
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>
    </div>
  {:else if hasSubmitted}
    <!-- ========== RECEIPT SUCCESS STATE ========== -->
    <div class="min-h-screen flex items-center justify-center p-6" in:fade={{ duration: 600 }}>
      <div class="w-full max-w-sm mx-auto">
        <div class="bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-700 shadow-[0_20px_60px_-10px_rgba(0,0,0,0.1)] dark:shadow-none p-8 relative overflow-hidden" 
             style="border-radius: 12px; border-bottom: 3px dashed var(--border-main);" 
             in:fly={{ y: 30, duration: 600, delay: 200, easing: elasticOut }}>
             
          <!-- decorative top notch -->
          <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-6 h-6 rounded-full bg-stone-50 dark:bg-[#292524] border border-stone-200 dark:border-stone-700"></div>

          <!-- receipt header -->
          <div class="text-center mb-6 pt-2 border-b border-dashed border-stone-200 dark:border-stone-700 pb-6">
            <p class="text-[10px] font-black tracking-[0.2em] text-stone-400 dark:text-stone-500 uppercase mb-2">Official Receipt</p>
            <h2 class="text-xl font-bold text-stone-900 dark:text-white">Vote Recorded</h2>
          </div>
          
          <div class="space-y-3 mb-6 text-sm font-mono text-stone-500 dark:text-stone-400">
             <div class="flex justify-between items-center">
               <span>Voter:</span>
               <span class="font-semibold text-stone-900 dark:text-white">{(voterName).substring(0,3).toUpperCase()}***</span>
             </div>
             <div class="flex justify-between items-center">
               <span>Election:</span>
               <span class="font-semibold text-stone-900 dark:text-white max-w-[150px] truncate text-right" title={electionName}>{electionName}</span>
             </div>
             <div class="flex justify-between items-center">
               <span>Positions:</span>
               <span class="font-semibold text-stone-900 dark:text-white">{selectedCount}</span>
             </div>
             <div class="flex justify-between items-center border-t border-dashed border-stone-200 dark:border-stone-700 pt-4 mt-4">
               <span>Rec. No:</span>
               <span class="font-bold text-brand-primary">{receiptId || 'PENDING...'}</span>
             </div>
          </div>

          <div class="text-center text-[10px] text-stone-400 dark:text-stone-500 font-mono mt-8 leading-relaxed">
             Please keep this receipt number. It can be used to cryptographically verify your vote after the election.
          </div>
        </div>

        <div class="mt-8 text-center" in:fade={{ delay: 800 }}>
          <a href="/student" class="btn-secondary w-full py-4 text-sm font-semibold">
            Return to Dashboard
          </a>
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
    <div class="max-w-5xl mx-auto w-full px-5 md:px-8 py-8">

      {#if !electionId}
        <!-- ========== ELECTION LIST VIEW ========== -->
        <div class="mb-10" in:fly={{ y: -10, duration: 400 }}>
          <h1 class="text-3xl font-bold text-stone-900 dark:text-white tracking-tight mb-2">Voting Room</h1>
          <p class="text-stone-500 dark:text-stone-400 text-sm">Select an active election session to securely cast your ballot.</p>
        </div>

        {@const elections = ($voterSession?.elections || []).filter(e => !e.has_voted)}
        {#if elections.length === 0}
          <div class="bg-stone-50 dark:bg-stone-900 border border-dashed border-stone-200 dark:border-stone-700 rounded-[2rem] p-16 text-center" in:fade>
            <div class="w-16 h-16 bg-white dark:bg-stone-800 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
              <svg class="w-8 h-8 text-stone-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            </div>
            <h3 class="text-lg font-bold text-stone-900 dark:text-white mb-2">No active ballots</h3>
            <p class="text-stone-500 dark:text-stone-400 text-sm max-w-xs mx-auto">You have completed all current election sessions or none are active at this time.</p>
          </div>
        {:else}
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {#each elections as election}
              <div class="bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-700 rounded-[2rem] p-8 shadow-sm hover:shadow-xl transition-all border-l-4 border-l-amber-500 group">
                <div class="flex items-center justify-between mb-6">
                  <span class="text-[10px] font-bold uppercase tracking-widest text-amber-600 bg-amber-50 px-3 py-1 rounded-full">
                    Ready to Vote
                  </span>
                </div>
                <h3 class="text-xl font-bold text-stone-900 dark:text-white mb-8 group-hover:text-amber-600 transition-colors uppercase tracking-tight">{election.name}</h3>
                <a 
                  href="/student/ballot?election={election.id}"
                  class="flex items-center justify-center gap-3 bg-stone-900 text-white rounded-2xl py-4 text-xs font-bold hover:bg-stone-800 transition-all shadow-lg active:scale-95"
                >
                  Enter Voting Booth
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/></svg>
                </a>
              </div>
            {/each}
          </div>
        {/if}

      {:else}
        <!-- ========== HEADER ========== -->
        <div class="mb-8" in:fly={{ y: -10, duration: 300 }}>
          <div class="flex items-center gap-2 mb-2">
            <a href="/student/ballot" class="text-stone-400 hover:text-stone-900 transition-colors flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
              Go Back
            </a>
          </div>
          <p class="text-xs font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-1">Official Ballot · {electionName}</p>
          <div class="flex items-start justify-between gap-4">
            <h1 class="text-2xl font-semibold text-stone-900 dark:text-white">Hi, {voterName.split(' ')[0]} 👋</h1>
            <!-- Selection counter -->
            <div class="flex-shrink-0 bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl px-4 py-2 text-center">
              <p class="text-xs font-semibold text-stone-900 dark:text-white">{selectedCount}/{totalPositions}</p>
              <p class="text-[10px] text-stone-400 dark:text-stone-500 mt-0.5">Selected</p>
            </div>
          </div>
          <p class="text-sm mt-1" style="color: var(--text-muted);">Select your preferred candidate for each position below.</p>
        </div>

        <!-- Progress -->
        <div class="mb-8" in:fly={{ y: -10, duration: 300, delay: 60 }}>
        <div class="flex items-center justify-between mb-2">
          <p class="text-xs font-medium" style="color: var(--text-muted);">{selectedCount} of {totalPositions} positions completed</p>
          <p class="text-xs font-semibold" style="color: var(--text-main);">{progressPercent}%</p>
        </div>
        <div class="h-1.5 rounded-full overflow-hidden" style="background-color: var(--border-main);">
          <div 
            class="h-full rounded-full transition-all duration-500 ease-out"
            style="width: {progressPercent}%; background-color: var(--text-main);"
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
          <div class="w-14 h-14 bg-stone-100 dark:bg-stone-800 rounded-2xl flex items-center justify-center mb-4">
            <svg class="w-7 h-7 text-stone-400 dark:text-stone-500" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V19.5a2.25 2.25 0 002.25 2.25h.75"/></svg>
          </div>
          <h3 class="text-base font-semibold text-stone-900 dark:text-white mb-1">No candidates listed</h3>
          <p class="text-stone-500 dark:text-stone-400 text-sm max-w-xs">The adviser hasn't added candidates yet. Check back later.</p>
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
                <div class="w-6 h-6 bg-stone-200 dark:bg-stone-700 rounded-md flex items-center justify-center text-stone-600 dark:text-stone-300 text-xs font-semibold">{idx + 1}</div>
                <h2 class="text-base font-semibold text-stone-900 dark:text-white capitalize">{position}</h2>
                {#if isComplete}
                  <span class="text-[10px] font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 px-2 py-0.5 rounded-full">Selected</span>
                {:else}
                  <span class="text-[10px] text-stone-400 dark:text-stone-500 border border-stone-200 dark:border-stone-700 px-2 py-0.5 rounded-full">Choose one</span>
                {/if}
              </div>

              <!-- Candidate cards grid -->
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-{Math.min(list.length, 3)} gap-3">
                {#each list as candidate}
                  {@const isSelected = selectedVotes[position] === candidate.id}

                  <label class="cursor-pointer select-none group">
                    <input type="radio" name={position} value={candidate.id} bind:group={selectedVotes[position]} class="sr-only" />

                    <div class="rounded-2xl border p-4 flex items-center gap-3 transition-all duration-200"
                         style={isSelected ? 'background-color: var(--brand-glow); border-color: var(--brand-primary); box-shadow: 0 4px 15px -3px var(--focus-ring);' : 'background-color: var(--bg-card); border-color: var(--border-main);'}
                    >
                      <!-- Avatar -->
                      <div class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0 transition-colors duration-200"
                           style={isSelected ? 'background-color: var(--brand-primary); color: var(--bg-card);' : 'background-color: var(--icon-bg); color: var(--text-muted);'}>
                        {getMonogram(candidate.name)}
                      </div>

                      <!-- Name + Party -->
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-semibold truncate transition-colors duration-200"
                           style={isSelected ? 'color: var(--text-main);' : 'color: var(--text-main);'}>{candidate.name}</p>
                        <p class="text-xs truncate transition-colors duration-200"
                           style="color: var(--text-muted);">{candidate.party}</p>
                      </div>

                      <!-- Radio indicator -->
                      <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all duration-200"
                           style={isSelected ? 'border-color: var(--brand-primary);' : 'border-color: var(--text-subtle);'}>
                        <div class="w-2 h-2 rounded-full transition-all duration-200"
                             style={isSelected ? 'background-color: var(--brand-primary); transform: scale(1); opacity: 1;' : 'transform: scale(0.4); opacity: 0;'}></div>
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
          <div class="bg-white dark:bg-stone-800/60 border border-stone-200 dark:border-stone-700 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <div class="flex-1">
              <p class="text-sm font-semibold mb-0.5" style="color: var(--text-main);">
                {allSelected ? 'Ready to submit?' : 'Complete your ballot'}
              </p>
              <p class="text-xs" style="color: var(--text-muted);">
                {allSelected 
                  ? 'You\'ve selected candidates for all positions. Your vote is final once submitted.' 
                  : `Select candidates for all ${totalPositions} positions to submit your ballot.`}
              </p>
            </div>
            <button 
              onclick={() => showConfirm = true}
              disabled={!allSelected}
              class="btn-gradient !rounded-xl !py-2.5 !px-6 !text-sm flex-shrink-0 !w-auto whitespace-nowrap"
            >
              Submit Ballot
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>
      {/if}
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
        <div class="bg-white dark:bg-stone-900 border border-stone-100 dark:border-stone-700 rounded-2xl w-full max-w-md p-6" in:fly={{ y: 16, duration: 250 }}>
          <div class="w-10 h-10 bg-stone-100 dark:bg-stone-800 rounded-xl flex items-center justify-center mb-4">
            <svg class="w-5 h-5 text-stone-700 dark:text-stone-300" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/></svg>
          </div>
          <h3 class="text-lg font-semibold text-stone-900 dark:text-white mb-1">Confirm your ballot</h3>
          <p class="text-sm text-stone-500 dark:text-stone-400 mb-5">Your vote is anonymous and cannot be changed once submitted. Are you sure you want to proceed?</p>
          
          <!-- Summary -->
          <div class="bg-stone-50 dark:bg-stone-800 rounded-xl p-4 mb-5 space-y-2 max-h-48 overflow-y-auto">
            {#each getReviewList() as item}
              <div class="flex items-center justify-between">
                <p class="text-xs text-stone-500 dark:text-stone-400 capitalize">{item.position}</p>
                <p class="text-xs font-semibold text-stone-900 dark:text-white">{item.candidate?.name}</p>
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
              class="flex-1 bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 rounded-xl py-2.5 text-sm font-medium hover:bg-stone-200 dark:hover:bg-stone-700 transition-colors"
            >
              Go Back
            </button>
            <button 
              onclick={submitVote}
              disabled={isSubmitting}
              class="flex-1 rounded-xl py-2.5 text-sm font-semibold hover:opacity-90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              style="background-color: var(--text-main); color: var(--bg-main);"
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
