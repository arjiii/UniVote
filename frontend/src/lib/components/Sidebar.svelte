<script>
  import { goto } from '$app/navigation';
  import { authSession } from '$lib/stores/auth.js';
  import { voterSession } from '$lib/stores/session.js';
  import { page } from '$app/state';
  import { toggleTheme } from '$lib/stores/theme.js';
  import { fade } from 'svelte/transition';

  /** @type {{ role: 'admin' | 'adviser' | 'student', student_info?: any, children: import('svelte').Snippet }} */
  let { role, student_info, children } = $props();

  let collapsed = $state(false);

  const links = {
    admin: [
      { name: 'Dashboard', path: '/admin', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { name: 'Elections', path: '/admin/elections', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
      { name: 'Voters', path: '/admin/voters', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
      { name: 'Advisers', path: '/admin/advisers', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
      { name: 'Audit Logs', path: '/admin/audit', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
    ],
    adviser: [
      { name: 'Dashboard', path: '/adviser', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { name: 'Candidates', path: '/adviser/candidates', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
      { name: 'Partylists', path: '/adviser/partylists', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
      { name: 'Results', path: '/adviser/results', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
      { name: 'Audit Logs', path: '/adviser/audit', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
    ],
    student: [
      { name: 'Dashboard', path: '/student', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { name: 'Cast Vote', path: '/student/ballot', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
      { name: 'Results', path: '/student/results', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' }
    ]
  };

  function handleLogout() {
    if (role === 'student') {
      voterSession.logout();
    } else {
      authSession.logout();
    }
    goto('/login');
  }

  const navLinks = $derived(links[/** @type {keyof typeof links} */ (role)] || []);
</script>

<!-- Sidebar -->
<aside class="hidden md:flex fixed left-0 top-0 h-screen flex-col z-50 transition-all duration-500 ease-in-out flex-shrink-0 {collapsed ? 'w-[72px]' : 'w-64'} glass-themed shadow-2xl shadow-black/5 dark:shadow-black/20" 
  style="border-right-width: 1px;">

  <!-- Brand -->
  <div class="flex items-center h-16 border-b px-6 transition-all" style="border-color: var(--border-main);">
    <div class="flex items-center gap-3">
      <button 
        onclick={toggleTheme}
        class="w-8 h-8 bg-stone-900 dark:bg-stone-100 rounded-lg flex items-center justify-center text-white dark:text-stone-900 text-xs font-black shrink-0 shadow-lg hover:shadow-brand-500/20 hover:scale-110 hover:rotate-3 active:scale-95 transition-all duration-300 outline-none"
        title="Toggle Dark Mode"
      >
        U
      </button>
      {#if !collapsed}
        <div class="min-w-0" in:fade={{ duration: 200 }}>
          <p class="font-bold text-sm tracking-tight leading-none dark:text-white transition-colors duration-300">UniVote</p>
          <p class="text-[9px] font-bold mt-1.5 capitalize tracking-[0.15em] transition-colors opacity-50" style="color: var(--text-muted); font-family: system-ui;">{role} Portal</p>
        </div>
      {/if}
    </div>
  </div>

  <!-- Collapse Toggle -->
  <button
    onclick={() => collapsed = !collapsed}
    class="absolute -right-3 top-[54px] w-6 h-6 rounded-full border shadow-md flex items-center justify-center transition-all duration-300 z-50 hover:scale-125 active:scale-90 bg-white dark:bg-stone-800 border-stone-200 dark:border-stone-700 text-stone-500 hover:text-stone-900 dark:hover:text-white"
    title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
  >
    <svg class="w-2.5 h-2.5 transition-transform duration-500 {collapsed ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7"/>
    </svg>
  </button>

  <!-- Nav -->
  <nav class="flex-1 {collapsed ? 'px-2' : 'px-3'} pt-8 space-y-1.5 overflow-y-auto scrollbar-hide">
    {#if !collapsed}
      <p class="text-[10px] font-bold text-stone-400 dark:text-stone-500 tracking-[0.25em] px-4 pb-4 uppercase">Navigation</p>
    {/if}
    {#each navLinks as link}
      {@const linkPath = link.path.split('?')[0]}
      {@const isActive = page.url.pathname === linkPath}
      <button
        onclick={() => goto(link.path)}
        class="w-full flex items-center {collapsed ? 'justify-center px-0 py-3.5' : 'gap-3.5 px-4 py-3'} rounded-2xl transition-all duration-300 text-left group relative border
          {isActive ? 'shadow-md shadow-black/5 dark:shadow-black/20' : ''}"
        title={collapsed ? link.name : ''}
        style={isActive ? 'background-color: var(--bg-card); color: var(--text-main); border-color: var(--border-main);' : 'background-color: transparent; color: var(--text-muted); border-color: transparent;'}
      >
        {#if isActive}
          <div class="absolute left-0 w-1 h-4 rounded-r-full shadow-md" style="background-color: var(--brand-primary); box-shadow: 0 0 10px var(--brand-glow);" in:fade></div>
        {/if}
        <svg class="w-4.5 h-4.5 shrink-0 transition-all duration-300 group-hover:scale-110 {isActive ? 'opacity-100' : 'opacity-60 group-hover:opacity-100'}" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style={isActive ? 'color: var(--brand-primary);' : ''}>
          <path stroke-linecap="round" stroke-linejoin="round" d={link.icon} />
        </svg>
        {#if !collapsed}
          <span class="text-[13px] font-bold tracking-tight">{link.name}</span>
        {/if}
      </button>
    {/each}
  </nav>

  <!-- User Section -->
  <div class="border-t {collapsed ? 'p-3' : 'p-4'} space-y-3" style="border-color: var(--border-main);">
    {#if !collapsed}
      <div class="flex items-center gap-3 px-3 py-3 rounded-2xl border transition-all" style="background-color: var(--bg-card); border-color: var(--border-subtle);">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-black flex-shrink-0 shadow-inner border" style="background-color: var(--bg-elevated); color: var(--text-main); border-color: var(--border-main);">
          {(student_info?.full_name || '?').split(' ').slice(0, 2).map((/** @type {string} */ w) => w[0]?.toUpperCase()).join('')}
        </div>
        <div class="min-w-0">
          <p class="text-[13px] font-bold truncate leading-tight transition-colors" style="color: var(--text-main);">{student_info?.full_name || 'Loading...'}</p>
          <p class="text-[10px] font-bold capitalize mt-1 tracking-wider" style="color: var(--brand-support);">{role}</p>
        </div>
      </div>
    {:else}
      <div class="flex justify-center">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-black transition-all border shadow-inner" title={student_info?.full_name || 'User'} style="background-color: var(--bg-elevated); color: var(--text-main); border-color: var(--border-main);">
          {(student_info?.full_name || '?')[0].toUpperCase()}
        </div>
      </div>
    {/if}
    <button
      onclick={handleLogout}
      class="w-full flex items-center {collapsed ? 'justify-center px-0' : 'gap-3 px-4'} py-3 rounded-2xl text-stone-500 dark:text-stone-400 dark:hover:bg-red-950/20 hover:text-red-600 dark:hover:text-red-400 transition-all text-xs font-bold group"
      title={collapsed ? 'Sign Out' : ''}
    >
      <svg class="w-4.5 h-4.5 shrink-0 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"/>
      </svg>
      {#if !collapsed}
        <span class="tracking-tight">Sign Out</span>
      {/if}
    </button>
  </div>
</aside>

<!-- Mobile topbar -->
<div class="md:hidden flex items-center justify-between px-6 h-18 border-b sticky top-0 z-50 transition-all glass-themed shadow-lg"
  style="border-bottom-width: 1px;">
  <div class="flex items-center gap-4">
    <button 
      onclick={toggleTheme}
      class="w-9 h-9 bg-stone-900 dark:bg-stone-100 rounded-xl flex items-center justify-center text-white dark:text-stone-900 text-xs font-black shadow-xl active:scale-90 transition-all duration-300 outline-none"
      title="Toggle Dark Mode"
    >
      U
    </button>
    <span class="font-black text-base tracking-tight dark:text-white transition-colors">UniVote</span>
  </div>
  <div class="flex items-center gap-3">
    <div class="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-black transition-all border shadow-inner" style="background-color: var(--bg-elevated); color: var(--text-main); border-color: var(--border-subtle);">
      {(student_info?.full_name || '?')[0].toUpperCase()}
    </div>
  </div>
</div>

<main class="h-screen overflow-y-auto transition-all duration-500 ease-out {collapsed ? 'md:pl-[68px]' : 'md:pl-60'} scrollbar-hide" style="background-color: var(--bg-main);">
  {@render children()}
</main>

<style>
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
</style>
