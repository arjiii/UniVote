<script>
  import { goto } from '$app/navigation';
  import { authSession } from '$lib/stores/auth.js';
  import { voterSession } from '$lib/stores/session.js';
  import { page } from '$app/state';

  /** @type {{ role: 'admin' | 'adviser' | 'student', student_info?: any, children: import('svelte').Snippet }} */
  let { role, student_info, children } = $props();

  let collapsed = $state(false);

  const links = {
    admin: [
      { name: 'Dashboard', path: '/admin', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
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

  const navLinks = $derived(links[role] || []);
</script>

<!-- Sidebar (white, clean) -->
<aside class="hidden md:flex fixed left-0 top-0 h-screen flex-col bg-white border-r border-stone-200 z-50 transition-all duration-300 ease-out flex-shrink-0 {collapsed ? 'w-[68px]' : 'w-60'}">

  <!-- Brand -->
  <div class="flex items-center {collapsed ? 'justify-center px-3' : 'gap-2.5 px-5'} h-14 border-b border-stone-200">
    <div class="w-7 h-7 bg-stone-900 rounded-md flex items-center justify-center text-white text-xs font-bold shrink-0">U</div>
    {#if !collapsed}
      <div>
        <p class="font-semibold text-xs tracking-tight leading-none">UniVote</p>
        <p class="text-[10px] text-stone-400 mt-0.5 capitalize">{role} Portal</p>
      </div>
    {/if}
  </div>

  <!-- Collapse Toggle -->
  <button
    onclick={() => collapsed = !collapsed}
    class="absolute -right-3 top-[46px] w-6 h-6 bg-white rounded-full border border-stone-200 shadow-sm flex items-center justify-center text-stone-400 hover:text-stone-900 hover:border-stone-400 hover:shadow-md transition-all duration-200 z-50"
    title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
  >
    <svg class="w-3 h-3 transition-transform duration-300 {collapsed ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
    </svg>
  </button>

  <!-- Nav -->
  <nav class="flex-1 {collapsed ? 'px-2' : 'px-3'} pt-4 space-y-0.5">
    {#if !collapsed}
      <p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase px-3 pb-2">Navigation</p>
    {/if}
    {#each navLinks as link}
      {@const isActive = page.url.pathname === link.path}
      <button
        onclick={() => goto(link.path)}
        class="w-full flex items-center {collapsed ? 'justify-center px-0 py-2.5' : 'gap-3 px-3 py-2.5'} rounded-lg transition-all duration-150 text-left
          {isActive ? 'bg-stone-100 text-stone-900' : 'text-stone-500 hover:bg-stone-50 hover:text-stone-800'}"
        title={collapsed ? link.name : ''}
      >
        <svg class="w-4 h-4 shrink-0 {isActive ? 'text-stone-900' : ''}" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d={link.icon} />
        </svg>
        {#if !collapsed}
          <span class="text-sm font-medium">{link.name}</span>
        {/if}
      </button>
    {/each}
  </nav>

  <!-- User -->
  <div class="border-t border-stone-200 {collapsed ? 'p-2' : 'p-3'}">
    {#if !collapsed}
      <div class="flex items-center gap-3 px-2 py-2 rounded-lg mb-1">
        <div class="w-8 h-8 bg-stone-200 rounded-full flex items-center justify-center text-stone-700 text-xs font-semibold flex-shrink-0">
          {(student_info?.full_name || '?').split(' ').slice(0, 2).map(w => w[0]?.toUpperCase()).join('')}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-medium text-stone-900 truncate">{student_info?.full_name || 'Loading...'}</p>
          <p class="text-xs text-stone-400 capitalize">{role}</p>
        </div>
      </div>
    {:else}
      <div class="flex justify-center mb-1">
        <div class="w-8 h-8 bg-stone-200 rounded-full flex items-center justify-center text-stone-700 text-xs font-semibold" title={student_info?.full_name || 'User'}>
          {(student_info?.full_name || '?')[0].toUpperCase()}
        </div>
      </div>
    {/if}
    <button
      onclick={handleLogout}
      class="w-full flex items-center {collapsed ? 'justify-center px-0' : 'gap-2 px-3'} py-2 rounded-lg text-stone-500 hover:bg-stone-100 hover:text-stone-700 transition-colors text-xs"
      title={collapsed ? 'Sign Out' : ''}
    >
      <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"/>
      </svg>
      {#if !collapsed}
        <span>Sign Out</span>
      {/if}
    </button>
  </div>
</aside>

<!-- Mobile topbar -->
<div class="md:hidden flex items-center justify-between px-5 h-14 bg-white border-b border-stone-200 sticky top-0 z-10">
  <div class="flex items-center gap-2">
    <div class="w-6 h-6 bg-stone-900 rounded-md flex items-center justify-center text-white text-[10px] font-bold">U</div>
    <span class="font-semibold text-sm">UniVote</span>
  </div>
  <div class="flex items-center gap-2">
    <div class="w-7 h-7 bg-stone-200 rounded-full flex items-center justify-center text-stone-700 text-xs font-semibold">
      {(student_info?.full_name || '?')[0].toUpperCase()}
    </div>
  </div>
</div>

<main class="h-screen overflow-y-auto bg-[#f9f8f6] transition-all duration-300 ease-out {collapsed ? 'md:pl-[68px]' : 'md:pl-60'} scrollbar-hide">
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
