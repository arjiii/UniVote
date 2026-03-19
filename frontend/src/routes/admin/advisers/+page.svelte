<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import Notification from '$lib/components/Notification.svelte';

  /** @type {Array<any>} */
  let advisers = $state([]);
  let isLoading = $state(true);
  let newAdviser = $state({ full_name: '', email: '', password: '', department: '' });
  let isAdding = $state(false);

  /** @type {{ text: string, type: 'info' | 'success' | 'error' }} */
  let notification = $state({ text: '', type: 'info' });

  onMount(async () => { await loadAdvisers(); });

  async function loadAdvisers() {
    try {
      isLoading = true;
      const res = await adminApi.getAdvisers();
      advisers = res.data ?? [];
    } catch (err) { console.error('Failed to load advisers:', err); }
    finally { isLoading = false; }
  }

  function notify(text = '', type = /** @type {'info' | 'success' | 'error'} */ ('info')) {
    notification = { text, type };
    setTimeout(() => (notification = { text: '', type: 'info' }), 3500);
  }

  async function handleAdd(e) {
    e.preventDefault();
    if (!newAdviser.email || !newAdviser.password || !newAdviser.full_name) {
      notify('All fields are required.', 'error'); return;
    }
    isAdding = true;
    try {
      await adminApi.createAdviser(newAdviser);
      newAdviser = { email: '', password: '', full_name: '', department: '' };
      notify('Adviser account created', 'success');
      await loadAdvisers();
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to create adviser', 'error'); }
    finally { isAdding = false; }
  }

  async function deleteAdviser(id) {
    if (!confirm('Delete this adviser account?')) return;
    try {
      await adminApi.deleteAdviser(id);
      advisers = advisers.filter(a => a.id !== id);
      notify('Adviser account removed', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to delete adviser', 'error'); }
  }
</script>

<svelte:head>
  <title>Advisers | UniVote Admin</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">
  <div>
    <p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Admin</p>
    <h1 class="text-2xl font-semibold text-stone-900">Advisers</h1>
    <p class="text-stone-500 text-sm mt-0.5">Create and manage adviser accounts.</p>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
    <!-- Add Form -->
    <div class="bg-white rounded-2xl border border-stone-200 p-6 h-fit">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
          <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
        </div>
        <h2 class="text-sm font-semibold text-stone-900">New Adviser</h2>
      </div>
      <form onsubmit={handleAdd} class="space-y-4">
        <div>
          <label for="adviser_full_name" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Full Name</label>
          <input id="adviser_full_name" bind:value={newAdviser.full_name} placeholder="e.g. Prof. Jane Doe" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
        </div>
        <div>
          <label for="adviser_email" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Email Address</label>
          <input id="adviser_email" type="email" bind:value={newAdviser.email} placeholder="jane.doe@univote.edu" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
        </div>
        <div>
          <label for="adviser_password" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Password</label>
          <input id="adviser_password" type="password" bind:value={newAdviser.password} placeholder="••••••••" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
        </div>
        <div>
          <label for="adviser_dept" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Department (Optional)</label>
          <input id="adviser_dept" bind:value={newAdviser.department} placeholder="e.g. CITE" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
        </div>
        <button type="submit" disabled={isAdding} class="w-full bg-stone-900 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-800 disabled:opacity-50 transition-all">
          {isAdding ? 'Creating...' : 'Create Adviser Account'}
        </button>
      </form>
    </div>

    <!-- Adviser List -->
    <div class="lg:col-span-2 bg-white rounded-2xl border border-stone-200 p-6 overflow-hidden">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
          <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
        </div>
        <h2 class="text-sm font-semibold text-stone-900">Manage Advisers <span class="text-stone-400 font-normal">({advisers.length})</span></h2>
      </div>
      <div class="space-y-3 overflow-y-auto max-h-[500px] pr-2 scrollbar-hide">
        {#if isLoading}
          <div class="py-12 flex items-center justify-center text-stone-400 text-sm animate-pulse">Loading advisers...</div>
        {:else if advisers.length === 0}
          <div class="py-12 flex flex-col items-center justify-center border-2 border-dashed border-stone-100 rounded-xl text-stone-400 text-sm italic">No adviser accounts yet.</div>
        {:else}
          {#each advisers as adviser}
            <div class="flex items-center justify-between p-4 bg-stone-50 rounded-xl border border-stone-100 hover:border-stone-200 transition-all group">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-full bg-stone-200 flex items-center justify-center text-stone-600 font-bold text-xs uppercase">
                  {adviser.full_name?.charAt(0) || 'A'}
                </div>
                <div>
                  <p class="font-semibold text-stone-900 text-sm">{adviser.full_name}</p>
                  <p class="text-[10px] text-stone-400 font-medium tracking-tight mt-0.5">{adviser.email} {adviser.department ? `• ${adviser.department}` : ''}</p>
                </div>
              </div>
              <button onclick={() => deleteAdviser(adviser.id)} class="p-2.5 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all opacity-0 group-hover:opacity-100" title="Delete Adviser">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
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
