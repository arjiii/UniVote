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
  import GlassCard from '$lib/components/GlassCard.svelte';

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
  
  let isAuthorized = $state(false);
  let adviserPasscode = $state('');
  let votingPin = $state('');
  let showPin = $state(false);
  let pinConfirmInput = $state('');
  let isVerifyingPasscode = $state(false);
  let retrySeconds = $state(0);

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

  $effect(() => {
    if (retrySeconds > 0) {
      const timer = setInterval(() => { retrySeconds -= 1; }, 1000);
      return () => clearInterval(timer);
    }
  });

  async function verifyAdviserCode() {
    if (!adviserPasscode) return;
    isVerifyingPasscode = true;
    errorMessage = '';
    try {
      await studentApi.verifyPasscode(electionId, adviserPasscode);
      isAuthorized = true;
      showToast('Welcome to the Voting Booth');
    } catch (/** @type {any} */ err) {
      errorMessage = err.message || 'Invalid Adviser Passcode.';
    } finally {
      isVerifyingPasscode = false;
    }
  }

  async function fetchPin() {
    if (votingPin) {
      showPin = true;
      return;
    }
    const session = $voterSession;
    if (!session?.student_id) return;
    try {
      const res = await studentApi.getVotingPin(session.student_id);
      votingPin = res.voting_pin;
      showPin = true;
    } catch (/** @type {any} */ err) { showToast('Failed to retrieve PIN'); }
  }

  async function submitVote() {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    if (pinConfirmInput !== votingPin) {
      errorMessage = 'Incorrect Voting PIN. Please verify and try again.';
      return;
    }

    isSubmitting = true;
    errorMessage = '';
    const votes = Object.entries(selectedVotes)
      .filter(([_, id]) => id)
      .map(([position, candidate_id]) => ({ candidate_id: /** @type {string} */ (candidate_id), position }));
    try {
      const resp = await studentApi.vote(session.student_id ?? '', electionId, votes, votingPin);
      if (resp && resp.receipt_id) receiptId = resp.receipt_id;
      voterSession.markVoted(electionId);
      showConfirm = false;
      hasSubmitted = true;
      showToast('Your vote has been submitted successfully!');
      setTimeout(() => goto(`/student`), 5000);
    } catch (/** @type {any} */ err) {
      if (err.retryAfter) {
        retrySeconds = err.retryAfter;
        errorMessage = `Too many attempts. Locked for ${retrySeconds}s.`;
      } else {
        errorMessage = err.message ?? 'Failed to submit ballot.';
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head><title>Official Ballot | UniVote</title></svelte:head>

<div class="min-h-full">
  <!-- Gatekeeper Overlay -->
  {#if electionId && !isAuthorized && !alreadyVoted && !isLoading && !hasSubmitted}
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-surface-main/90 backdrop-blur-xl" in:fade>
      <div class="w-full max-w-md bg-surface-card border border-line-subtle rounded-[2rem] p-8 shadow-2xl text-center" in:scale={{ duration: 400, start: 0.9, easing: elasticOut }}>
        <div class="w-16 h-16 bg-[var(--status-warning-bg)] text-[var(--status-warning-fg)] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-inner">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25-2.25v6.75a2.25 2.25 0 002.25 2.25z"/></svg>
        </div>
        <h2 class="text-xl font-black text-content-main mb-2">Gatekeeper Required</h2>
        <p class="text-content-subtle text-sm mb-8 font-medium">Enter the 16-digit Adviser Passcode to unlock this protected voting session.</p>
        
        <div class="space-y-6">
          <input 
            type="text" bind:value={adviserPasscode} placeholder="XXXX-XXXX-XXXX-XXXX"
            class="input-base w-full text-center font-mono py-4 text-[1rem] uppercase tracking-[0.2em]"
          />
          {#if errorMessage}
            <div class="pill pill-danger" style="width:100%;justify-content:center;">{errorMessage}</div>
          {/if}
          <button onclick={verifyAdviserCode} disabled={isVerifyingPasscode || !adviserPasscode} class="btn-primary w-full py-4 text-[11px] font-black uppercase tracking-[0.2em]">
            {#if isVerifyingPasscode} <LoadingSpinner /> Authorizing... {:else} Open Ballot Portal {/if}
          </button>
          <a href="/student" class="inline-block text-[10px] font-black uppercase text-content-subtle hover:text-content-main hover:underline underline-offset-4 tracking-[0.2em]">Return to Safety</a>
        </div>
      </div>
    </div>
  {/if}

  {#if alreadyVoted}
    <!-- Already Voted -->
    <div class="min-h-[80vh] flex items-center justify-center p-6" in:fade={{ duration: 400 }}>
      <div class="text-center max-w-sm">
        <div class="w-16 h-16 bg-surface-elevated border border-line-subtle rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
          <svg class="w-8 h-8 text-content-subtle" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <h2 class="text-xl font-black text-content-main mb-2">Access Restricted</h2>
        <p class="text-content-subtle text-sm mb-8 font-medium">Our records show your ballot has already been securely cast and certified.</p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a href="/student" class="btn-primary w-full sm:w-auto">Portal Home</a>
          <a href="/student/results" class="btn-secondary w-full sm:w-auto">Audit Results</a>
        </div>
      </div>
    </div>

  {:else if hasSubmitted}
    <!-- Receipt -->
    <div class="min-h-screen flex items-center justify-center p-6" in:fade={{ duration: 600 }}>
      <div class="w-full max-w-sm mx-auto">
        <div class="bg-surface-card border border-line-main shadow-2xl p-8 relative flex flex-col items-center" style="border-radius:2rem;border-bottom:4px dashed var(--border-strong);" in:fly={{ y: 60, duration: 1000, delay: 200, easing: elasticOut }}>
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-surface-main border border-line-main"></div>
          <div class="text-center mb-8 pt-4 w-full border-b border-dashed border-line-main pb-8">
            <div class="w-16 h-16 bg-[var(--status-success-bg)] text-[var(--status-success-fg)] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-inner">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            </div>
            <p class="text-[10px] font-black tracking-[0.3em] text-content-subtle uppercase mb-2">Vote Certified</p>
            <h2 class="text-xl font-black text-content-main tracking-tight">Receipt Generated</h2>
          </div>
          
          <div class="w-full space-y-4 mb-10 text-xs font-mono font-black text-content-subtle tracking-tight">
             <div class="flex justify-between items-center opacity-80"><span>IDENTIFIER</span><span class="text-content-main">{(voterName).substring(0,3).toUpperCase()}***</span></div>
             <div class="flex justify-between items-center opacity-80"><span>SESSION</span><span class="text-content-main max-w-[150px] truncate text-right">{electionName}</span></div>
             <div class="flex justify-between items-center opacity-80"><span>CERTIFIED</span><span class="text-content-main font-bold">{new Date().toLocaleDateString()}</span></div>
             <div class="pt-6 mt-6 border-t border-dashed border-line-main flex flex-col items-center gap-3">
               <span class="text-[10px] uppercase tracking-widest text-content-muted">BLOCKCHAIN RECEIPT NO.</span>
               <span class="text-[0.9rem] font-black text-[var(--status-success-fg)] tracking-[0.1em] break-all text-center">{receiptId || 'PENDING...'}</span>
             </div>
          </div>
          <div class="text-center text-[10px] text-content-subtle font-bold uppercase tracking-widest leading-relaxed">This receipt is your cryptographic proof of participation.</div>
        </div>
        <div class="mt-8 text-center px-4" in:fade={{ delay: 800 }}>
          <a href="/student" class="btn-primary w-full shadow-2xl">Return to Portal</a>
        </div>
      </div>
    </div>

  {:else if isLoading}
    <!-- Loading -->
    <div class="min-h-screen flex flex-col items-center justify-center gap-6">
      <LoadingSpinner />
      <p class="text-content-subtle font-black text-[10px] uppercase tracking-[0.3em] animate-pulse">Initializing Secure Protocol...</p>
    </div>

  {:else}
    <!-- Main Ballot -->
    <GlassCard title={electionId ? "Official Ballot" : "Voting Room"} subtitle={electionId ? electionName : "Secure Election Portal"}>
      {#snippet headerExtra()}
        {#if electionId}
          <div class="mt-4 lg:mt-0 flex flex-col items-end gap-2" in:fly={{ x: 20, duration: 800, delay: 200 }}>
            <div class="flex items-center gap-3 bg-surface-elevated border border-line-subtle rounded-2xl px-5 py-3 shadow-inner">
               <div class="text-right">
                 <p class="text-lg font-black text-content-main tracking-widest leading-none">{selectedCount}/{totalPositions}</p>
                 <p class="text-[9px] font-black text-content-subtle uppercase tracking-widest mt-1">Assignments</p>
               </div>
               <div class="w-8 h-8 rounded-full border-2 border-[var(--status-success-bg)] flex items-center justify-center relative bg-[var(--status-success-bg)] text-[var(--status-success-fg)]">
                  {#if allSelected}
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                  {/if}
               </div>
            </div>
          </div>
        {/if}
      {/snippet}

      {#if !electionId}
        <!-- Election List View -->
        {@const elections = ($voterSession?.elections || []).filter(e => !e.has_voted)}
        {#if elections.length === 0}
          <div class="empty-state">You have completed all active election sessions. Thank you for participating in the democratic process.</div>
        {:else}
          <div class="bento-grid bento-2col" style="margin-top:1.5rem;">
            {#each elections as election}
              <div class="admin-card group" style="padding:2rem;text-align:center;display:flex;flex-direction:column;align-items:center;">
                <div class="w-16 h-16 bg-surface-main border border-line-main rounded-2xl flex items-center justify-center mb-6 shadow-sm transition-transform group-hover:scale-110">
                   <svg class="w-8 h-8 text-brand-primary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                </div>
                <h3 class="text-lg font-black text-content-main mb-2 uppercase tracking-tight group-hover:text-brand-primary transition-colors">{election.name}</h3>
                <p class="text-[10px] font-black text-content-subtle uppercase tracking-widest mb-8">Verification Required</p>
                <a href="/student/ballot?election={election.id}" class="btn-primary w-full">Enter Booth</a>
              </div>
            {/each}
          </div>
        {/if}

      {:else}
        <!-- Ballot Form -->
        <div style="margin-top:1.5rem;display:flex;flex-direction:column;gap:3rem;">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-line-main" in:fly={{ y: 20, duration: 800, delay: 300 }}>
             <div>
                <h2 class="text-xl font-black text-content-main tracking-tight leading-tight mb-2">Authenticated Session: Welcome {voterName.split(' ')[0]}</h2>
                <p class="text-sm font-medium text-content-muted leading-relaxed">Assign your choices carefully. Selections are encrypted and cannot be altered.</p>
             </div>
             <a href="/student/ballot" class="btn-secondary whitespace-nowrap">Abort Session</a>
          </div>

          {#if errorMessage}
            <div class="pill pill-danger" style="width:100%;justify-content:flex-start;">{errorMessage}</div>
          {/if}

          {#if totalPositions === 0}
            <div class="empty-state">This election session has no candidates assigned.</div>
          {:else}
            <div style="display:flex;flex-direction:column;gap:4rem;">
              {#each positionOrder as position, idx}
                {@const list = candidatesGrouped[position] || []}
                {@const isComplete = !!selectedVotes[position]}

                <div in:fly={{ y: 20, duration: 800, delay: 400 + idx * 100 }}>
                  <div class="flex items-center gap-4 mb-6">
                    <div class="w-10 h-10 {isComplete ? 'bg-[var(--status-success-bg)] text-[var(--status-success-fg)]' : 'bg-surface-elevated text-content-main'} rounded-xl flex items-center justify-center text-sm font-black transition-all shadow-sm">
                      {#if isComplete}
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                      {:else} {idx + 1} {/if}
                    </div>
                    <div>
                      <h2 class="text-base font-black text-content-main uppercase tracking-tight">{position}</h2>
                      <p class="text-[10px] font-black text-content-subtle uppercase tracking-widest mt-0.5">
                        {isComplete ? 'Selection Recorded' : 'Select candidate'}
                      </p>
                    </div>
                  </div>

                  <div class="bento-grid bento-3col text-center">
                    {#each list as candidate}
                      {@const isSelected = selectedVotes[position] === candidate.id}
                      <label class="cursor-pointer select-none group relative h-full">
                        <input type="radio" name={position} value={candidate.id} bind:group={selectedVotes[position]} class="sr-only" />
                        <div class="h-full bg-surface-card border rounded-[1.5rem] p-6 flex flex-col items-center transition-all duration-300 active:scale-95 shadow-sm
                             {isSelected ? 'border-[var(--status-success-fg)] shadow-[var(--status-success-bg)]' : 'border-line-main group-hover:border-line-strong'}"
                        >
                          <div class="avatar-initial w-16 h-16 rounded-2xl flex items-center justify-center text-xl font-black mb-4 transition-all
                               {isSelected ? 'bg-[var(--status-success-bg)] text-[var(--status-success-fg)] scale-110' : 'bg-surface-elevated text-content-muted'}">
                            {getMonogram(candidate.name)}
                          </div>
                          
                          <div class="flex-1">
                            <h4 class="text-sm font-black text-content-main mb-1">{candidate.name}</h4>
                            <p class="text-[9px] font-black text-content-subtle uppercase tracking-[0.2em]">{candidate.party}</p>
                          </div>

                          <div class="mt-4 flex items-center gap-2">
                             <div class="w-2 h-2 rounded-full transition-all {isSelected ? 'bg-[var(--status-success-fg)]' : 'bg-line-main'}"></div>
                             <span class="text-[9px] font-black uppercase tracking-[0.2em] {isSelected ? 'text-[var(--status-success-fg)]' : 'text-content-subtle'}">
                               {isSelected ? 'SELECTED' : 'CHOOSE'}
                             </span>
                          </div>
                        </div>
                      </label>
                    {/each}
                  </div>
                </div>
              {/each}
            </div>

            <div class="mt-12 bg-surface-elevated p-8 rounded-[2rem] flex flex-col items-center text-center shadow-inner border border-line-subtle" in:fly={{ y: 20, duration: 1000, delay: 600 }}>
              <h3 class="text-xl font-black text-content-main tracking-tight mb-2">
                {allSelected ? 'Protocol Complete' : 'Protocol Pending'}
              </h3>
              <p class="text-content-muted text-sm font-medium mb-8">
                {allSelected ? 'All ballot assignments have been recorded. Proceed to final encryption.' : `You must designate candidates for all ${totalPositions} positions.`}
              </p>
              <button onclick={() => showConfirm = true} disabled={!allSelected} class="btn-primary" style="padding:1rem 2rem;font-size:0.875rem;">
                Certify Ballot
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </GlassCard>
  {/if}
</div>

<!-- Confirm Modal -->
{#if showConfirm}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div 
    class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-surface-main/80 backdrop-blur-md"
    in:fade={{ duration: 200 }}
    onclick={(e) => { if (e.target === e.currentTarget) showConfirm = false; }} onkeydown={() => {}}
  >
    <div class="bg-surface-card border border-line-main rounded-[2rem] w-full max-w-md p-8 shadow-2xl" in:fly={{ y: 20, duration: 250 }}>
      <h3 class="text-xl font-black text-content-main mb-2">Confirm Ballot</h3>
      <p class="text-xs text-content-muted mb-6 font-medium">Your vote is anonymous and final. Are you sure you want to proceed?</p>
      
      <div class="bg-surface-elevated border border-line-subtle rounded-2xl p-4 mb-6 space-y-3 max-h-48 overflow-y-auto">
        {#each getReviewList() as item}
          <div class="flex items-center justify-between border-b border-line-main last:border-0 pb-2 last:pb-0">
            <span class="text-[10px] font-black text-content-subtle uppercase tracking-widest">{item.position}</span>
            <span class="text-xs font-black text-content-main">{item.candidate?.name}</span>
          </div>
        {/each}
      </div>

      <div class="mb-8">
        <div class="flex items-center justify-between mb-3">
          <label for="pin-input" class="text-[10px] font-bold text-content-muted uppercase tracking-widest">Enter Voting PIN</label>
          {#if !showPin}
            <button onclick={fetchPin} class="text-[10px] font-black text-brand-primary hover:underline">Show My PIN</button>
          {/if}
        </div>

        {#if showPin}
          <div class="mb-4 pill pill-success" style="justify-content:space-between;border-radius:1rem;">
            <div>
              <p class="text-[9px] font-black uppercase tracking-widest mb-0.5 opacity-80">Unique PIN</p>
              <p class="text-lg font-mono font-black tracking-[0.2em]">{votingPin}</p>
            </div>
            <button onclick={() => showPin = false} class="opacity-60 hover:opacity-100" aria-label="Close PIN">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        {/if}

        <input 
          id="pin-input" type="text" bind:value={pinConfirmInput} maxlength="6" placeholder="XXXXXX"
          class="input-base w-full text-center text-lg font-mono font-black tracking-[0.3em] uppercase py-4"
        />
        
        {#if errorMessage}
           <div class="pill pill-danger mt-4" style="font-size:0.6875rem;">{errorMessage}</div>
        {/if}
      </div>

      <div class="flex gap-4">
        <button onclick={() => { showConfirm = false; pinConfirmInput = ''; errorMessage = ''; }} class="btn-secondary flex-1">Go Back</button>
        <button onclick={submitVote} disabled={isSubmitting || pinConfirmInput.length < 6 || retrySeconds > 0} class="btn-primary flex-1">
          {#if isSubmitting} <LoadingSpinner /> Casting... {:else} Cast Vote {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

{#if toastVisible}
  <div class="fixed bottom-6 left-1/2 -translate-x-1/2 pill pill-success z-[200] shadow-xl" in:fly={{ y: 16, duration: 300 }} out:fade={{ duration: 200 }}>
    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
    <span>{toastMessage}</span>
  </div>
{/if}
