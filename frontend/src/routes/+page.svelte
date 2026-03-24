<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authSession } from '$lib/stores/auth.js';
  import { voterSession } from '$lib/stores/session.js';
  import { toggleTheme } from '$lib/stores/theme.js';

  onMount(() => {
    if ($authSession) goto($authSession.role === 'admin' ? '/admin' : '/adviser');
    else if ($voterSession) goto('/student/ballot');
  });
</script>

<svelte:head>
  <title>UniVote — School Election System</title>
</svelte:head>

<div class="landing">

  <!-- Topbar -->
  <nav class="topbar">
    <div class="topbar-inner">
      <div class="topbar-brand">
        <button onclick={toggleTheme} class="logo-mark" title="Toggle theme">U</button>
        <span class="logo-text">UniVote</span>
        <span class="logo-divider">|</span>
        <span class="logo-sub">School Election System</span>
      </div>
      <div class="topbar-right">
        <span class="status-dot"></span>
        <span class="status-label">System Online</span>
      </div>
    </div>
  </nav>

  <!-- Hero -->
  <main class="hero">
    <div class="hero-inner">
      <h1 class="hero-title">
        School Elections,<br/>
        <span class="hero-title-accent">Done Right.</span>
      </h1>
      <p class="hero-desc">
        Transparent · Secure · Verifiable. Cast and manage student council votes
        through a trusted, real-time digital system.
      </p>

      <!-- Entry cards -->
      <div class="entry-grid">

        <!-- Student -->
        <a href="/student/validate" class="entry-card" id="entry-student">
          <div class="entry-icon-wrap entry-icon-primary">
            <svg class="entry-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
            </svg>
          </div>
          <div class="entry-body">
            <p class="entry-tag">Student Access</p>
            <h2 class="entry-title">Cast Your Vote</h2>
            <p class="entry-desc">Authenticate with your student ID to vote in active school elections.</p>
          </div>
          <div class="entry-features">
            <div class="entry-feature">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              One vote per election, guaranteed
            </div>
            <div class="entry-feature">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              View your ballot receipt
            </div>
          </div>
          <div class="entry-action btn-primary" style="margin-top:auto;">
            Enter Student Portal
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/></svg>
          </div>
        </a>

        <!-- Staff -->
        <a href="/login" class="entry-card" id="entry-staff">
          <div class="entry-icon-wrap entry-icon-neutral">
            <svg class="entry-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25"/>
            </svg>
          </div>
          <div class="entry-body">
            <p class="entry-tag">Staff Access</p>
            <h2 class="entry-title">Administration</h2>
            <p class="entry-desc">Manage elections, candidates, voters, and view real-time results.</p>
          </div>
          <div class="entry-features">
            <div class="entry-feature">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              Full audit log access
            </div>
            <div class="entry-feature">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              Live turnout monitoring
            </div>
          </div>
          <div class="entry-action btn-secondary" style="margin-top:auto;">
            Staff Login
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/></svg>
          </div>
        </a>
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer class="landing-footer">
    <span>© 2025 UniVote</span>
    <span class="footer-sep">·</span>
    <span>Secure · Transparent · Official</span>
  </footer>

</div>

<style>
  :global(body) { background-color: var(--bg-main); }

  .landing {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background-color: var(--bg-main);
  }

  /* Topbar */
  .topbar {
    position: sticky; top: 0; z-index: 50;
    background-color: var(--bg-card);
    border-bottom: 1px solid var(--border-main);
  }
  .topbar-inner {
    max-width: 900px; margin: 0 auto;
    padding: 0 1.5rem;
    height: 52px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .topbar-brand { display: flex; align-items: center; gap: 0.625rem; }
  .logo-mark {
    width: 28px; height: 28px;
    background-color: var(--brand-primary);
    color: #fff; border-radius: 6px;
    font-size: 0.75rem; font-weight: 800;
    border: none; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background-color 0.15s;
  }
  .logo-mark:hover { background-color: var(--brand-primary-h); }
  .logo-text  { font-size: 0.9375rem; font-weight: 700; color: var(--text-main); }
  .logo-divider { color: var(--border-strong); margin: 0 0.25rem; }
  .logo-sub   { font-size: 0.75rem; color: var(--text-subtle); font-weight: 500; }
  .topbar-right { display: flex; align-items: center; gap: 0.4rem; }
  .status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background-color: var(--status-success-fg);
  }
  .status-label { font-size: 0.75rem; color: var(--text-subtle); font-weight: 500; }

  /* Hero */
  .hero { flex: 1; display: flex; align-items: center; justify-content: center; padding: 3rem 1.5rem; }
  .hero-inner { width: 100%; max-width: 720px; text-align: center; }

  .hero-title {
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 800;
    color: var(--text-main);
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 1rem;
  }
  .hero-title-accent { color: var(--brand-primary); }
  .hero-desc {
    font-size: 0.9375rem;
    color: var(--text-muted);
    line-height: 1.65;
    max-width: 480px;
    margin: 0 auto 2.5rem;
  }

  /* Entry cards */
  .entry-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    text-align: left;
  }
  @media (max-width: 600px) { .entry-grid { grid-template-columns: 1fr; } }

  .entry-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-main);
    border-radius: 8px;
    padding: 1.5rem;
    display: flex; flex-direction: column; gap: 1rem;
    text-decoration: none; color: inherit;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .entry-card:hover {
    border-color: var(--brand-primary);
    box-shadow: 0 0 0 3px var(--brand-glow);
  }

  .entry-icon-wrap {
    width: 40px; height: 40px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
  }
  .entry-icon-primary { background-color: rgba(37,99,235,0.1); color: var(--brand-primary); }
  .entry-icon-neutral { background-color: var(--bg-elevated); color: var(--text-muted); }
  .entry-icon { width: 20px; height: 20px; }

  .entry-tag  { font-size: 0.6875rem; font-weight: 600; color: var(--text-subtle); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.25rem; }
  .entry-title { font-size: 1.0625rem; font-weight: 700; color: var(--text-main); }
  .entry-desc { font-size: 0.8125rem; color: var(--text-muted); line-height: 1.55; margin-top: 0.25rem; }

  .entry-features { display: flex; flex-direction: column; gap: 0.375rem; }
  .entry-feature {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.75rem; color: var(--text-muted); font-weight: 500;
  }

  .entry-action {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1rem;
    font-size: 0.8125rem; font-weight: 600;
    border-radius: 6px; text-decoration: none;
    justify-content: center;
    cursor: pointer;
    border: none;
  }

  /* Footer */
  .landing-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-main);
    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    font-size: 0.75rem; color: var(--text-subtle); font-weight: 500;
  }
  .footer-sep { color: var(--border-strong); }
</style>
