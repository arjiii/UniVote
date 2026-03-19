<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth as authApi } from '$lib/api.js';
  import { authSession } from '$lib/stores/auth.js';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { fade, fly } from 'svelte/transition';

  onMount(() => {
    if ($authSession) {
      goto($authSession.role === 'admin' ? '/admin' : '/adviser');
    }
  });

  let email = $state('');
  let password = $state('');
  let showPassword = $state(false);
  let isSubmitting = $state(false);
  let errorMessage = $state('');

  async function handleLogin(/** @type {SubmitEvent} */ e) {
    e.preventDefault();
    if (!email || !password) {
      errorMessage = 'Please enter both email and password.';
      return;
    }

    isSubmitting = true;
    errorMessage = '';

    try {
      const data = await authApi.login(email, password);
      authSession.login(data);
      goto(data.role === 'admin' ? '/admin' : '/adviser');
    } catch (/** @type {any} */ err) {
      errorMessage = err.message ?? 'Sign in failed. Please check your credentials.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Sign In | UniVote Staff Portal</title>
</svelte:head>

<div class="min-h-screen flex bg-[#f9f8f6]">

  <!-- Left branding panel (dark) -->
  <div class="hidden lg:flex w-[44%] bg-stone-900 flex-col justify-between p-10 relative overflow-hidden flex-shrink-0">
    <!-- Subtle grid -->
    <div class="absolute inset-0 opacity-[0.04]"
      style="background-image:linear-gradient(rgba(255,255,255,1) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,1) 1px,transparent 1px);background-size:48px 48px"></div>

    <div class="relative">
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 bg-white rounded-md flex items-center justify-center text-stone-900 text-xs font-bold">U</div>
        <span class="text-white font-semibold text-sm tracking-tight">UniVote</span>
      </div>
    </div>

    <div class="relative">
      <div class="inline-flex items-center gap-2 bg-white/10 border border-white/10 rounded-full px-3 py-1 mb-6">
        <span class="w-1.5 h-1.5 bg-emerald-400 rounded-full block"></span>
        <span class="text-xs text-white/70 font-medium">Secure E-Voting</span>
      </div>
      <h2 class="text-4xl text-white leading-[1.15] mb-4" style="font-family:'Instrument Serif',Georgia,serif">
        The future of<br/><em>campus elections.</em>
      </h2>
      <p class="text-stone-400 text-sm leading-relaxed max-w-xs">
        Transparent, secure, and accessible digital voting for your university community.
      </p>

      <div class="grid grid-cols-2 gap-3 mt-8">
        <div class="bg-white/5 border border-white/8 rounded-xl p-4">
          <p class="text-white text-xl font-semibold mb-0.5">100%</p>
          <p class="text-stone-500 text-xs">Encrypted Votes</p>
        </div>
        <div class="bg-white/5 border border-white/8 rounded-xl p-4">
          <p class="text-white text-xl font-semibold mb-0.5">Live</p>
          <p class="text-stone-500 text-xs">Result Tracking</p>
        </div>
      </div>
    </div>

    <p class="relative text-stone-600 text-xs">© 2025 UniVote. All rights reserved.</p>
  </div>

  <!-- Right form panel -->
  <div class="flex-1 flex items-center justify-center px-6 py-12" in:fade={{ duration: 400 }}>
    <div class="w-full max-w-sm">

      <!-- Mobile logo -->
      <div class="lg:hidden flex items-center gap-2 mb-8">
        <div class="w-7 h-7 bg-stone-900 rounded-md flex items-center justify-center text-white text-xs font-bold">U</div>
        <span class="font-semibold text-sm">UniVote</span>
      </div>

      <div in:fly={{ y: 14, duration: 400, delay: 50 }}>
        <h1 class="text-2xl font-semibold text-stone-900 mb-1">Welcome back</h1>
        <p class="text-stone-500 text-sm">Sign in to your staff account</p>
      </div>

      <form onsubmit={handleLogin} class="mt-8 space-y-4" in:fly={{ y: 14, duration: 400, delay: 120 }}>

        <!-- Email -->
        <div>
          <label for="email" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Email Address</label>
          <input 
            type="email" 
            id="email" 
            bind:value={email} 
            placeholder="admin@univote.edu"
            class="w-full bg-white border border-stone-200 rounded-xl px-4 py-3 text-sm text-stone-900 placeholder-stone-300 transition-all duration-200 focus:outline-none focus:border-stone-900 focus:ring-[3px] focus:ring-stone-900/[0.06]"
            required
          >
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Password</label>
          <div class="relative">
            <input 
              type={showPassword ? 'text' : 'password'}
              id="password" 
              bind:value={password} 
              placeholder="••••••••"
              class="w-full bg-white border border-stone-200 rounded-xl px-4 py-3 pr-12 text-sm text-stone-900 placeholder-stone-300 transition-all duration-200 focus:outline-none focus:border-stone-900 focus:ring-[3px] focus:ring-stone-900/[0.06]"
              required
            >
            <button 
              type="button" 
              onclick={() => showPassword = !showPassword}
              class="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-700 transition-colors"
            >
              {#if showPassword}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/></svg>
              {:else}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
              {/if}
            </button>
          </div>
        </div>

        <!-- Error -->
        {#if errorMessage}
          <div class="bg-red-50 border border-red-200 rounded-xl px-4 py-3 flex items-center gap-2" in:fly={{ y: -5, duration: 200 }}>
            <svg class="w-4 h-4 text-red-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
            <p class="text-red-600 text-xs font-medium">{errorMessage}</p>
          </div>
        {/if}

        <!-- Submit -->
        <div class="pt-1">
          <button 
            type="submit" 
            disabled={isSubmitting}
            class="w-full bg-stone-900 text-white rounded-xl py-3 text-sm font-semibold transition-all duration-200 hover:bg-stone-800 active:scale-[0.99] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden"
          >
            {#if isSubmitting}
              <LoadingSpinner />
              <span>Signing in...</span>
            {:else}
              <span>Sign In</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
            {/if}
          </button>
        </div>
      </form>

      <div class="mt-6 pt-6 border-t border-stone-200 text-center space-y-3" in:fly={{ y: 14, duration: 400, delay: 200 }}>
        <p class="text-xs text-stone-500">
          Need portal access? <a href="/register" class="text-stone-900 font-medium hover:underline">Request Account</a>
        </p>
        <a href="/" class="inline-flex items-center gap-1 text-xs text-stone-400 hover:text-stone-700 transition-colors">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back to home
        </a>
      </div>
    </div>
  </div>
</div>
