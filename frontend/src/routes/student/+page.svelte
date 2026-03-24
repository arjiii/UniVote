<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { fade } from 'svelte/transition';

  let isLoading = $state(true);
  let elections = $derived($voterSession?.elections || []);
  let voterName = $derived($voterSession?.full_name || 'Student');

  let selectedSummaryElection = $state(/** @type {string | null} */ (null));
  let summaryLoading = $state(false);
  let receiptId = $state('');
  let votedAt = $state('');
  /** @type {any[]} */
  let voteDetails = $state([]);

  onMount(async () => {
    const session = $voterSession;
    if (!session) { goto('/student/validate'); return; }
    try {
      const resp = await studentApi.validate(session.student_id);
      if (resp?.student) {
        voterSession.login({ ...resp.student, access_token: resp.access_token, elections: resp.active_elections });
      }
    } catch (err) { console.error('Session sync failed:', err); }
    finally { isLoading = false; }
  });

  const stats = $derived({
    total:   elections.length,
    voted:   elections.filter(/** @param {any} e */ e => e.has_voted).length,
    pending: elections.length - elections.filter(/** @param {any} e */ e => e.has_voted).length
  });

  /** @param {string} electionId */
  async function loadVoteSummary(electionId) {
    const session = $voterSession;
    if (!session) return;
    if (selectedSummaryElection === electionId) { selectedSummaryElection = null; return; }
    selectedSummaryElection = electionId;
    summaryLoading = true;
    try {
      const data = await studentApi.getVoteSummary(session.student_id, electionId);
      receiptId   = data.receipt_id || '';
      votedAt     = data.voted_at   || '';
      voteDetails = data.votes      || [];
    } catch (err) { console.error('Vote summary load failed:', err); }
    finally { summaryLoading = false; }
  }

  /** @param {string} firstName */
  function greeting(firstName) {
    const h = new Date().getHours();
    if (h < 12) return `Good morning, ${firstName}`;
    if (h < 18) return `Good afternoon, ${firstName}`;
    return `Good evening, ${firstName}`;
  }
</script>

<svelte:head><title>Student Dashboard | UniVote</title></svelte:head>

<GlassCard title={greeting(voterName.split(' ')[0])} subtitle="Student Portal">

  {#if isLoading}
    <div style="padding:3rem 0;display:flex;flex-direction:column;align-items:center;gap:0.75rem;">
      <div class="spinner"></div>
      <p style="font-size:0.75rem;color:var(--text-subtle);font-weight:500;">Synchronizing account…</p>
    </div>

  {:else}
    <!-- Stats row -->
    {#if elections.length > 0}
      {@const s = stats}
      <div class="bento-grid bento-3col">
        <div class="stat-card">
          <p class="section-label">Total Elections</p>
          <p style="font-size:1.75rem;font-weight:800;color:var(--text-main);line-height:1;margin-top:0.25rem;">{s.total}</p>
        </div>
        <div class="stat-card">
          <p class="section-label" style="color:var(--status-success-fg);">Votes Cast</p>
          <p style="font-size:1.75rem;font-weight:800;color:var(--status-success-fg);line-height:1;margin-top:0.25rem;">{s.voted}</p>
        </div>
        <div class="stat-card">
          <p class="section-label" style="color:var(--status-warning-fg);">Pending</p>
          <p style="font-size:1.75rem;font-weight:800;color:var(--status-warning-fg);line-height:1;margin-top:0.25rem;">{s.pending}</p>
        </div>
      </div>
    {/if}

    <!-- Election list -->
    {#if elections.length === 0}
      <div class="empty-state">
        <svg style="width:2rem;height:2rem;color:var(--border-strong);margin-bottom:0.75rem;" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        <p style="font-weight:600;color:var(--text-muted);margin-bottom:0.25rem;">No active elections</p>
        <p style="font-size:0.8125rem;">You have no elections currently assigned. Check back later.</p>
      </div>
    {:else}
      <div>
        <p class="section-label" style="margin-bottom:0.75rem;">Active Elections ({elections.length})</p>
        <div style="display:flex;flex-direction:column;gap:0.75rem;">
          {#each elections as election, idx}
            <div class="election-card admin-card" in:fade={{ duration: 200, delay: idx * 50 }}>
              <div class="election-card-header">
                <!-- Left: icon + info -->
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <div class="election-icon {election.has_voted ? 'voted' : 'pending'}">
                    {#if election.has_voted}
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                    {:else}
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    {/if}
                  </div>
                  <div>
                    <p class="election-name">{election.name}</p>
                    <p class="election-date">Ends {new Date(election.end_date ?? Date.now()).toLocaleDateString()}</p>
                  </div>
                </div>
                <!-- Right: badge -->
                <StatusBadge status={election.has_voted ? 'voted' : 'pending'} />
              </div>

              <!-- Actions -->
              <div class="election-card-actions">
                {#if election.has_voted}
                  <button onclick={() => loadVoteSummary(election.id)} class="btn-secondary btn-sm">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>
                    {selectedSummaryElection === election.id ? 'Hide Receipt' : 'View Receipt'}
                  </button>
                  <a href="/student/results?election={election.id}" class="btn-ghost btn-sm">Results</a>
                {:else}
                  <a href="/student/ballot?election={election.id}" class="btn-primary btn-sm" style="text-decoration:none;display:inline-flex;align-items:center;gap:0.375rem;">
                    Cast Vote
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/></svg>
                  </a>
                  <a href="/student/results?election={election.id}" class="btn-ghost btn-sm" style="text-decoration:none;">Results</a>
                {/if}
              </div>

              <!-- Receipt drawer -->
              {#if selectedSummaryElection === election.id}
                <div class="receipt-drawer" in:fade={{ duration: 150 }}>
                  {#if summaryLoading}
                    <div style="display:flex;align-items:center;gap:0.5rem;padding:1rem;">
                      <div class="spinner" style="width:1rem;height:1rem;border-width:2px;"></div>
                      <span style="font-size:0.75rem;color:var(--text-subtle);">Loading receipt…</span>
                    </div>
                  {:else}
                    <!-- Receipt ID -->
                    <div class="receipt-id-row">
                      <div>
                        <p class="section-label">Receipt ID</p>
                        <code style="font-size:0.75rem;font-weight:600;color:var(--text-main);word-break:break-all;">{receiptId}</code>
                      </div>
                      <button
                        onclick={() => navigator.clipboard.writeText(receiptId)}
                        class="btn-icon" title="Copy to clipboard"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/></svg>
                      </button>
                    </div>
                    {#if votedAt}
                      <p style="font-size:0.6875rem;color:var(--status-success-fg);margin-bottom:0.75rem;display:flex;align-items:center;gap:0.375rem;">
                        <span style="width:5px;height:5px;background:currentColor;border-radius:50%;display:inline-block;"></span>
                        Certified at {new Date(votedAt).toLocaleString()}
                      </p>
                    {/if}
                    <!-- Votes -->
                    <div style="display:flex;flex-direction:column;gap:0.375rem;">
                      {#each voteDetails as vote}
                        <div class="vote-row">
                          <div>
                            <p class="section-label">{vote.position}</p>
                            <p style="font-size:0.8125rem;font-weight:600;color:var(--text-main);">{vote.candidates?.students?.full_name || 'Unknown'}</p>
                            <p style="font-size:0.6875rem;color:var(--text-subtle);">{vote.candidates?.partylists?.name || 'Independent'}</p>
                          </div>
                          <span class="pill pill-success pill-dot">Certified</span>
                        </div>
                      {/each}
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</GlassCard>

<style>
  .election-card-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.875rem 1rem;
    border-bottom: 1px solid var(--border-subtle);
    gap: 0.75rem;
  }
  .election-icon {
    width: 34px; height: 34px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .election-icon.voted   { background-color: var(--status-success-bg); color: var(--status-success-fg); }
  .election-icon.pending { background-color: var(--bg-elevated); color: var(--text-subtle); }
  .election-name { font-size: 0.875rem; font-weight: 600; color: var(--text-main); }
  .election-date { font-size: 0.6875rem; color: var(--text-subtle); margin-top: 0.125rem; }

  .election-card-actions {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.625rem 1rem;
  }

  .receipt-drawer {
    border-top: 1px solid var(--border-main);
    padding: 1rem;
    background-color: var(--bg-elevated);
    display: flex; flex-direction: column; gap: 0.75rem;
  }
  .receipt-id-row {
    display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem;
    background-color: var(--bg-card);
    border: 1px solid var(--border-main);
    border-radius: 6px;
    padding: 0.625rem 0.75rem;
  }
  .vote-row {
    display: flex; align-items: center; justify-content: space-between;
    background-color: var(--bg-card);
    border: 1px solid var(--border-main);
    border-radius: 6px;
    padding: 0.625rem 0.75rem;
    gap: 0.75rem;
  }

  @media (max-width: 640px) {
    .bento-grid { grid-template-columns: 1fr !important; }
  }
</style>
