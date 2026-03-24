<script>
  import { voterSession } from '$lib/stores/session.js';
  import { page } from '$app/state';
  import Sidebar from '$lib/components/Sidebar.svelte';

  /** @type {{ children: import('svelte').Snippet }} */
  let { children } = $props();

  const showSidebar = $derived(
    $voterSession && page.url.pathname !== '/student/validate'
  );
</script>

{#if showSidebar}
  <Sidebar role="student" student_info={$voterSession}>
    {@render children()}
  </Sidebar>
{:else}
  <div class="min-h-screen">
    {@render children()}
  </div>
{/if}
