<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import GlassCard from '$lib/components/GlassCard.svelte';

  /** @type {Array<any>} */
  let auditLogs = $state([]);
  let isLoading = $state(true);
  let searchQuery = $state('');

  onMount(async () => {
    try {
      const res = await adminApi.getAuditLog();
      auditLogs = res.data ?? [];
    } catch (err) {
      console.error('Failed to load audit log:', err);
    } finally {
      isLoading = false;
    }
  });

  const filteredLogs = $derived(
    searchQuery
      ? auditLogs.filter(log =>
          log.action?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          log.target_type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          log.actor_role?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      : auditLogs
  );

  /** @param {string} action */
  function actionIcon(action) {
    if (action?.includes('DELETE')) return 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16';
    if (action?.includes('CREATE') || action?.includes('ADD') || action?.includes('IMPORT')) return 'M12 6v6m0 0v6m0-6h6m-6 0H6';
    if (action?.includes('STATUS')) return 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15';
    return 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z';
  }
</script>

<svelte:head><title>Audit Logs | UniVote Admin</title></svelte:head>

<GlassCard title="Audit Logs" subtitle="System Administrator">
  {#snippet headerExtra()}
    <div style="position:relative;">
      <svg style="position:absolute;left:0.625rem;top:50%;transform:translateY(-50%);width:1rem;height:1rem;color:var(--text-subtle);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      <input
        bind:value={searchQuery}
        placeholder="Filter logs…"
        class="input-base btn-sm"
        style="padding-left:2rem;width:240px;"
      />
    </div>
  {/snippet}

  <!-- Stats row -->
  <div class="bento-grid bento-3col">
    {#each [
      { label: 'Total Events',    value: auditLogs.length, sub: 'All recorded ops' },
      { label: 'Admin Actions',   value: auditLogs.filter(l => l.actor_role === 'admin').length, sub: 'System level ops' },
      { label: 'Adviser Actions', value: auditLogs.filter(l => l.actor_role === 'adviser').length, sub: 'Gatekeeper ops' }
    ] as stat}
      <div class="stat-card">
        <p class="section-label">{stat.label}</p>
        <p style="font-size:1.75rem;font-weight:800;color:var(--text-main);line-height:1;margin-top:0.25rem;">{stat.value}</p>
        <p style="font-size:0.6875rem;color:var(--text-subtle);margin-top:0.25rem;">{stat.sub}</p>
      </div>
    {/each}
  </div>

  <!-- Log Table -->
  <div class="admin-card" style="overflow:hidden;">
    <div style="padding:0.75rem 1rem;border-bottom:1px solid var(--border-main);">
      <p class="section-label">
        {filteredLogs.length} event{filteredLogs.length !== 1 ? 's' : ''}
        {searchQuery ? ' matching filter' : ''}
      </p>
    </div>

    {#if isLoading}
      <div style="padding:1.5rem;display:flex;flex-direction:column;gap:0.5rem;">
        {#each Array(5) as _}
          <div class="skeleton" style="height:3rem;"></div>
        {/each}
      </div>
    {:else if filteredLogs.length === 0}
      <div class="empty-state">{searchQuery ? 'No logs match your filter.' : 'No protocol data recorded.'}</div>
    {:else}
      <div style="overflow-x:auto;">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:1%;">Icon</th>
              <th>Action</th>
              <th>Role</th>
              <th>Details</th>
              <th style="text-align:right;">Time</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredLogs as log (log.id || Math.random())}
              <tr>
                <td>
                  <div style="width:28px;height:28px;background-color:var(--bg-elevated);color:var(--text-muted);border-radius:6px;display:flex;align-items:center;justify-content:center;">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d={actionIcon(log.action)}/>
                    </svg>
                  </div>
                </td>
                <td style="font-weight:600;color:var(--text-main);font-size:0.75rem;">
                  {log.action}
                  {#if log.target_type}
                    <span style="display:inline-block;margin-left:0.375rem;padding:0.125rem 0.375rem;background-color:var(--bg-elevated);color:var(--text-subtle);border-radius:4px;font-size:0.625rem;">
                      {log.target_type}
                    </span>
                  {/if}
                </td>
                <td>
                  {#if log.actor_role === 'admin'}
                    <span class="pill pill-warning pill-dot">Admin</span>
                  {:else}
                    <span class="pill pill-info pill-dot">Adviser</span>
                  {/if}
                </td>
                <td style="color:var(--text-muted);max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                  {#if log.details && Object.keys(log.details).length > 0}
                    {Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(' · ')}
                  {:else}
                    <span style="color:var(--text-subtle);">None</span>
                  {/if}
                </td>
                <td style="text-align:right;white-space:nowrap;">
                  <span style="font-weight:600;color:var(--text-main);">{new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  <span style="display:block;font-size:0.625rem;color:var(--text-subtle);margin-top:0.125rem;">{new Date(log.created_at).toLocaleDateString()}</span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</GlassCard>
