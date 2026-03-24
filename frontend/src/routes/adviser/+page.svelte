<script>
  import { onMount } from 'svelte';
  import { admin, adviser } from '$lib/api.js';
  import { selectedElectionId } from '$lib/stores/election.js';
  import { authSession } from '$lib/stores/auth.js';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { goto } from '$app/navigation';

  /** @type {any[]} */
  let elections = $state([]);
  let summary = $state({ candidates: 0, partylists: 0, totalVotes: 0 });
  let isRefreshing = $state(false);

  async function loadSummary() {
    if (!$selectedElectionId) return;
    try {
      const [pRes, cRes, lRes] = await Promise.all([
        adviser.getPartylists($selectedElectionId),
        adviser.getCandidates($selectedElectionId),
        adviser.getLiveResults($selectedElectionId)
      ]);
      const res = lRes.data || {};
      const liveResults = res.tallies || res;
      let voteCount = 0;
      Object.values(liveResults).forEach(posVotes => {
        if (typeof posVotes === 'object' && posVotes !== null) {
          Object.values(posVotes).forEach(count => { voteCount += Number(count); });
        }
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

  async function refreshPasscode() {
    if (!$selectedElectionId) return;
    isRefreshing = true;
    try {
      const res = await adviser.refreshPasscode($selectedElectionId);
      elections = elections.map(e => e.id === $selectedElectionId ? { ...e, adviser_passcode: res.adviser_passcode } : e);
    } catch (err) { console.error('Failed to refresh passcode:', err); }
    finally { isRefreshing = false; }
  }

  onMount(async () => {
    await loadElections();
    if ($selectedElectionId) await loadSummary();
  });

  $effect(() => { if ($selectedElectionId) { loadSummary(); } });

  const currentElection = $derived(elections.find(e => e.id === $selectedElectionId));

  const navCards = [
    { name: 'Candidates', path: '/adviser/candidates', desc: 'Manage election participants', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
    { name: 'Partylists',  path: '/adviser/partylists',  desc: 'Manage political organizations', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
    { name: 'Results',    path: '/adviser/results',    desc: 'Monitor live ballot tallies', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { name: 'Audit Logs',  path: '/adviser/audit',      desc: 'Review administrative actions', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
  ];
</script>

<svelte:head><title>Adviser Dashboard | UniVote</title></svelte:head>

<GlassCard title="Dashboard" subtitle="Adviser Portal — {$authSession?.full_name || ''}">
  {#snippet headerExtra()}
    <div style="display:flex;align-items:center;gap:0.5rem;">
      <label class="field-label" for="election-select" style="margin-bottom:0;white-space:nowrap;">Election:</label>
      <select
        id="election-select"
        bind:value={$selectedElectionId}
        class="input-base btn-sm"
        style="min-width:180px;width:auto;"
      >
        <option value="" disabled>Select election</option>
        {#each elections as election}
          <option value={election.id}>{election.name}</option>
        {/each}
      </select>
    </div>
  {/snippet}

  <!-- KPI Stats -->
  <div class="bento-grid bento-3col">
    {#each [
      { label: 'Candidates',   value: summary.candidates,  color: '#2563EB' },
      { label: 'Partylists',   value: summary.partylists,  color: '#7C3AED' },
      { label: 'Votes Cast',   value: summary.totalVotes,  color: '#16A34A' },
    ] as stat}
      <div class="stat-card">
        <div style="width:6px;height:6px;border-radius:50%;background-color:{stat.color};margin-bottom:0.5rem;"></div>
        <p style="font-size:1.5rem;font-weight:800;color:var(--text-main);line-height:1;">{stat.value}</p>
        <p class="section-label" style="margin-top:0.25rem;">{stat.label}</p>
      </div>
    {/each}
  </div>

  <!-- Passcode Panel -->
  {#if currentElection}
    <div class="admin-card" style="padding:1rem;">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:0.75rem;">
          <div style="width:32px;height:32px;background-color:var(--status-info-bg);color:var(--status-info-fg);border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg style="width:1rem;height:1rem;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/></svg>
          </div>
          <div>
            <p class="section-label">Student Entry Passcode</p>
            <code style="font-size:1.0625rem;font-weight:700;color:var(--text-main);letter-spacing:0.15em;">
              {currentElection?.adviser_passcode || '—'}
            </code>
          </div>
        </div>
        <button onclick={refreshPasscode} disabled={isRefreshing} class="btn-secondary btn-sm">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/></svg>
          {isRefreshing ? 'Refreshing…' : 'Refresh Passcode'}
        </button>
      </div>
    </div>
  {/if}

  <!-- Quick Nav Cards -->
  <div>
    <p class="section-label" style="margin-bottom:0.75rem;">Quick Access</p>
    <div class="bento-grid bento-4col">
      {#each navCards as card}
        <a href={card.path} class="admin-card nav-card" style="padding:1rem;text-decoration:none;display:flex;flex-direction:column;gap:0.625rem;">
          <div style="width:32px;height:32px;background-color:var(--bg-elevated);color:var(--text-muted);border-radius:6px;display:flex;align-items:center;justify-content:center;">
            <svg style="width:1rem;height:1rem;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d={card.icon}/>
            </svg>
          </div>
          <div>
            <p style="font-size:0.8125rem;font-weight:600;color:var(--text-main);">{card.name}</p>
            <p style="font-size:0.6875rem;color:var(--text-subtle);margin-top:0.125rem;">{card.desc}</p>
          </div>
        </a>
      {/each}
    </div>
  </div>
</GlassCard>

<style>
  .nav-card { transition: border-color 0.15s, box-shadow 0.15s; }
  .nav-card:hover { border-color: var(--brand-primary); box-shadow: 0 0 0 3px var(--brand-glow); }
  @media (max-width: 768px) { .bento-grid { grid-template-columns: 1fr 1fr !important; } }
</style>
