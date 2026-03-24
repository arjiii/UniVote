<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import { goto } from '$app/navigation';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';

  /** @type {any[]} */
  let elections = $state([]);
  /** @type {any[]} */
  let students = $state([]);
  /** @type {any[]} */
  let advisers = $state([]);
  /** @type {any[]} */
  let auditLogs = $state([]);
  let isLoading = $state(true);

  onMount(async () => {
    try {
      const [electionsRes, studentsRes, advisersRes, logsRes] = await Promise.all([
        adminApi.getElections(),
        adminApi.getStudents(),
        adminApi.getAdvisers(),
        adminApi.getAuditLog()
      ]);
      elections = electionsRes.data ?? [];
      students  = studentsRes.data  ?? [];
      advisers  = advisersRes.data  ?? [];
      auditLogs = logsRes.data      ?? [];
    } catch (err) { console.error('Dashboard load error:', err); }
    finally { isLoading = false; }
  });

  const activeElections = $derived(elections.filter(e => e.status === 'active'));
  const recentLogs      = $derived(auditLogs.slice(0, 8));
</script>

<GlassCard title="Dashboard" subtitle="System Administrator">

  <!-- KPI Stats -->
  <div class="bento-grid bento-4col">
    {#each [
      { label: 'Elections',     value: elections.length,       path: '/admin/elections', color: '#2563EB' },
      { label: 'Active Now',    value: activeElections.length, path: '/admin/elections', color: '#16A34A' },
      { label: 'Total Voters',  value: students.length,        path: '/admin/voters',    color: '#7C3AED' },
      { label: 'Advisers',      value: advisers.length,        path: '/admin/advisers',  color: '#D97706' },
    ] as stat}
      <button onclick={() => goto(stat.path)} class="stat-card" style="text-align:left;cursor:pointer;">
        <div style="width:6px;height:6px;border-radius:50%;background-color:{stat.color};margin-bottom:0.625rem;"></div>
        {#if isLoading}
          <div class="skeleton" style="width:3rem;height:1.75rem;margin-bottom:0.25rem;"></div>
        {:else}
          <p style="font-size:1.5rem;font-weight:800;color:var(--text-main);line-height:1;">{stat.value}</p>
        {/if}
        <p class="section-label" style="margin-top:0.25rem;">{stat.label}</p>
      </button>
    {/each}
  </div>

  <!-- Bento: Active Elections + Activity Log -->
  <div class="bento-grid" style="grid-template-columns: 1fr 1fr; gap: 1rem;">

    <!-- Active Elections -->
    <div class="admin-card" style="overflow:hidden;">
      <div class="panel-header">
        <span class="panel-title">Active Elections</span>
        <button onclick={() => goto('/admin/elections')} class="btn-link" style="font-size:0.75rem;">All Elections →</button>
      </div>
      <div class="panel-body">
        {#if isLoading}
          {#each Array(3) as _}
            <div class="skeleton" style="height:2.5rem;width:100%;"></div>
          {/each}
        {:else if activeElections.length === 0}
          <div class="empty-state">No active elections right now.</div>
        {:else}
          {#each activeElections as election}
            <button onclick={() => goto('/admin/elections')} class="election-row">
              <div>
                <p class="election-name">{election.name}</p>
                <p style="font-size:0.6875rem;color:var(--text-subtle);margin-top:0.125rem;">
                  Ends {new Date(election.end_date).toLocaleDateString()} · {election.voters_count ?? 0} voters
                </p>
              </div>
              <div style="display:flex;align-items:center;gap:0.75rem;flex-shrink:0;">
                <span style="font-size:0.8125rem;font-weight:700;color:var(--text-main);">
                  {election.voters_count ? Math.round((election.votes_cast / election.voters_count) * 100) : 0}%
                </span>
                <StatusBadge status="active" />
              </div>
            </button>
          {/each}
        {/if}
      </div>
    </div>

    <!-- Activity Log -->
    <div class="admin-card" style="overflow:hidden;">
      <div class="panel-header">
        <span class="panel-title">Recent Activity</span>
        <button onclick={() => goto('/admin/audit')} class="btn-link" style="font-size:0.75rem;">Full Log →</button>
      </div>
      <div class="panel-body">
        {#if isLoading}
          {#each Array(5) as _}
            <div class="skeleton" style="height:2rem;width:100%;"></div>
          {/each}
        {:else if recentLogs.length === 0}
          <div class="empty-state">No activity logged yet.</div>
        {:else}
          {#each recentLogs as log}
            <div class="log-row">
              <span class="log-role-badge {log.actor_role === 'admin' ? 'log-admin' : 'log-adviser'}">
                {log.actor_role?.[0]?.toUpperCase()}
              </span>
              <div style="flex:1;min-width:0;">
                <p class="log-action">{log.action}</p>
                <p class="log-time">{new Date(log.created_at).toLocaleString([], { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' })}</p>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>

  <!-- Quick Links -->
  <div class="bento-grid bento-4col">
    {#each [
      { label: 'Manage Elections', path: '/admin/elections', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
      { label: 'Manage Voters',    path: '/admin/voters',    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
      { label: 'Manage Advisers',  path: '/admin/advisers',  icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
      { label: 'View Audit Logs',  path: '/admin/audit',     icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
    ] as link}
      <button onclick={() => goto(link.path)} class="quick-link">
        <div class="quick-link-icon">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d={link.icon}/>
          </svg>
        </div>
        <span class="quick-link-label">{link.label}</span>
      </button>
    {/each}
  </div>

</GlassCard>

<style>
  .panel-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-main);
  }
  .panel-title { font-size: 0.8125rem; font-weight: 600; color: var(--text-main); }
  .panel-body  { display: flex; flex-direction: column; gap: 0; }

  .election-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.625rem 1rem;
    border-bottom: 1px solid var(--border-subtle);
    background: transparent; border-left: none; border-right: none; border-top: none;
    cursor: pointer; text-align: left; width: 100%;
    transition: background-color 0.12s;
    gap: 1rem;
  }
  .election-row:last-child { border-bottom: none; }
  .election-row:hover { background-color: var(--bg-hover); }
  .election-name { font-size: 0.8125rem; font-weight: 600; color: var(--text-main); }

  .log-row {
    display: flex; align-items: flex-start; gap: 0.625rem;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid var(--border-subtle);
  }
  .log-row:last-child { border-bottom: none; }
  .log-role-badge {
    width: 22px; height: 22px; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6875rem; font-weight: 700;
    flex-shrink: 0; margin-top: 0.125rem;
  }
  .log-admin   { background-color: var(--status-warning-bg); color: var(--status-warning-fg); }
  .log-adviser { background-color: var(--status-info-bg);    color: var(--status-info-fg); }
  .log-action { font-size: 0.75rem; font-weight: 500; color: var(--text-main); line-height: 1.4; }
  .log-time   { font-size: 0.6875rem; color: var(--text-subtle); margin-top: 0.125rem; }

  .quick-link {
    display: flex; align-items: center; gap: 0.625rem;
    padding: 0.75rem;
    background-color: var(--bg-card);
    border: 1px solid var(--border-main);
    border-radius: 6px;
    cursor: pointer; text-align: left; width: 100%;
    transition: border-color 0.12s, background-color 0.12s;
  }
  .quick-link:hover { border-color: var(--brand-primary); background-color: var(--bg-hover); }
  .quick-link-icon {
    width: 30px; height: 30px;
    background-color: var(--bg-elevated);
    color: var(--text-muted);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .quick-link:hover .quick-link-icon { background-color: rgba(37,99,235,0.1); color: var(--brand-primary); }
  .quick-link-label { font-size: 0.75rem; font-weight: 600; color: var(--text-main); }

  @media (max-width: 768px) {
    .bento-grid { grid-template-columns: 1fr !important; }
  }
</style>
