<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth as authApi } from '$lib/api.js';
  import { authSession } from '$lib/stores/auth.js';
  import { theme, toggleTheme } from '$lib/stores/theme.js';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import { fade, fly } from 'svelte/transition';

  onMount(() => {
    if ($authSession) {
      goto($authSession.role === 'admin' ? '/admin' : '/adviser');
    }
  });

  let fullName = $state('');
  let id = $state('');
  let password = $state('');
  let role = $state(/** @type {'admin' | 'adviser'} */ ('adviser'));
  let department = $state('');
  
  let isSubmitting = $state(false);
  let errorMessage = $state('');
  let successMessage = $state('');

  async function handleRegister(/** @type {SubmitEvent} */ e) {
    e.preventDefault();
    if (!id || !password || !fullName) {
      errorMessage = 'Please fill out all required fields.';
      return;
    }
    if (fullName.length < 2) {
      errorMessage = 'Full name must be at least 2 characters.';
      return;
    }
    if (id.length < 3) {
      errorMessage = 'ID must be at least 3 characters.';
      return;
    }
    if (password.length < 6) {
      errorMessage = 'Password must be at least 6 characters.';
      return;
    }

    isSubmitting = true;
    errorMessage = '';
    successMessage = '';

    try {
      const payload = {
        id,
        password,
        full_name: fullName,
        role,
        ...(role === 'adviser' && department ? { department } : {})
      };
      
      const data = await authApi.register(payload);
      successMessage = data.message;
      
      setTimeout(() => { goto('/login'); }, 2000);

    } catch (/** @type {any} */ err) {
      errorMessage = err.message ?? 'Registration failed.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Register | UniVote Staff Portal</title>
</svelte:head>

<div class="min-h-screen flex bg-surface-main transition-colors duration-500" class:dark={$theme === 'dark'}>
  <!-- Left Branding Panel -->
  <div class="hidden lg:flex w-[44%] flex-col justify-between bg-surface-elevated border-r border-line-main p-12 relative overflow-hidden flex-shrink-0">
    <!-- Decorative circles -->
    <div class="absolute -top-32 -left-32 w-80 h-80 rounded-full border-[40px] border-line-subtle pointer-events-none opacity-50"></div>
    <div class="absolute -top-16 -left-16 w-48 h-48 rounded-full border-[20px] border-line-strong pointer-events-none opacity-30"></div>

    <div class="relative flex items-center gap-4">
      <button 
        onclick={toggleTheme}
        class="w-10 h-10 bg-content-main text-surface-main rounded-2xl flex items-center justify-center text-sm font-black shadow-xl hover:scale-110 active:scale-95 transition-all duration-300 outline-none"
      >
        U
      </button>
      <span class="font-black text-lg tracking-tighter text-content-main uppercase mt-0.5">UniVote</span>
    </div>

    <div class="relative max-w-sm">
      <h1 class="text-5xl font-black text-content-main leading-[1.05] mb-8 tracking-tighter uppercase">
        Join the<br/><span class="text-content-muted">university board.</span>
      </h1>
      <p class="text-content-subtle text-sm leading-relaxed font-bold uppercase tracking-widest mb-12">
        Register as an Admin or Adviser to execute digital protocols and manage student agency.
      </p>

      <div class="space-y-6">
        {#each ['End-to-End Election Ops', 'Student Registry Oversight', 'Real-time Flux Monitoring', 'Verifiable Audit Ledger'] as feature}
          <div class="flex items-center gap-4 group">
            <div class="w-8 h-8 bg-surface-main border border-line-strong rounded-xl flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-brand-primary" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            </div>
            <span class="text-[10px] font-black uppercase tracking-[0.2em] text-content-main transition-colors">{feature}</span>
          </div>
        {/each}
      </div>
    </div>

    <p class="relative text-content-subtle text-[9px] font-black uppercase tracking-[0.3em]">© 2025 UniVote · System Integrity Nominal</p>
  </div>

  <!-- Right Registration Panel -->
  <div class="flex-1 flex flex-col items-center justify-center p-6 md:p-12 overflow-y-auto" in:fade={{ duration: 500 }}>
    <div class="w-full max-w-md py-8">
      <GlassCard title="Access Provisioning" subtitle="Request Personnel Clearance" hideMobileDashboardOnly={false}>
        <!-- Role Switch -->
        <div class="mt-4 flex gap-2 p-1.5 bg-surface-main border border-line-main rounded-2xl transition-all shadow-inner">
          <button 
            type="button" 
            onclick={() => role = 'adviser'}
            class="flex-1 py-3 text-[10px] font-black uppercase tracking-[0.2em] rounded-xl transition-all duration-300 {role === 'adviser' ? 'bg-content-main text-surface-main shadow-xl' : 'text-content-subtle hover:text-content-muted'}"
          >
            Adviser
          </button>
          <button 
            type="button" 
            onclick={() => role = 'admin'}
            class="flex-1 py-3 text-[10px] font-black uppercase tracking-[0.2em] rounded-xl transition-all duration-300 {role === 'admin' ? 'bg-content-main text-surface-main shadow-xl' : 'text-content-subtle hover:text-content-muted'}"
          >
            Admin
          </button>
        </div>

        <form onsubmit={handleRegister} class="mt-8 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="md:col-span-2 space-y-2">
              <label for="fullName" class="field-label ml-1">Legal Identity</label>
              <input type="text" id="fullName" bind:value={fullName} placeholder="Jane Doe" class="input-base w-full uppercase" required>
            </div>

            {#if role === 'adviser'}
              <div class="md:col-span-2 space-y-2" in:fade={{ duration: 200 }}>
                <label for="department" class="field-label ml-1">Departmental Sector</label>
                <input type="text" id="department" bind:value={department} placeholder="e.g. Computer Science" class="input-base w-full uppercase">
              </div>
            {/if}

            <div class="space-y-2">
              <label for="id" class="field-label ml-1">Registry ID</label>
              <input type="text" id="id" bind:value={id} placeholder="e.g. 2026-001" class="input-base w-full uppercase" required>
            </div>
            
            <div class="space-y-2">
              <label for="password" class="field-label ml-1">Master Cipher</label>
              <input type="password" id="password" bind:value={password} placeholder="••••••••" class="input-base w-full uppercase" required minlength="6">
            </div>
          </div>

          {#if errorMessage}
            <div class="pill pill-danger" style="width:100%;justify-content:flex-start;">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              {errorMessage}
            </div>
          {/if}

          {#if successMessage}
            <div class="pill pill-success" style="width:100%;justify-content:flex-start;">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              {successMessage}
            </div>
          {/if}

          <button type="submit" disabled={isSubmitting || !!successMessage} class="btn-primary w-full py-5 text-[11px]">
            {#if isSubmitting}
              <span class="flex items-center justify-center gap-3">
                <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                Committing Data...
              </span>
            {:else}
              Execute Formation
            {/if}
          </button>
        </form>

        <div class="mt-10 pt-8 border-t border-line-main text-center space-y-4">
          <p class="text-[10px] font-black text-content-subtle uppercase tracking-widest">
            Identity Active? <a href="/login" class="text-content-main hover:underline underline-offset-4">Personnel Gate</a>
          </p>
          <a href="/" class="inline-flex items-center gap-2 text-[10px] font-black text-content-subtle hover:text-content-main uppercase tracking-[0.2em] transition-all">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Command Center
          </a>
        </div>
      </GlassCard>
    </div>
  </div>
</div>
