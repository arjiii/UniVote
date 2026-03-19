<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import { goto } from '$app/navigation';

  let elections = $state([]);
  let students = $state([]);
  let advisers = $state([]);
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
      students = studentsRes.data ?? [];
      advisers = advisersRes.data ?? [];
      auditLogs = logsRes.data ?? [];
    } catch (err) { console.error('Failed to load dashboard data:', err); }
    finally { isLoading = false; }
  });

  const activeElections = $derived(elections.filter(e => e.status === 'active'));
  const recentLogs = $derived(auditLogs.slice(0, 5));
</script>

<svelte:head>
  <title>Admin Dashboard | UniVote</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">

  <!-- Header -->
  <div>
    <p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Admin</p>
    <h1 class="text-2xl font-semibold text-stone-900">Dashboard</h1>
    <p class="text-stone-500 text-sm mt-0.5">System overview at a glance.</p>
  </div>

  <!-- KPI Stats -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    {#each [
      { label: 'Total Elections', value: elections.length, path: '/admin/elections', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z', accent: 'bg-blue-500/10 text-blue-600 dark:text-blue-400' },
      { label: 'Active Now', value: activeElections.length, path: '/admin/elections', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', accent: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' },
      { label: 'Total Voters', value: students.length, path: '/admin/voters', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z', accent: 'bg-violet-500/10 text-violet-600 dark:text-violet-400' },
      { label: 'Advisers', value: advisers.length, path: '/admin/advisers', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z', accent: 'bg-amber-500/10 text-amber-600 dark:text-amber-400' }
    ] as stat}
      <button onclick={() => goto(stat.path)} class="card-themed p-5 text-left hover:border-brand-500/30 transition-all group outline-none">
        <div class="w-10 h-10 {stat.accent} rounded-xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={stat.icon}/></svg>
        </div>
        {#if isLoading}
          <div class="h-8 w-12 bg-stone-100 dark:bg-stone-800 rounded-lg animate-pulse mb-2"></div>
        {:else}
          <p class="text-3xl font-bold text-stone-900 dark:text-white transition-colors">{stat.value}</p>
        {/if}
        <p class="text-[10px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-[0.15em] mt-1.5">{stat.label}</p>
      </button>
    {/each}
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Active Elections -->
    <div class="card-themed p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-sm font-bold text-stone-900 dark:text-white">Active Elections</h2>
        <button onclick={() => goto('/admin/elections')} class="text-[10px] font-bold text-stone-400 hover:text-stone-900 dark:hover:text-white uppercase tracking-widest transition-colors">View all →</button>
      </div>
      {#if isLoading}
        <div class="space-y-3">
          {#each Array(3) as _}
            <div class="h-16 bg-stone-50 dark:bg-stone-800/50 rounded-xl animate-pulse"></div>
          {/each}
        </div>
      {:else if activeElections.length === 0}
        <div class="py-12 text-center text-stone-400 dark:text-stone-500 text-xs italic border-2 border-dashed border-stone-100 dark:border-stone-800 rounded-2xl">No active elections right now.</div>
      {:else}
        <div class="grid grid-cols-1 gap-4">
          {#each activeElections as election}
            <div class="card-themed p-5 flex items-center justify-between group">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-stone-50 dark:bg-stone-800/50 flex items-center justify-center text-stone-400 dark:text-stone-600 border border-stone-100 dark:border-stone-800 group-hover:scale-110 transition-transform duration-300">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-bold text-stone-900 dark:text-white transition-colors">{election.name}</h4>
                  <p class="text-xs text-stone-400 dark:text-stone-500 mt-1 font-medium">{election.voters_count} registered voters • Ends {new Date(election.end_date).toLocaleDateString()}</p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div class="text-right hidden sm:block">
                  <p class="text-xs font-bold text-stone-900 dark:text-white transition-colors">{Math.round((election.votes_cast / election.voters_count) * 100)}%</p>
                  <p class="text-[10px] font-bold text-stone-400 uppercase tracking-tighter">Turnout</p>
                </div>
                <div class="w-10 h-10 rounded-full flex items-center justify-center text-stone-300 dark:text-stone-700 hover:text-stone-900 dark:hover:text-white hover:bg-stone-50 dark:hover:bg-stone-800 transition-all cursor-pointer">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5"/></svg>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Activity Log -->
    <div class="space-y-6">
      <div class="flex items-center justify-between px-2">
        <h2 class="text-lg font-bold text-stone-900 dark:text-white">Recent Activity</h2>
        <button onclick={() => goto('/admin/audit')} class="text-xs font-bold text-stone-400 hover:text-stone-900 dark:hover:text-white transition-colors">View All</button>
      </div>
      {#if isLoading}
        <div class="space-y-3">
          {#each Array(5) as _}
            <div class="h-12 bg-stone-50 dark:bg-stone-800/50 rounded-xl animate-pulse"></div>
          {/each}
        </div>
      {:else if recentLogs.length === 0}
        <div class="py-12 text-center text-stone-400 dark:text-stone-500 text-xs italic border-2 border-dashed border-stone-100 dark:border-stone-800 rounded-2xl">No activity logged yet.</div>
      {:else}
        <div class="space-y-3">
          {#each recentLogs as log}
            <div class="flex items-center gap-4 p-3 rounded-xl hover:bg-stone-50 dark:hover:bg-stone-800/50 transition-all group">
              <span class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-[10px] font-black uppercase
                {log.actor_role === 'admin' ? 'bg-amber-100 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400' : 'bg-violet-100 text-violet-600 dark:bg-violet-500/10 dark:text-violet-400'}">
                {log.actor_role?.[0]}
              </span>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-stone-700 dark:text-stone-200 group-hover:text-stone-900 dark:group-hover:text-white transition-colors truncate">{log.action}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-[10px] text-stone-400 dark:text-stone-500 font-medium">{new Date(log.created_at).toLocaleDateString()}</span>
                  <span class="w-1 h-1 rounded-full bg-stone-200 dark:bg-stone-700"></span>
                  <span class="text-[10px] text-stone-400 dark:text-stone-500 font-medium">{new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Quick Links -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    {#each [
      { label: 'Manage Elections', path: '/admin/elections', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
      { label: 'Manage Voters', path: '/admin/voters', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
      { label: 'Manage Advisers', path: '/admin/advisers', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
      { label: 'View Audit Logs', path: '/admin/audit', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
    ] as link}
      <button onclick={() => goto(link.path)} class="card-themed p-4 flex items-center gap-3 hover:bg-stone-50 dark:hover:bg-stone-800/50 transition-all text-left group outline-none">
        <div class="w-8 h-8 bg-stone-100 dark:bg-stone-800 rounded-lg flex items-center justify-center text-stone-500 dark:text-stone-400 group-hover:scale-110 transition-transform">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={link.icon}/></svg>
        </div>
        <span class="text-[11px] font-bold text-stone-600 dark:text-stone-300 group-hover:text-stone-900 dark:group-hover:text-white transition-colors">{link.label}</span>
      </button>
    {/each}
  </div>

</div>
