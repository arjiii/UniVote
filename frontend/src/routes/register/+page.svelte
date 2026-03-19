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

<div class="min-h-screen flex bg-slate-50">
  <!-- Left Branding Panel -->
  <div class="hidden lg:flex flex-col justify-between w-[45%] bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-700 p-12 relative overflow-hidden">
    <div class="absolute inset-0 opacity-10">
      <div class="absolute -top-20 -left-20 w-80 h-80 rounded-full border-[50px] border-white"></div>
      <div class="absolute bottom-0 right-0 w-96 h-96 rounded-full border-[60px] border-white"></div>
    </div>

    <div class="relative z-10 flex items-center gap-3">
      <a href="/" class="flex items-center gap-3">
        <div class="w-10 h-10 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center border border-white/30">
          <span class="text-white font-black text-lg">U</span>
        </div>
        <span class="text-white font-bold text-xl tracking-tight">UniVote</span>
      </a>
    </div>

    <div class="relative z-10">
      <h1 class="text-4xl font-black text-white leading-tight mb-4">
        Join the<br/>UniVote team.
      </h1>
      <p class="text-white/70 text-sm leading-relaxed max-w-xs mb-10">
        Register as an Admin or Adviser to manage elections, candidates, and results.
      </p>

      <div class="space-y-4">
        {#each ['Manage Elections End-to-End', 'Import & Oversee Student Voters', 'Monitor Results in Real-time', 'Full Activity Audit Trail'] as feature}
          <div class="flex items-center gap-3 text-white/90 text-sm">
            <div class="w-6 h-6 rounded-full bg-white/20 border border-white/30 flex items-center justify-center shrink-0">
              <svg class="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            </div>
            <span class="font-medium">{feature}</span>
          </div>
        {/each}
      </div>
    </div>

    <p class="relative z-10 text-white/40 text-xs">© 2025 UniVote. All rights reserved.</p>
  </div>

  <!-- Right Registration Panel -->
  <div class="flex-1 flex flex-col items-center justify-center p-8 overflow-y-auto" in:fade={{ duration: 500 }}>
    <div class="w-full max-w-md py-8">
      <!-- Mobile logo -->
      <div class="lg:hidden flex items-center gap-2 mb-8">
        <a href="/" class="flex items-center gap-2">
          <div class="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center">
            <span class="text-white font-black">U</span>
          </div>
          <span class="font-bold text-slate-900 text-lg">UniVote</span>
        </a>
      </div>

      <div in:fly={{ y: 20, duration: 500, delay: 100 }}>
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">Create account</h2>
        <p class="text-slate-500 text-sm mt-1.5 font-medium">Request staff access to the UniVote portal</p>
      </div>

      <!-- Role Switch -->
      <div class="mt-6 flex gap-2 p-1.5 bg-slate-100 rounded-xl border border-slate-200" in:fly={{ y: 20, duration: 500, delay: 150 }}>
        <button 
          type="button" 
          onclick={() => role = 'adviser'}
          class="flex-1 py-2 text-sm font-semibold rounded-lg transition-all duration-200 {role === 'adviser' ? 'bg-white text-indigo-700 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-800'}"
        >
          Adviser
        </button>
        <button 
          type="button" 
          onclick={() => role = 'admin'}
          class="flex-1 py-2 text-sm font-semibold rounded-lg transition-all duration-200 {role === 'admin' ? 'bg-white text-indigo-700 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-800'}"
        >
          Administrator
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

        <button type="submit" disabled={isSubmitting || !!successMessage} class="btn-primary">
          {#if isSubmitting}
            <LoadingSpinner />
            <span>Creating Account...</span>
          {:else}
            Complete Registration
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
