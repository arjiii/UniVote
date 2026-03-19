<script>
  import { goto } from '$app/navigation';
  import { student as studentApi } from '$lib/api.js';
  import { voterSession } from '$lib/stores/session.js';
  import { theme, toggleTheme } from '$lib/stores/theme.js';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { fade, fly } from 'svelte/transition';
  
  let studentId = $state('');
  let isChecking = $state(false);
  let errorMessage = $state('');

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
      errorMessage = err.message ?? 'Error validating student ID.';
    } finally {
      isChecking = false;
    }
  }
</script>

<svelte:head>
  <title>Student Access | UniVote</title>
</svelte:head>

<div class="min-h-screen flex bg-stone-50 dark:bg-stone-950 transition-colors duration-500" class:dark={$theme === 'dark'}>

  <!-- Left panel: brand + trust signals -->
  <div class="hidden lg:flex w-[44%] flex-col justify-between bg-stone-100 dark:bg-stone-900 border-r border-stone-200 dark:border-stone-800 p-10 relative overflow-hidden flex-shrink-0">
    <!-- Decorative circles -->
    <div class="absolute -bottom-32 -right-32 w-80 h-80 rounded-full border-[40px] border-stone-200/50 dark:border-stone-800/50 pointer-events-none"></div>
    <div class="absolute -bottom-16 -right-16 w-48 h-48 rounded-full border-[20px] border-stone-300/30 dark:border-stone-700/30 pointer-events-none"></div>

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
      <div class="inline-flex items-center gap-2 bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-full px-3 py-1 mb-6">
        <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full block animate-pulse"></span>
        <span class="text-emerald-700 dark:text-emerald-400 text-[10px] font-bold uppercase tracking-widest transition-colors">Election Active</span>
      </div>
      <h2 class="text-4xl font-black text-stone-950 dark:text-white leading-[1.1] mb-4 tracking-tighter transition-colors">
        Ready to cast<br/><span class="text-stone-500">your vote?</span>
      </h2>
      <p class="text-stone-500 dark:text-stone-400 text-sm leading-relaxed max-w-xs mb-10 font-medium transition-colors">
        Verify your identity with your Student ID to access the secure ballot and make your voice count.
      </p>

      <div class="space-y-4">
        {#each ['Your vote is completely anonymous', 'You can only vote once', 'Results updated in real-time'] as point}
          <div class="flex items-center gap-3 group">
            <div class="w-7 h-7 bg-emerald-100 dark:bg-emerald-500/10 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-500" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            </div>
            <span class="text-sm font-bold text-stone-700 dark:text-stone-300 transition-colors">{point}</span>
          </div>
        {/each}
      </div>
    </div>

    <p class="relative text-stone-400 dark:text-stone-600 text-[10px] font-bold uppercase tracking-widest">© 2025 UniVote. All rights reserved.</p>
  </div>

  <!-- Right form -->
  <div class="flex-1 flex items-center justify-center px-6 py-12" in:fade={{ duration: 400 }}>
    <div class="w-full max-w-sm">

      <!-- Mobile logo -->
      <div class="lg:hidden flex items-center gap-3 mb-10">
        <button 
          onclick={toggleTheme}
          class="w-9 h-9 bg-stone-900 dark:bg-stone-50 rounded-xl flex items-center justify-center text-white dark:text-stone-950 text-base font-black shadow-xl hover:scale-110 active:scale-95 transition-all outline-none"
        >
          U
        </button>
        <span class="font-bold text-lg dark:text-white transition-colors">UniVote</span>
      </div>

      <!-- Header -->
      <div in:fly={{ y: 14, duration: 400, delay: 50 }}>
        <h1 class="text-3xl font-black text-stone-950 dark:text-white mb-2 tracking-tighter transition-colors">Student Access</h1>
        <p class="text-stone-500 dark:text-stone-400 text-sm font-medium transition-colors">Enter your Student ID to access the ballot.</p>
      </div>

      <form onsubmit={checkStudentId} class="mt-8" in:fly={{ y: 14, duration: 400, delay: 120 }}>

        <!-- ID field -->
        <div class="mb-5">
          <label for="studentId" class="block text-[10px] font-bold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-2">Student ID Number</label>
          <div class="relative">
            <div class="absolute left-4 top-1/2 -translate-y-1/2 text-stone-400 dark:text-stone-500 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z"/></svg>
            </div>
            <input 
              id="studentId"
              type="text" 
              bind:value={studentId}
              placeholder="e.g. 2021-00123"
              class="input-base !pl-11 !py-3.5 font-mono"
              required
            />
          </div>
          <p class="text-[10px] text-stone-400 font-bold mt-2 tracking-tight">Your official University-issued ID number.</p>
        </div>

        <!-- Error -->
        {#if errorMessage}
          <div class="mb-5 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-2xl px-4 py-3 flex items-center gap-2.5" in:fly={{ y: -5, duration: 200 }}>
            <svg class="w-4 h-4 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
            <p class="text-red-600 dark:text-red-400 text-xs font-bold">{errorMessage}</p>
          </div>
        {/if}

        <!-- Submit -->
        <button 
          type="submit" 
          disabled={isChecking || !studentId}
          class="btn-premium w-full py-4 text-sm font-black shadow-2xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {#if isChecking}
            <LoadingSpinner />
            <span>Verifying...</span>
          {:else}
            <span>Proceed to Ballot</span>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
          {/if}
        </button>
      </form>

      <div class="mt-8 pt-6 border-t border-stone-100 dark:border-stone-800 text-center" in:fly={{ y: 14, duration: 400, delay: 200 }}>
        <a href="/" class="inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest text-stone-400 hover:text-stone-900 dark:hover:text-white transition-colors">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back to home
        </a>
      </div>
    </div>
  </div>
</div>
