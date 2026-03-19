<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authSession } from '$lib/stores/auth.js';
  import { voterSession } from '$lib/stores/session.js';
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

<div class="bg-[#f9f8f6] text-stone-900 min-h-screen flex flex-col">

  <!-- NAV -->
  <nav class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-stone-200/80">
    <div class="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 bg-stone-900 rounded-md flex items-center justify-center text-white text-xs font-bold tracking-tight">U</div>
        <span class="font-semibold text-sm tracking-tight">UniVote</span>
      </div>
      <a href="/login" class="group flex items-center gap-1 text-xs font-medium text-stone-500 hover:text-stone-900 transition-colors">
        Staff Portal
        <svg class="w-3 h-3 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
    </div>
  </nav>

  <main class="flex-1 max-w-5xl mx-auto px-6">

    <!-- Hero -->
    <div class="text-center pt-10 pb-8">
      <h1 class="text-3xl md:text-4xl leading-[1.1] text-stone-900 mb-4" style="font-family:'Instrument Serif',Georgia,serif" in:fly={{ y: 18, duration: 500, delay: 100 }}>
        Campus elections,<br/><span class="text-stone-400 text-2xl md:text-3xl">reimagined.</span>
      </h1>
      <p class="text-stone-500 text-sm font-light max-w-sm mx-auto leading-relaxed" in:fly={{ y: 18, duration: 500, delay: 180 }}>
        Transparent ballot management, real-time results, and secure student access — all in one platform.
      </p>
    </div>

    <!-- Cards -->
    <div class="grid md:grid-cols-2 gap-4 pb-10" in:fly={{ y: 24, duration: 600, delay: 280 }}>

      <!-- Student -->
      <a href="/student/validate"
         class="group bg-white border border-stone-200 rounded-2xl p-7 flex flex-col gap-5 hover:border-stone-300 hover:-translate-y-[3px] hover:shadow-[0_12px_40px_-8px_rgba(0,0,0,0.1)] transition-all duration-250">
        <div class="flex items-start justify-between">
          <div class="w-10 h-10 bg-stone-900 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <svg class="w-4 h-4 text-stone-300 group-hover:text-stone-700 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M7 7h10v10"/></svg>
        </div>
        <div>
          <p class="text-[9px] font-semibold text-stone-400 tracking-widest uppercase mb-1.5">For Students</p>
          <h2 class="text-lg font-semibold text-stone-900 mb-2">Cast Your Vote</h2>
          <p class="text-stone-500 text-xs leading-relaxed">Verify your Student ID and access the secure ballot in seconds.</p>
        </div>
        <div class="border-t border-stone-100 pt-4 flex flex-col gap-1.5">
          <p class="flex items-center gap-2 text-xs text-stone-500">
            <svg class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            Completely anonymous
          </p>
          <p class="flex items-center gap-2 text-xs text-stone-500">
            <svg class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            One vote per student, results in real-time
          </p>
        </div>
      </a>

      <!-- Staff -->
      <a href="/login"
         class="group bg-stone-900 border border-stone-800 rounded-2xl p-7 flex flex-col gap-5 hover:bg-stone-800 hover:border-stone-700 hover:-translate-y-[3px] hover:shadow-[0_12px_40px_-8px_rgba(0,0,0,0.15)] transition-all duration-250">
        <div class="flex items-start justify-between">
          <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75"/>
            </svg>
          </div>
          <svg class="w-4 h-4 text-stone-600 group-hover:text-stone-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 17L17 7M7 7h10v10"/></svg>
        </div>
        <div>
          <p class="text-[9px] font-semibold text-stone-500 tracking-widest uppercase mb-1.5">For Staff</p>
          <h2 class="text-lg font-semibold text-white mb-2">Staff Portal</h2>
          <p class="text-stone-400 text-xs leading-relaxed">Manage elections, add candidates, and monitor live results.</p>
        </div>
        <div class="border-t border-stone-800 pt-4 flex flex-col gap-1.5">
          <p class="flex items-center gap-2 text-xs text-stone-500">
            <svg class="w-3.5 h-3.5 text-stone-500 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            100% encrypted votes
          </p>
          <p class="flex items-center gap-2 text-xs text-stone-500">
            <svg class="w-3.5 h-3.5 text-stone-500 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            Real-time result tracking
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
