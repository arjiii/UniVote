<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import Notification from '$lib/components/Notification.svelte';

  /** @type {Array<any>} */
  let elections = $state([]);
  let isLoading = $state(true);
  let newElection = $state({ name: '', start_date: '', end_date: '', description: '' });
  let isCreating = $state(false);

  /** @type {{ text: string, type: 'info' | 'success' | 'error' }} */
  let notification = $state({ text: '', type: 'info' });

  onMount(async () => {
    await loadElections();
  });

  async function loadElections() {
    try {
      const res = await adminApi.getElections();
      elections = res.data ?? [];
    } catch (err) { console.error('Failed to load elections:', err); }
    finally { isLoading = false; }
  }

  function notify(text = '', type = /** @type {'info' | 'success' | 'error'} */ ('info')) {
    notification = { text, type };
    setTimeout(() => (notification = { text: '', type: 'info' }), 3500);
  }

  async function handleCreate(/** @type {SubmitEvent} */ e) {
    e.preventDefault();
    if (!newElection.name || !newElection.start_date || !newElection.end_date) {
      notify('Please fill in all required fields.', 'error'); return;
    }
    if (new Date(newElection.end_date) <= new Date(newElection.start_date)) {
      notify('End date must be after start date.', 'error'); return;
    }
    isCreating = true;
    try {
      await adminApi.createElection({
        ...newElection,
        start_date: new Date(newElection.start_date).toISOString(),
        end_date: new Date(newElection.end_date).toISOString()
      });
      await loadElections();
      newElection = { name: '', start_date: '', end_date: '', description: '' };
      notify('Election created successfully', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to create election', 'error'); }
    finally { isCreating = false; }
  }

  async function toggleElection(/** @type {string} */ id, /** @type {string} */ current_status) {
    let nextStatus = 'upcoming';
    if (current_status === 'upcoming') nextStatus = 'active';
    else if (current_status === 'active') nextStatus = 'completed';
    try {
      await adminApi.toggleElection(id, /** @type {any} */ (nextStatus));
      const res = await adminApi.getElections();
      elections = res.data ?? [];
      notify('Election status updated', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Error updating status', 'error'); }
  }

  async function deleteElection(/** @type {string} */ id) {
    if (!confirm('Delete this election and all its data permanently?')) return;
    try {
      await adminApi.deleteElection(id);
      elections = elections.filter(e => e.id !== id);
      notify('Election deleted', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to delete election', 'error'); }
  }
</script>

<svelte:head>
  <title>Elections | UniVote Admin</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    <div>
      <p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-1">Admin</p>
      <h1 class="text-2xl font-semibold text-stone-900 dark:text-white">Elections</h1>
      <p class="text-stone-500 dark:text-stone-400 text-sm mt-0.5">Create and manage all elections.</p>
    </div>
    <button onclick={loadElections} class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl text-sm font-medium text-stone-700 dark:text-stone-200 hover:bg-stone-50 dark:hover:bg-stone-700 transition-all">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
      Refresh
    </button>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
    <!-- Create Form -->
    <div class="bg-white dark:bg-stone-900 rounded-2xl border border-stone-200 dark:border-stone-700 p-6">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-stone-100 dark:bg-stone-800 rounded-xl flex items-center justify-center">
          <svg class="w-5 h-5 text-stone-600 dark:text-stone-300" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/></svg>
        </div>
        <h2 class="text-sm font-semibold text-stone-900 dark:text-white">New Election</h2>
      </div>
      <form onsubmit={handleCreate} class="space-y-4">
        <div>
          <label for="election_name" class="block text-xs font-semibold text-stone-500 dark:text-stone-400 tracking-wide uppercase mb-1.5">Election Name</label>
          <input id="election_name" bind:value={newElection.name} placeholder="e.g. Student Council 2024" class="w-full bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl px-4 py-2.5 text-sm text-stone-900 dark:text-white placeholder-stone-300 dark:placeholder-stone-600 focus:outline-none focus:border-stone-900 dark:focus:border-stone-400 focus:ring-[3px] focus:ring-stone-900/[0.06] dark:focus:ring-white/10 transition-all"/>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="start_date" class="block text-xs font-semibold text-stone-500 dark:text-stone-400 tracking-wide uppercase mb-1.5">Start</label>
            <input id="start_date" type="datetime-local" bind:value={newElection.start_date} class="w-full bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl px-3 py-2.5 text-xs text-stone-900 dark:text-white focus:outline-none focus:border-stone-900 dark:focus:border-stone-400 transition-all"/>
          </div>
          <div>
            <label for="end_date" class="block text-xs font-semibold text-stone-500 dark:text-stone-400 tracking-wide uppercase mb-1.5">End</label>
            <input id="end_date" type="datetime-local" bind:value={newElection.end_date} class="w-full bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl px-3 py-2.5 text-xs text-stone-900 dark:text-white focus:outline-none focus:border-stone-900 dark:focus:border-stone-400 transition-all"/>
          </div>
        </div>
        <button type="submit" disabled={isCreating} class="w-full rounded-xl py-2.5 text-sm font-semibold hover:opacity-90 disabled:opacity-50 transition-all" style="background-color: var(--text-main); color: var(--bg-main);">
          {isCreating ? 'Creating...' : 'Create Election'}
        </button>
      </form>
    </div>

    <!-- Elections List -->
    <div class="lg:col-span-2 bg-white dark:bg-stone-900 rounded-2xl border border-stone-200 dark:border-stone-700 p-6 overflow-hidden">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-stone-100 dark:bg-stone-800 rounded-xl flex items-center justify-center">
          <svg class="w-5 h-5 text-stone-600 dark:text-stone-300" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <h2 class="text-sm font-semibold text-stone-900 dark:text-white">All Elections</h2>
      </div>
      <div class="space-y-3 overflow-y-auto max-h-[500px] pr-2 scrollbar-hide">
        {#if isLoading}
          <div class="py-12 flex items-center justify-center text-stone-400 dark:text-stone-500 text-sm animate-pulse">Loading elections...</div>
        {:else if elections.length === 0}
          <div class="py-12 flex flex-col items-center justify-center border-2 border-dashed border-stone-100 dark:border-stone-800 rounded-xl text-stone-400 dark:text-stone-500 text-sm italic">No elections found.</div>
        {:else}
          {#each elections as election}
            <div class="flex items-center justify-between p-4 bg-stone-50 dark:bg-stone-800 rounded-xl border border-stone-100 dark:border-stone-700 hover:border-stone-200 dark:hover:border-stone-600 transition-all group">
              <div>
                <p class="font-medium text-stone-900 dark:text-white text-sm">{election.name}</p>
                <div class="flex items-center gap-3 mt-1">
                  <span class="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide
                    {election.status === 'active' ? 'text-emerald-600' : election.status === 'completed' ? 'text-stone-500 dark:text-stone-400' : 'text-amber-600'}">
                    <span class="w-1.5 h-1.5 rounded-full {election.status === 'active' ? 'bg-emerald-500 animate-pulse' : election.status === 'completed' ? 'bg-stone-400' : 'bg-amber-400'}"></span>
                    {election.status}
                  </span>
                  <span class="text-[10px] text-stone-400 dark:text-stone-500 bg-stone-100 dark:bg-stone-700 px-1.5 py-0.5 rounded italic">Ends {new Date(election.end_date).toLocaleDateString()}</span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                {#if election.status === 'upcoming'}
                  <button onclick={() => toggleElection(election.id, election.status)} class="bg-stone-900 text-white hover:bg-stone-800 rounded-lg px-3 py-1.5 text-[10px] font-bold uppercase transition-all">Start</button>
                {:else if election.status === 'active'}
                  <button onclick={() => toggleElection(election.id, election.status)} class="bg-red-50 text-red-600 border border-red-100 hover:bg-red-100 rounded-lg px-3 py-1.5 text-[10px] font-bold uppercase transition-all">End</button>
                {/if}
                <button onclick={() => deleteElection(election.id)} class="p-2 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100" title="Delete">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
</div>

<div class="fixed bottom-6 right-6 z-[60]">
  <Notification text={notification.text} type={notification.type} />
</div>
