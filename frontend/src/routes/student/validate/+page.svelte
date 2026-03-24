<script>
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import { theme, toggleTheme } from '$lib/stores/theme.js';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import { fade, fly } from 'svelte/transition';
  
  let studentId = $state('');
  let isChecking = $state(false);
  let errorMessage = $state('');
  let retrySeconds = $state(0);

  async function checkStudentId(/** @type {SubmitEvent} */ e) {
    e.preventDefault();
    if (!studentId) {
      errorMessage = 'Please enter your Student ID.';
      return;
    }

    isChecking = true;
    errorMessage = '';

    try {
      const data = await studentApi.validate(studentId);
      const elections = (data.active_elections || []).map(/** @param {any} e */ e => ({
        id: e.id,
        name: e.name,
        has_voted: e.has_voted
      }));
      voterSession.login({
        ...data.student,
        access_token: data.access_token,
        elections
      });
      goto('/student');
    } catch (/** @type {any} */ err) {
      if (err.retryAfter) {
        retrySeconds = err.retryAfter;
        errorMessage = `Too many attempts. Please wait ${retrySeconds}s.`;
      } else {
        errorMessage = err.message ?? 'Error validating student ID.';
      }
    } finally {
      isChecking = false;
    }
  }

  import { onMount, onDestroy } from 'svelte';
  let timer;
  $effect(() => {
    if (retrySeconds > 0) {
      timer = setInterval(() => {
        retrySeconds -= 1;
      }, 1000);
      return () => clearInterval(timer);
    }
  });
</script>

<svelte:head>
  <title>Student Access | UniVote</title>
</svelte:head>

<div class="min-h-screen flex bg-surface-main transition-colors duration-500" class:dark={$theme === 'dark'}>

  <!-- Left panel: brand + trust signals -->
  <div class="hidden lg:flex w-[44%] flex-col justify-between bg-surface-elevated border-r border-line-main p-12 relative overflow-hidden flex-shrink-0">
    <!-- Decorative circles -->
    <div class="absolute -bottom-32 -right-32 w-80 h-80 rounded-full border-[40px] border-line-subtle opacity-50 pointer-events-none"></div>
    <div class="absolute -bottom-16 -right-16 w-48 h-48 rounded-full border-[20px] border-line-strong opacity-30 pointer-events-none"></div>

    <div class="relative flex items-center gap-4">
      <button 
        onclick={toggleTheme}
        class="w-10 h-10 bg-content-main text-surface-main rounded-2xl flex items-center justify-center text-sm font-black shadow-2xl hover:scale-110 active:scale-95 transition-all outline-none"
      >
        U
      </button>
      <span class="font-black text-lg tracking-tighter text-content-main uppercase mt-0.5">UniVote</span>
    </div>

    <div class="relative max-w-sm">
      <div class="inline-flex items-center gap-3 bg-[var(--status-success-bg)] border border-[var(--status-success-fg)] rounded-2xl px-4 py-2 mb-10 shadow-inner">
        <span class="w-1.5 h-1.5 bg-[var(--status-success-fg)] rounded-full block animate-pulse"></span>
        <span class="text-[10px] text-[var(--status-success-fg)] font-black uppercase tracking-[0.2em]">Flux Node Active</span>
      </div>
      <h2 class="text-5xl text-content-main leading-[1.05] mb-8 font-black tracking-tighter uppercase">
        Ready to cast<br/><span class="text-content-muted">your vote?</span>
      </h2>
      <p class="text-content-subtle text-sm leading-relaxed font-bold uppercase tracking-widest opacity-80 mb-12">
        Verify your identity via the student ledger to access the secure ballot and make your voice count.
      </p>

      <div class="space-y-6">
        {#each ['Anonymity Guaranteed', 'Single Instance Vote', 'Real-time Flux Updates'] as point}
          <div class="flex items-center gap-4 group">
            <div class="w-8 h-8 bg-[var(--status-success-bg)] border border-[var(--status-success-bg)] rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-[var(--status-success-fg)]" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            </div>
            <span class="text-[10px] font-black uppercase tracking-[0.2em] text-content-subtle transition-colors">{point}</span>
          </div>
        {/each}
      </div>
    </div>

    <p class="relative text-content-subtle text-[9px] font-black uppercase tracking-[0.3em]">© 2025 UniVote · System Integrity Nominal</p>
  </div>

  <!-- Right form -->
  <div class="flex-1 flex items-center justify-center p-6 md:p-12" in:fade={{ duration: 400 }}>
    <div class="w-full max-w-sm">
      <GlassCard
        title="Student Identity"
        subtitle="Gateway to the Voting Booth"
        hideMobileDashboardOnly={false}
      >
        <form onsubmit={checkStudentId} class="space-y-6 mt-4">
          <div class="space-y-2">
            <label for="studentId" class="field-label ml-1">Official Student ID</label>
            <div class="relative">
              <input 
                id="studentId"
                type="text" 
                bind:value={studentId}
                placeholder="e.g. 2021-00123"
                class="input-base w-full uppercase"
                required
              />
            </div>
            <p class="text-[9px] text-content-subtle font-black uppercase tracking-tight mt-2 ml-1">Registry identification number.</p>
          </div>

          {#if errorMessage}
            <div class="pill pill-danger" style="width: 100%; justify-content: space-between;">
              <div class="flex items-center gap-3">
                <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
                {errorMessage}
              </div>
              {#if retrySeconds > 0}
                <span class="flex-shrink-0 font-mono text-[10px] font-black bg-[var(--status-danger-fg)] text-white px-2 py-0.5 rounded shadow-sm opacity-80">
                  {retrySeconds}S
                </span>
              {/if}
            </div>
          {/if}

          <button 
            type="submit" 
            disabled={isChecking || !studentId || retrySeconds > 0}
            class="btn-primary w-full py-5 text-[11px]"
          >
            {#if isChecking}
              <span class="flex items-center justify-center gap-3">
                <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                Validating ID...
              </span>
            {:else}
              Enter Voting Booth
            {/if}
          </button>
        </form>

        <div class="mt-10 pt-8 border-t border-line-main text-center">
          <a href="/" class="inline-flex items-center gap-2 text-[10px] font-black text-content-subtle hover:text-content-main uppercase tracking-[0.2em] transition-all">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Command Center
          </a>
        </div>
      </GlassCard>
    </div>
  </div>
</div>
