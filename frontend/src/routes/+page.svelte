<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authSession } from '$lib/stores/auth.js';
  import { voterSession } from '$lib/stores/session.js';
  import { toggleTheme } from '$lib/stores/theme.js';
  import { fade, fly } from 'svelte/transition';

  onMount(() => {
    if ($authSession) {
      goto($authSession.role === 'admin' ? '/admin' : '/adviser');
    } else if ($voterSession) {
      goto('/student/ballot');
    }
  });
</script>

<svelte:head>
  <title>UniVote — Secure Campus Elections</title>
</svelte:head>

<div class="bg-[#f9f8f6] dark:bg-stone-950 text-stone-900 dark:text-stone-100 min-h-screen flex flex-col transition-colors duration-300">

  <!-- NAV -->
  <nav class="fixed top-0 left-0 right-0 h-14 z-50 transition-all duration-500 glass-themed">
    <div class="max-w-6xl mx-auto px-6 h-full flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button 
          onclick={toggleTheme}
          class="w-8 h-8 bg-stone-900 dark:bg-stone-50 rounded-xl flex items-center justify-center text-white dark:text-stone-950 text-xs font-black shadow-xl hover:shadow-brand-500/20 hover:scale-110 hover:rotate-3 active:scale-90 transition-all duration-300 outline-none"
          title="Toggle Dark Mode"
        >
          U
        </button>
        <span class="font-bold text-sm tracking-tight dark:text-white transition-colors duration-500">UniVote</span>
      </div>
    </div>
  </nav>

  <main class="flex-1 max-w-6xl mx-auto px-6">

    <!-- Hero Service -->
    <div class="pt-24 pb-6 text-center" in:fly={{ y: -20, duration: 800 }}>
      <h1 class="text-4xl md:text-5xl font-black text-stone-900 dark:text-white leading-[1.05] tracking-tighter mb-4 transition-colors">
        Campus elections, <br/>
        <span class="text-stone-500 dark:text-stone-400">reimagined.</span>
      </h1>
      <p class="text-stone-500 dark:text-stone-400 text-base font-medium max-w-2xl mx-auto leading-relaxed transition-colors px-4">
        Transparent ballot management, real-time results, and <br class="hidden md:block" />
        secure student access — all in a professional platform.
      </p>
    </div>

    <!-- Cards -->
    <div class="grid md:grid-cols-2 gap-5 pb-12" in:fly={{ y: 24, duration: 800, delay: 200 }}>

      <!-- Student -->
      <a href="/student/validate"
         class="group card-themed p-6 flex flex-col gap-5">
        <div class="flex items-start justify-between">
          <div class="icon-box-themed w-10 h-10 rounded-2xl bg-stone-950 dark:bg-stone-50 text-white dark:text-stone-950 shadow-xl shadow-black/5 dark:shadow-white/5">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-stone-300 dark:text-stone-700 bg-stone-50/50 dark:bg-stone-800/50 group-hover:text-stone-950 dark:group-hover:text-white group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-500 border border-transparent group-hover:border-stone-200 dark:group-hover:border-stone-700">
            <svg class="w-4 h-4 font-bold" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M7 7h10v10"/></svg>
          </div>
        </div>
        <div>
          <p class="text-[9px] font-black text-stone-400 dark:text-stone-500 tracking-[0.2em] uppercase mb-2 transition-colors">For Students</p>
          <h2 class="text-lg font-bold text-stone-900 dark:text-white mb-1.5 transition-colors">Cast Your Vote</h2>
          <p class="text-stone-500 dark:text-stone-400 text-xs leading-relaxed transition-colors">Verify your Student ID and access the secure ballot in seconds.</p>
        </div>
        <div class="mt-auto border-t border-stone-100 dark:border-stone-800 pt-4 flex flex-col gap-2">
          <p class="flex items-center gap-2 text-[10px] font-bold text-stone-500 dark:text-stone-400">
            <svg class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            Completely anonymous
          </p>
          <p class="flex items-center gap-2 text-[10px] font-bold text-stone-500 dark:text-stone-400">
            <svg class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            One vote per student
          </p>
        </div>
      </a>

      <!-- Staff -->
      <a href="/login"
         class="group card-themed p-6 flex flex-col gap-5">
        <div class="flex items-start justify-between">
          <div class="icon-box-themed w-10 h-10 rounded-2xl bg-stone-950 dark:bg-stone-50 text-white dark:text-stone-950 shadow-xl shadow-black/5 dark:shadow-white/5">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"/>
            </svg>
          </div>
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-stone-300 dark:text-stone-700 bg-stone-50/50 dark:bg-stone-800/50 group-hover:text-stone-950 dark:group-hover:text-white group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-500 border border-transparent group-hover:border-stone-200 dark:group-hover:border-stone-700">
            <svg class="w-4 h-4 font-bold" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M7 7h10v10"/></svg>
          </div>
        </div>
        <div>
          <p class="text-[9px] font-black text-stone-400 dark:text-stone-500 tracking-[0.2em] uppercase mb-2 transition-colors">For Staff</p>
          <h2 class="text-lg font-bold text-stone-900 dark:text-white mb-1.5 transition-colors">Staff Portal</h2>
          <p class="text-stone-500 dark:text-stone-400 text-xs leading-relaxed transition-colors">Manage elections, add candidates, and monitor live results.</p>
        </div>
        <div class="mt-auto border-t border-stone-100 dark:border-stone-800 pt-4 flex flex-col gap-2">
          <p class="flex items-center gap-2 text-[10px] font-bold text-stone-500 dark:text-stone-400">
            <svg class="w-3.5 h-3.5 text-brand-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            100% encrypted votes
          </p>
          <p class="flex items-center gap-2 text-[10px] font-bold text-stone-500 dark:text-stone-400">
            <svg class="w-3.5 h-3.5 text-brand-500 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            Real-time tracking
          </p>
        </div>
      </a>
    </div>
  </main>

  <footer class="border-t border-stone-200 bg-white">
    <div class="max-w-5xl mx-auto px-6 h-12 flex items-center justify-between">
      <p class="text-[10px] text-stone-400">© 2025 UniVote. All rights reserved.</p>
      <p class="text-[10px] text-stone-400">Secure · Private · Transparent</p>
    </div>
  </footer>
</div>

<style>
  :global(body) {
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none;  /* IE and Edge */
  }
  :global(body::-webkit-scrollbar) {
    display: none; /* Chrome, Safari and Opera */
  }
</style>
