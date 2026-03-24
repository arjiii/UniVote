<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import Notification from '$lib/components/Notification.svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';

  /** @type {Array<any>} */
  let advisers = $state([]);
  let isLoading = $state(true);
  let newAdviser = $state({ full_name: '', email: '', password: '', department: '' });
  let isAdding = $state(false);
  let showForm = $state(false);

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

  async function handleAdd(/** @type {SubmitEvent} */ e) {
    e.preventDefault();
    if (!newAdviser.email || !newAdviser.password || !newAdviser.full_name) {
      notify('Name, email, and password are required.', 'error'); return;
    }
    isAdding = true;
    try {
      await adminApi.createAdviser(newAdviser);
      newAdviser = { email: '', password: '', full_name: '', department: '' };
      showForm = false;
      notify('Adviser account created', 'success');
      await loadAdvisers();
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to create adviser', 'error'); }
    finally { isAdding = false; }
  }

  async function deleteAdviser(/** @type {string} */ id) {
    if (!confirm('Delete this adviser account?')) return;
    try {
      await adminApi.deleteAdviser(id);
      advisers = advisers.filter(a => a.id !== id);
      notify('Adviser account removed', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to delete adviser', 'error'); }
  }
</script>

<svelte:head><title>Advisers | UniVote Admin</title></svelte:head>

<GlassCard title="Adviser Registry" subtitle="Administrator">
  {#snippet headerExtra()}
    <div style="display:flex;gap:0.5rem;align-items:center;">
      <button onclick={loadAdvisers} class="btn-secondary btn-sm">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"/></svg>
        Refresh
      </button>
      <button onclick={() => showForm = !showForm} class="btn-primary btn-sm">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
        Add Adviser
      </button>
    </div>
  {/snippet}

  <!-- Add Adviser Form -->
  {#if showForm}
    <div class="admin-card" style="padding:1.25rem;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
        <h2 style="font-size:0.875rem;font-weight:600;color:var(--text-main);">Create Adviser Account</h2>
        <button onclick={() => showForm = false} class="btn-icon">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <form onsubmit={handleAdd} style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
        <div>
          <label class="field-label" for="adviser_full_name">Full Name *</label>
          <input id="adviser_full_name" class="input-base" bind:value={newAdviser.full_name} placeholder="e.g. Prof. Jane Doe"/>
        </div>
        <div>
          <label class="field-label" for="adviser_email">Email Address *</label>
          <input id="adviser_email" type="email" class="input-base" bind:value={newAdviser.email} placeholder="jane.doe@univote.edu"/>
        </div>
        <div>
          <label class="field-label" for="adviser_password">Password *</label>
          <input id="adviser_password" type="password" class="input-base" bind:value={newAdviser.password} placeholder="••••••••"/>
        </div>
        <div>
          <label class="field-label" for="adviser_dept">Department</label>
          <input id="adviser_dept" class="input-base" bind:value={newAdviser.department} placeholder="e.g. CITE"/>
        </div>
        <div style="grid-column:1/-1;display:flex;gap:0.5rem;justify-content:flex-end;margin-top:0.25rem;">
          <button type="button" onclick={() => showForm = false} class="btn-secondary btn-sm">Cancel</button>
          <button type="submit" disabled={isAdding} class="btn-primary btn-sm">
            {isAdding ? 'Creating…' : 'Create Adviser'}
          </button>
        </div>
      </form>
    </div>
  {/if}

  <!-- Advisers Table -->
  <div class="admin-card" style="overflow:hidden;">
    <div style="padding:0.75rem 1rem;border-bottom:1px solid var(--border-main);">
      <p class="section-label">{advisers.length} active adviser account{advisers.length !== 1 ? 's' : ''}</p>
    </div>

    {#if isLoading}
      <div style="padding:1.5rem;display:flex;flex-direction:column;gap:0.5rem;">
        {#each Array(4) as _}
          <div class="skeleton" style="height:3rem;"></div>
        {/each}
      </div>
    {:else if advisers.length === 0}
      <div class="empty-state">No advisers registered. Click "Add Adviser" to create one.</div>
    {:else}
      <div style="overflow-x:auto;">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:1%;">Avatar</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Department</th>
              <th style="text-align:right;">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each advisers as adviser (adviser.id)}
              <tr>
                <td>
                  <div class="avatar-initial" style="width:32px;height:32px;">
                    {adviser.full_name?.charAt(0) || 'A'}
                  </div>
                </td>
                <td style="font-weight:600;color:var(--text-main);">{adviser.full_name}</td>
                <td style="color:var(--text-muted);">{adviser.email}</td>
                <td>
                  {#if adviser.department}
                    <span class="pill pill-neutral">{adviser.department}</span>
                  {:else}
                    <span style="color:var(--text-subtle);">—</span>
                  {/if}
                </td>
                <td style="text-align:right;">
                  <button onclick={() => deleteAdviser(adviser.id)} class="btn-icon-danger" title="Revoke access">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/></svg>
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>

</GlassCard>

<div style="position:fixed;bottom:1.5rem;right:1.5rem;z-index:110;">
  <Notification text={notification.text} type={notification.type} />
</div>
