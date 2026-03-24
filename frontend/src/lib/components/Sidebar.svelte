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
  let mobileMenuOpen = $state(false);

  const links = {
    admin: [
      { name: 'Dashboard',  path: '/admin',           icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { name: 'Elections',  path: '/admin/elections',  icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
      { name: 'Voters',     path: '/admin/voters',     icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
      { name: 'Advisers',   path: '/admin/advisers',   icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
      { name: 'Audit Logs', path: '/admin/audit',      icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
    ],
    adviser: [
      { name: 'Dashboard',  path: '/adviser',              icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { name: 'Candidates', path: '/adviser/candidates',   icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
      { name: 'Partylists', path: '/adviser/partylists',   icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
      { name: 'Results',    path: '/adviser/results',      icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
      { name: 'Audit Logs', path: '/adviser/audit',        icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' }
    ],
    student: [
      { name: 'Dashboard', path: '/student',         icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
      { name: 'Cast Vote', path: '/student/ballot',  icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
      { name: 'Results',   path: '/student/results', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' }
    ]
  };

  function handleLogout() {
    if (role === 'student') voterSession.logout();
    else authSession.logout();
    mobileMenuOpen = false;
    goto('/login');
  }

  function handleNav(/** @type {string} */ path) {
    mobileMenuOpen = false;
    goto(path);
  }

  const navLinks = $derived(links[/** @type {keyof typeof links} */ (role)] || []);
  const initials = $derived((student_info?.full_name || '?').split(' ').slice(0,2).map((/** @type {string} */w) => w[0]?.toUpperCase()).join(''));
  const sidebarWidth = $derived(collapsed ? '56px' : '220px');
</script>

<!-- Mobile overlay -->
{#if mobileMenuOpen}
  <div
    onclick={() => mobileMenuOpen = false}
    onkeydown={(e) => e.key === 'Escape' && (mobileMenuOpen = false)}
    role="button" tabindex="0" aria-label="Close menu"
    class="md:hidden fixed inset-0 bg-black/40 z-[60]"
    in:fade={{ duration: 200 }} out:fade={{ duration: 200 }}
  ></div>
{/if}

<!-- Sidebar -->
<aside class="sidebar {collapsed ? 'collapsed' : 'expanded'} {mobileMenuOpen ? 'mobile-open' : ''}">

  <!-- User Profile (Top) -->
  <div class="sidebar-brand" style="padding: 1.25rem 0.875rem; height: auto;">
    <button onclick={toggleTheme} class="user-avatar avatar-initial" style="width: 32px; height: 32px; font-size: 0.75rem; flex-shrink: 0; cursor: pointer; transition: transform 0.2s;" title="Toggle Dark Mode" aria-label="Toggle Dark Mode">
      {initials}
    </button>
    {#if !collapsed || mobileMenuOpen}
      <div class="user-details" in:fade={{ duration: 150 }} style="margin-left: 0.5rem; flex: 1; min-width: 0;">
        <p class="user-name" style="font-size: 0.875rem; font-weight: 600; color: var(--text-main); white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{student_info?.full_name || 'Loading…'}</p>
        <p class="user-role" style="font-size: 0.625rem; font-weight: 600; color: var(--text-subtle); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.125rem;">{role}</p>
      </div>
    {/if}
  </div>

  <!-- Collapse toggle (desktop only) -->
  <button
    onclick={() => collapsed = !collapsed}
    class="collapse-btn"
    title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
  >
    <svg class="w-3 h-3 {collapsed ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
    </svg>
  </button>

  <!-- Nav -->
  <nav class="sidebar-nav">
    {#each navLinks as link}
      {@const isActive = page.url.pathname === link.path.split('?')[0]}
      <button
        onclick={() => handleNav(link.path)}
        class="nav-item {isActive ? 'active' : ''} {collapsed && !mobileMenuOpen ? 'icon-only' : ''}"
        title={collapsed && !mobileMenuOpen ? link.name : ''}
      >
        {#if isActive}
          <div class="nav-indicator"></div>
        {/if}
        <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d={link.icon}/>
        </svg>
        {#if !collapsed || mobileMenuOpen}
          <span class="nav-label">{link.name}</span>
        {/if}
      </button>
    {/each}
  </nav>

  <!-- User section -->
  <div class="sidebar-footer">
    <button
      onclick={handleLogout}
      class="logout-btn {collapsed && !mobileMenuOpen ? 'icon-only' : ''}"
      title={collapsed && !mobileMenuOpen ? 'Sign Out' : ''}
    >
      <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"/>
      </svg>
      {#if !collapsed || mobileMenuOpen}
        <span>Sign Out</span>
      {/if}
    </button>
  </div>
</aside>

<!-- Mobile topbar -->
<div class="mobile-topbar">
  <div style="display:flex;align-items:center;gap:0.75rem;">
    <button onclick={() => mobileMenuOpen = !mobileMenuOpen} class="topbar-btn" aria-label="Toggle menu">
      {#if mobileMenuOpen}
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
      {:else}
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"/></svg>
      {/if}
    </button>
  </div>
  
  <div style="display:flex;align-items:center;gap:0.5rem;">
    <div style="text-align: right; display: flex; flex-direction: column; justify-content: center;">
      <span style="font-size: 0.8125rem; font-weight: 600; color: var(--text-main); line-height: 1.2;">{student_info?.full_name || 'Loading…'}</span>
      <span style="font-size: 0.625rem; font-weight: 600; color: var(--text-subtle); text-transform: uppercase; letter-spacing: 0.08em; line-height: 1.2;">{role}</span>
    </div>
    <button onclick={toggleTheme} class="user-avatar avatar-initial" style="width:32px;height:32px;font-size:0.75rem;cursor:pointer;" title="Toggle Dark Mode" aria-label="Toggle Dark Mode">
      {initials}
    </button>
  </div>
</div>

<!-- Main content -->
<main class="main-content {collapsed ? 'sidebar-collapsed' : 'sidebar-expanded'}">
  {@render children()}
</main>

<style>
  /* ─── Sidebar ─── */
  aside.sidebar {
    position: fixed;
    left: 0; top: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    z-index: 70;
    background-color: var(--bg-card);
    border-right: 1px solid var(--border-main);
    transition: width 0.25s ease;
    overflow: hidden;
  }
  aside.sidebar.expanded  { width: 220px; }
  aside.sidebar.collapsed { width: 56px; }
  @media (max-width: 767px) {
    aside.sidebar { transform: translateX(-100%); width: 220px !important; transition: transform 0.25s ease; }
    aside.sidebar.mobile-open { transform: translateX(0); }
  }

  /* Brand */
  .sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    height: 52px;
    padding: 0 0.875rem;
    border-bottom: 1px solid var(--border-main);
    flex-shrink: 0;
  }

  /* Collapse button */
  .collapse-btn {
    position: absolute;
    right: -10px; top: 60px;
    width: 20px; height: 20px;
    background-color: var(--bg-card);
    border: 1px solid var(--border-main);
    border-radius: 50%;
    display: none;
    align-items: center; justify-content: center;
    cursor: pointer;
    z-index: 80;
    transition: background-color 0.15s;
    color: var(--text-subtle);
    padding: 0;
  }
  @media (min-width: 768px) { .collapse-btn { display: flex; } }
  .collapse-btn:hover { background-color: var(--bg-elevated); color: var(--text-main); }
  .collapse-btn svg { transition: transform 0.25s; }

  /* Nav */
  .sidebar-nav {
    flex: 1;
    padding: 0.5rem 0.375rem;
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
    overflow-y: auto;
  }
  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    padding: 0.5rem 0.75rem;
    border: none;
    background: transparent;
    color: var(--text-muted);
    border-radius: 6px;
    cursor: pointer;
    text-align: left;
    position: relative;
    transition: background-color 0.12s, color 0.12s;
    width: 100%;
  }
  .nav-item:hover { background-color: var(--bg-elevated); color: var(--text-main); }
  .nav-item.active {
    background-color: rgba(37,99,235,0.08);
    color: var(--brand-primary);
    font-weight: 600;
  }
  :global(.dark) .nav-item.active { background-color: rgba(59,130,246,0.12); }
  .nav-item.icon-only { justify-content: center; padding: 0.625rem 0; }
  .nav-indicator {
    position: absolute;
    left: 0; top: 50%;
    transform: translateY(-50%);
    width: 3px; height: 18px;
    background-color: var(--brand-primary);
    border-radius: 0 2px 2px 0;
  }
  .nav-icon { width: 1rem; height: 1rem; flex-shrink: 0; }
  .nav-label { font-size: 0.8125rem; font-weight: 500; white-space: nowrap; }

  /* Footer */
  .sidebar-footer {
    border-top: 1px solid var(--border-main);
    padding: 0.625rem 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    flex-shrink: 0;
  }
  .user-avatar { border-radius: 6px; }
  .user-details { min-width: 0; }
  .user-name {
    font-size: 0.8125rem; font-weight: 600;
    color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .user-role {
    font-size: 0.625rem; font-weight: 600;
    color: var(--text-subtle); text-transform: uppercase; letter-spacing: 0.08em;
  }
  .logout-btn {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.4rem 0.75rem;
    border: none; background: transparent;
    color: var(--text-subtle); font-size: 0.8125rem; font-weight: 500;
    cursor: pointer; border-radius: 6px; width: 100%;
    transition: background-color 0.12s, color 0.12s;
  }
  .logout-btn:hover { background-color: var(--status-danger-bg); color: var(--status-danger-fg); }
  .logout-btn.icon-only { justify-content: center; padding: 0.5rem 0; }

  /* Mobile topbar */
  .mobile-topbar {
    display: none;
    align-items: center;
    justify-content: space-between;
    height: 52px;
    padding: 0 1rem;
    background-color: var(--bg-card);
    border-bottom: 1px solid var(--border-main);
    position: sticky; top: 0; z-index: 50;
  }
  @media (max-width: 767px) { .mobile-topbar { display: flex; } }
  .topbar-btn {
    width: 32px; height: 32px;
    background: transparent;
    border: 1px solid var(--border-main);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    color: var(--text-main); cursor: pointer;
  }

  /* Main */
  .main-content {
    min-height: 100vh;
    background-color: var(--bg-main);
    transition: padding-left 0.25s ease;
  }
  @media (min-width: 768px) {
    .main-content.sidebar-expanded  { padding-left: 220px; }
    .main-content.sidebar-collapsed { padding-left: 56px; }
  }
</style>
