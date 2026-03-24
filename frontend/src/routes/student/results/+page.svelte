<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import { page } from '$app/state';
  import { fade, fly } from 'svelte/transition';
  import { sortPositions, calculateWinners } from '$lib/constants.js';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import { BASE } from '$lib/api.js';

  const SSE_BASE = `${BASE}/api/results/adviser/stream`;

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

    const urlId = page.url.searchParams.get('election');
    const defaultId = session.elections?.[0]?.id ?? '';
    const targetId = urlId || defaultId;

    if (targetId) loadResults(targetId);
    else isLoading = false;

    return () => closeSSE();
  });

  function closeSSE() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  }

  function openSSE(/** @type {string} */ targetId) {
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
        lastUpdated = new Date().toLocaleTimeString();
      } catch (err) { console.error('SSE parse error:', err); }
    };
    eventSource.onerror = () => console.warn('SSE connection lost, retrying...');
  }

  async function loadResults(/** @type {string} */ targetId) {
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
    } catch (err) { console.error('Failed to load results:', err); } 
    finally {
      isLoading = false;
      openSSE(targetId);
    }
  }

  async function handleElectionChange(/** @type {Event} */ e) {
    const newId = /** @type {HTMLSelectElement} */ (e.target).value;
    if (!newId) return;
    isLoading = true;
    await loadResults(newId);
  }

  function getCandidateInfo(/** @type {string} */ candidateId) {
    const c = candidates.find(/** @param {any} c */ c => c.id === candidateId);
    return { name: c?.students?.full_name || 'Unknown', party: c?.partylists?.name || 'Independent' };
  }

  function getPositionResults(/** @type {string} */ position) {
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

<svelte:head><title>Election Results | UniVote</title></svelte:head>

<GlassCard title="Election Outcomes" subtitle="Official Results & Tally">
  {#snippet headerExtra()}
    <div style="display:flex;align-items:center;gap:1.5rem;" in:fly={{ x: 20, duration: 800, delay: 200 }}>
      <!-- Election Selector -->
      <div style="display:flex;align-items:center;gap:0.75rem;">
        <label for="election-select" class="field-label" style="margin-bottom:0;line-height:1;">Session</label>
        <select 
          id="election-select" class="input-base" style="width:200px;padding:0.375rem 0.75rem;font-size:0.8125rem;"
          bind:value={electionId} onchange={handleElectionChange}
        >
          {#each availableElections as e}
            <option value={e.id}>{e.name}</option>
          {/each}
        </select>
      </div>
      
      <!-- SSE Indicator -->
      <div class="pill pill-success pill-dot" style="font-size:0.6875rem;">
        {lastUpdated ? `Live: ${lastUpdated}` : 'Connecting...'}
      </div>
    </div>
  {/snippet}

  {#if isLoading}
    <div class="empty-state" style="border:none;">
      <LoadingSpinner />
      <span style="display:block;margin-top:1rem;">Syncing Cryptographic Data...</span>
    </div>
  {:else if positions.length === 0}
    <div class="empty-state">This election session has not yet recorded any validated ballots.</div>
  {:else}
    <div style="display:flex;flex-direction:column;gap:2rem;">
      <!-- Certified block -->
      {#if isCompleted}
        <div in:fade={{ duration: 600 }}>
          <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.5rem;">
            <div class="pill pill-warning pill-dot" style="font-size:0.875rem;">Election Certified</div>
            <h2 style="font-size:1.125rem;font-weight:700;color:var(--text-main);">Official Winners</h2>
          </div>
          
          <div class="bento-grid bento-3col">
            {#each positions as position}
              {#if winnersData[position] && winnersData[position].length > 0}
                <div class="admin-card" style="padding:1.5rem;display:flex;flex-direction:column;align-items:center;text-align:center;">
                  <p class="section-label" style="margin-bottom:1.25rem;">{position}</p>
                  {#each winnersData[position] as winner}
                    <div class="avatar-initial" style="width:64px;height:64px;border-radius:16px;font-size:1.5rem;margin-bottom:1rem;color:var(--status-warning-fg);background:var(--status-warning-bg);border-color:transparent;">
                      {winner.students?.full_name?.charAt(0) || '?'}
                    </div>
                    <h3 style="font-size:1rem;font-weight:700;color:var(--text-main);">{winner.students?.full_name || 'Unknown'}</h3>
                    <p style="font-size:0.6875rem;color:var(--text-muted);margin-top:0.25rem;">{winner.partylists?.name || 'Independent'}</p>
                    <div class="pill pill-warning" style="margin-top:1rem;">
                      {(results[position] || {})[winner.id] || 0} Votes
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
        <h2 style="font-size:1.125rem;font-weight:700;color:var(--text-main);margin-bottom:1.5rem;">Real-time Metrics</h2>

        <div class="bento-grid bento-2col">
          {#each positions as position, idx}
            {@const { entries, totalVotes } = getPositionResults(position)}
            <div class="admin-card" style="padding:1.5rem;" in:fly={{ y: 20, duration: 800, delay: idx * 100 }}>
              <div style="display:flex;align-items:flex-start;justify-content:space-between;border-bottom:1px solid var(--border-main);padding-bottom:1rem;margin-bottom:1.25rem;">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <div class="avatar-initial" style="width:28px;height:28px;border-radius:6px;font-size:0.75rem;">{idx + 1}</div>
                  <h2 style="font-size:0.875rem;font-weight:700;color:var(--text-main);">{position}</h2>
                </div>
                <span class="section-label">{totalVotes} Total Votes</span>
              </div>
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
                    <div style="height:6px;background-color:var(--border-subtle);border-radius:3px;overflow:hidden;">
                      <div style="height:100%;border-radius:3px;background-color:{isLeading ? 'var(--status-success-fg)' : 'var(--text-muted)'};width:{pct}%;transition:width 1s ease-out;"></div>
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
