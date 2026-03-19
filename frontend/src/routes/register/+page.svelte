<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth as authApi } from '$lib/api.js';
  import { authSession } from '$lib/stores/auth.js';
  import { theme, toggleTheme } from '$lib/stores/theme.js';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { fade, fly } from 'svelte/transition';

  onMount(() => {
    if ($authSession) {
      goto($authSession.role === 'admin' ? '/admin' : '/adviser');
    }
  });

  let fullName = $state('');
  let email = $state('');
  let password = $state('');
  let role = $state(/** @type {'admin' | 'adviser'} */ ('adviser'));
  let department = $state('');
  
  let isSubmitting = $state(false);
  let errorMessage = $state('');
  let successMessage = $state('');

  async function handleRegister(/** @type {SubmitEvent} */ e) {
    e.preventDefault();
    if (!email || !password || !fullName) {
      errorMessage = 'Please fill out all required fields.';
      return;
    }
    if (fullName.length < 2) {
      errorMessage = 'Full name must be at least 2 characters.';
      return;
    }
    if (!email.includes('@')) {
      errorMessage = 'Please enter a valid email address.';
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
        email,
        password,
        full_name: fullName,
        role,
        ...(role === 'adviser' && department ? { department } : {})
      };
      
      const data = await authApi.register(payload);
      successMessage = data.message;
      
      setTimeout(() => {
        goto('/login');
      }, 2000);

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

<div class="min-h-screen flex bg-stone-50 dark:bg-stone-950 transition-colors duration-500" class:dark={$theme === 'dark'}>
  <!-- Left Branding Panel -->
  <div class="hidden lg:flex w-[44%] flex-col justify-between bg-stone-100 dark:bg-stone-900 border-r border-stone-200 dark:border-stone-800 p-10 relative overflow-hidden flex-shrink-0">
    <!-- Decorative circles -->
    <div class="absolute -top-32 -left-32 w-80 h-80 rounded-full border-[40px] border-stone-200/50 dark:border-stone-800/50 pointer-events-none"></div>
    <div class="absolute -top-16 -left-16 w-48 h-48 rounded-full border-[20px] border-stone-300/30 dark:border-stone-700/30 pointer-events-none"></div>

    <div class="relative flex items-center gap-3">
      <button 
        onclick={toggleTheme}
        class="w-8 h-8 bg-stone-950 dark:bg-stone-50 rounded-xl flex items-center justify-center text-white dark:text-stone-950 text-xs font-black shadow-xl hover:shadow-brand-500/20 hover:scale-110 hover:rotate-3 active:scale-95 transition-all duration-300 outline-none"
      >
        U
      </button>
      <span class="font-bold text-sm tracking-tight dark:text-white transition-colors">UniVote</span>
    </div>

    <div class="relative">
      <h1 class="text-4xl font-black text-stone-950 dark:text-white leading-[1.1] mb-6 tracking-tighter transition-colors">
        Join the<br/><span class="text-stone-500">UniVote team.</span>
      </h1>
      <p class="text-stone-500 dark:text-stone-400 text-sm leading-relaxed max-w-xs mb-10 font-medium transition-colors">
        Register as an Admin or Adviser to manage elections, candidates, and results.
      </p>

      <div class="space-y-4">
        {#each ['Manage Elections End-to-End', 'Import & Oversee Student Voters', 'Monitor Results in Real-time', 'Full Activity Audit Trail'] as feature}
          <div class="flex items-center gap-3 group">
            <div class="w-6 h-6 bg-stone-200 dark:bg-stone-800 rounded-lg flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
              <svg class="w-3.5 h-3.5 text-emerald-500" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            </div>
            <span class="text-sm font-bold text-stone-700 dark:text-stone-300 transition-colors">{feature}</span>
          </div>
        {/each}
      </div>
    </div>

    <p class="relative text-stone-400 dark:text-stone-600 text-[10px] font-bold uppercase tracking-widest">© 2025 UniVote. All rights reserved.</p>
  </div>

  <!-- Right Registration Panel -->
  <div class="flex-1 flex flex-col items-center justify-center p-8 overflow-y-auto" in:fade={{ duration: 500 }}>
    <div class="w-full max-w-md py-8">
      <!-- Mobile logo -->
      <div class="lg:hidden flex items-center gap-3 mb-10">
        <button 
          onclick={toggleTheme}
          class="w-9 h-9 bg-stone-900 dark:bg-stone-50 rounded-xl flex items-center justify-center text-white dark:text-stone-950 text-base font-black shadow-xl hover:scale-110 active:scale-95 transition-all outline-none"
        >
          U
        </button>
        <span class="font-bold text-stone-950 dark:text-white text-lg transition-colors">UniVote</span>
      </div>

      <div in:fly={{ y: 20, duration: 500, delay: 100 }}>
        <h2 class="text-3xl font-black text-stone-950 dark:text-white tracking-tighter transition-colors">Create account</h2>
        <p class="text-stone-500 dark:text-stone-400 text-sm mt-1.5 font-medium transition-colors">Request staff access to the UniVote portal</p>
      </div>

      <!-- Role Switch -->
      <div class="mt-6 flex gap-2 p-1.5 bg-stone-100 dark:bg-stone-900 rounded-2xl border border-stone-200 dark:border-stone-800 transition-colors" in:fly={{ y: 20, duration: 500, delay: 150 }}>
        <button 
          type="button" 
          onclick={() => role = 'adviser'}
          class="flex-1 py-2.5 text-xs font-black uppercase tracking-widest rounded-xl transition-all duration-300 {role === 'adviser' ? 'bg-white dark:bg-stone-800 text-stone-950 dark:text-white shadow-xl shadow-black/5' : 'text-stone-400 hover:text-stone-600'}"
        >
          Adviser
        </button>
        <button 
          type="button" 
          onclick={() => role = 'admin'}
          class="flex-1 py-2.5 text-xs font-black uppercase tracking-widest rounded-xl transition-all duration-300 {role === 'admin' ? 'bg-white dark:bg-stone-800 text-stone-950 dark:text-white shadow-xl shadow-black/5' : 'text-stone-400 hover:text-stone-600'}"
        >
          Admin
        </button>
      </div>

      <form onsubmit={handleRegister} class="mt-6 space-y-4" in:fly={{ y: 20, duration: 500, delay: 200 }}>
        <!-- Full name + department row on md+ -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label for="fullName" class="field-label">Full Name</label>
            <input 
              type="text" 
              id="fullName" 
              bind:value={fullName} 
              placeholder="Jane Doe"
              class="input-base"
              required
            >
            <p class="text-slate-400 text-[10px] mt-1.5">Legal name as it appears on official records.</p>
          </div>

          {#if role === 'adviser'}
            <div class="md:col-span-2" in:fade={{ duration: 200 }}>
              <label for="department" class="field-label">Department (Optional)</label>
              <input 
                type="text" 
                id="department" 
                bind:value={department} 
                placeholder="e.g. Computer Science"
                class="input-base"
              >
            </div>
          {/if}

          <div>
            <label for="email" class="field-label">Email Address</label>
            <input 
              type="email" 
              id="email" 
              bind:value={email} 
              placeholder="staff@univote.edu"
              class="input-base"
              required
            >
          </div>
          
          <div>
            <label for="password" class="field-label">Password</label>
            <input 
              type="password" 
              id="password" 
              bind:value={password} 
              placeholder="Min. 6 characters"
              class="input-base"
              required
              minlength="6"
            >
          </div>
        </div>

        {#if errorMessage}
          <div class="p-3.5 rounded-xl bg-red-50 border border-red-200 flex items-start gap-2.5 text-red-700 text-sm" in:fly={{ y: -5, duration: 200 }}>
            <svg class="w-4 h-4 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
            <p class="font-medium">{errorMessage}</p>
          </div>
        {/if}

        {#if successMessage}
          <div class="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start gap-2.5 text-emerald-700 text-sm" in:fade>
            <svg class="w-4 h-4 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
            <p class="font-semibold">{successMessage}</p>
          </div>
        {/if}

        <button 
          type="submit" 
          disabled={isSubmitting || !!successMessage}
          class="btn-premium w-full py-4 text-sm font-black shadow-2xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {#if isSubmitting}
            <LoadingSpinner />
            <span>Creating Account...</span>
          {:else}
            <span>Complete Registration</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
          {/if}
        </button>
      </form>

      <div class="mt-6 pt-5 border-t border-slate-200 text-center">
        <p class="text-sm text-slate-500 font-medium">
          Already have an account? 
          <a href="/login" class="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors ml-1">Sign In</a>
        </p>
      </div>
    </div>
  </div>
</div>
