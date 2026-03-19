<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';

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
  function actionColor(action) {
    if (action?.includes('DELETE')) return 'bg-red-50 text-red-600 border-red-100';
    if (action?.includes('CREATE') || action?.includes('ADD') || action?.includes('IMPORT')) return 'bg-emerald-50 text-emerald-700 border-emerald-100';
    if (action?.includes('UPDATE') || action?.includes('STATUS')) return 'bg-blue-50 text-blue-700 border-blue-100';
    return 'bg-stone-100 text-stone-600 border-stone-200';
  }

  /** @param {string} action */
  function actionIcon(action) {
    if (action?.includes('DELETE')) return 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16';
    if (action?.includes('CREATE') || action?.includes('ADD') || action?.includes('IMPORT')) return 'M12 6v6m0 0v6m0-6h6m-6 0H6';
    if (action?.includes('STATUS')) return 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15';
    return 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z';
  }
</script>

<svelte:head>
  <title>Audit Logs | UniVote Admin</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">

  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    <div>
      <p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-1">Admin</p>
      <h1 class="text-2xl font-semibold text-stone-900 dark:text-white">Audit Logs</h1>
      <p class="text-stone-500 dark:text-stone-400 text-sm mt-0.5">A complete record of all system actions.</p>
    </div>
    <div class="flex items-center gap-2 bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl shadow-sm">
      <div class="relative w-64">
        <svg class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-stone-400 dark:text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          bind:value={searchQuery}
          placeholder="Search actions..."
          class="w-full pl-9 pr-4 py-2.5 bg-transparent text-stone-900 dark:text-white text-xs focus:outline-none rounded-xl placeholder-stone-400 dark:placeholder-stone-500"
        />
      </div>
    </div>
  </div>

  <!-- Stats row -->
  <div class="grid grid-cols-3 gap-4">
    {#each [
      { label: 'Total Events', value: auditLogs.length },
      { label: 'Admin Actions', value: auditLogs.filter(l => l.actor_role === 'admin').length },
      { label: 'Adviser Actions', value: auditLogs.filter(l => l.actor_role === 'adviser').length }
    ] as stat}
      <div class="bg-white dark:bg-stone-900 rounded-2xl border border-stone-200 dark:border-stone-700 p-4 text-center">
        <p class="text-2xl font-semibold text-stone-900 dark:text-white">{stat.value}</p>
        <p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 uppercase tracking-widest mt-1">{stat.label}</p>
      </div>
    {/each}
  </div>

  <!-- Log Table -->
  <div class="bg-white dark:bg-stone-900 rounded-2xl border border-stone-200 dark:border-stone-700 overflow-hidden">
    <div class="px-6 py-4 border-b border-stone-100 dark:border-stone-700 flex items-center justify-between">
      <h2 class="text-sm font-semibold text-stone-900 dark:text-white">System Audit Trail</h2>
      <span class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 uppercase tracking-widest">
        {filteredLogs.length} record{filteredLogs.length !== 1 ? 's' : ''}
      </span>
    </div>

    {#if isLoading}
      <div class="py-20 flex items-center justify-center text-stone-400 dark:text-stone-500 text-sm animate-pulse">
        Retrieving audit logs...
      </div>
    {:else if filteredLogs.length === 0}
      <div class="py-20 flex flex-col items-center justify-center text-stone-400 dark:text-stone-500 text-xs gap-2">
        <svg class="w-8 h-8 text-stone-300 dark:text-stone-600" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
        </svg>
        <p>{searchQuery ? 'No logs match your search.' : 'No activity has been logged yet.'}</p>
      </div>
    {:else}
      <div class="divide-y divide-stone-50 dark:divide-stone-800">
        {#each filteredLogs as log}
          {@const color = actionColor(log.action)}
          <div class="flex items-start gap-4 px-6 py-4 hover:bg-stone-50/60 dark:hover:bg-stone-800/60 transition-colors">
            <!-- Icon -->
            <div class="w-8 h-8 rounded-lg border flex items-center justify-center shrink-0 mt-0.5 {color}">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d={actionIcon(log.action)}/>
              </svg>
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-0.5">
                <p class="text-xs font-bold text-stone-900 dark:text-white font-mono">{log.action}</p>
                {#if log.target_type}
                  <span class="text-[10px] font-semibold text-stone-400 dark:text-stone-400 uppercase tracking-tighter bg-stone-100 dark:bg-stone-800 px-1.5 py-0.5 rounded border border-stone-200 dark:border-stone-700">
                    {log.target_type}
                  </span>
                {/if}
                <span class="text-[10px] font-semibold uppercase tracking-tighter px-1.5 py-0.5 rounded border
                  {log.actor_role === 'admin' ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-100 dark:border-amber-800' : 'bg-violet-50 dark:bg-violet-900/30 text-violet-700 dark:text-violet-400 border-violet-100 dark:border-violet-800'}">
                  {log.actor_role}
                </span>
              </div>
              {#if log.details && Object.keys(log.details).length > 0}
                <p class="text-[10px] text-stone-400 dark:text-stone-500 truncate max-w-md">
                  {Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(' · ')}
                </p>
              {/if}
            </div>

            <!-- Timestamp -->
            <div class="text-right shrink-0">
              <p class="text-[10px] text-stone-400 dark:text-stone-500 whitespace-nowrap">{new Date(log.created_at).toLocaleString()}</p>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>
