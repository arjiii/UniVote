<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authSession } from '$lib/stores/auth.js';
  import Sidebar from '$lib/components/Sidebar.svelte';

  /** @type {{ children: import('svelte').Snippet }} */
  let { children } = $props();
  let isChecking = $state(true);

  onMount(() => {
    const unsub = authSession.subscribe((session) => {
      if (!session) {
        goto('/login', { replaceState: true });
      } else if (session.role === 'adviser') {
        goto('/adviser', { replaceState: true });
      } else if (session.role === 'admin') {
        isChecking = false;
      } else {
        goto('/login', { replaceState: true });
      }
    });
    
    return unsub;
  });
</script>

{#if !isChecking}
  <Sidebar role="admin" student_info={$authSession}>
    {@render children()}
  </Sidebar>
{:else}
  <div class="min-h-screen flex items-center justify-center bg-slate-950">
    <div class="h-8 w-8 rounded-full border-4 border-indigo-500/30 border-t-indigo-500 animate-spin"></div>
  </div>
{/if}
