<script>
	import { onMount } from 'svelte';
	import { admin, adviser } from '$lib/api.js';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import { selectedElectionId } from '$lib/stores/election.js';

	/** @type {any[]} */
	let elections = $state([]);
	/** @type {any[]} */
	let partylists = $state([]);

	let newPartylist = $state('');
	let editingPartylistId = $state(/** @type {string | null} */ (null));
	let editingPartylistName = $state('');
	
	let isSubmitting = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');

	async function loadElections() {
		try {
			const res = await admin.getElections();
			elections = res.data || [];
		} catch (err) { console.error('Failed to load elections:', err); }
	}

	async function loadPartylists() {
		if (!$selectedElectionId) return;
		try {
			const res = await adviser.getPartylists($selectedElectionId);
			partylists = res.data || [];
		} catch (err) { console.error('Failed to load partylists:', err); }
	}

	onMount(async () => {
		await loadElections();
		if ($selectedElectionId) await loadPartylists();
	});

	$effect(() => { if ($selectedElectionId) { loadPartylists(); } });

	const selectedElection = $derived(() => elections.find(/** @param {any} e */ e => e.id === $selectedElectionId));
	const isModifiable = $derived(() => selectedElection()?.status === 'upcoming');

	/** @param {SubmitEvent} e */
	async function handleAddPartylist(e) {
		e.preventDefault();
		if (!newPartylist || !$selectedElectionId) return;
		if (!isModifiable()) { errorMessage = 'Cannot add partylist to an active/completed election.'; return; }
		isSubmitting = true;
		errorMessage = ''; successMessage = '';
		try {
			await adviser.createPartylist($selectedElectionId, newPartylist);
			newPartylist = '';
			successMessage = 'Partylist added successfully!';
			await loadPartylists();
		} catch (/** @type {any} */ err) {
			errorMessage = err.message || 'Failed to add partylist.';
		} finally {
			isSubmitting = false;
		}
	}

	/** @param {string} id */
	async function handleDeletePartylist(id) {
		if (!isModifiable()) { errorMessage = 'Cannot delete from an active/completed election.'; return; }
		if (!confirm('Are you sure? Deleting this partylist will also DELETE all candidates associated with it.')) return;
		try {
			await adviser.deletePartylist(id);
			successMessage = 'Partylist and its candidates deleted.';
			await loadPartylists();
		} catch (/** @type {any} */ err) {
			errorMessage = err.message || 'Failed to delete partylist.';
		}
	}

	function startEditPartylist(/** @type {any} */ party) {
		if (!isModifiable()) { errorMessage = 'Cannot edit an active/completed election.'; return; }
		editingPartylistId = party.id;
		editingPartylistName = party.name;
	}

	async function handleUpdatePartylist() {
		if (!editingPartylistId || !editingPartylistName) return;
		try {
			await adviser.updatePartylist(editingPartylistId, editingPartylistName);
			editingPartylistId = null;
			successMessage = 'Partylist updated.';
			await loadPartylists();
		} catch (/** @type {any} */ err) {
			errorMessage = err.message || 'Failed to update partylist.';
		}
	}
</script>

<svelte:head>
	<title>Partylist Configuration | UniVote</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">
	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Adviser</p>
			<h1 class="text-2xl font-semibold text-stone-900">Partylists</h1>
			<p class="text-stone-500 text-sm mt-0.5">Configure political organizations for the selected election.</p>
		</div>

		<div class="flex items-center gap-3 bg-white border border-stone-200 rounded-xl px-4 py-2.5 w-fit">
			<label for="election-select" class="text-[10px] font-semibold text-stone-400 uppercase tracking-widest whitespace-nowrap">Election</label>
			<select 
				id="election-select"
				bind:value={$selectedElectionId}
				class="bg-transparent border-none text-sm font-semibold text-stone-900 focus:outline-none cursor-pointer min-w-[180px]"
			>
				<option value="" disabled>Select election</option>
				{#each elections as election}
					<option value={election.id}>{election.name}</option>
				{/each}
			</select>
		</div>
	</div>

	{#if !$selectedElectionId}
		<div class="flex flex-col items-center justify-center py-24 text-center border-2 border-dashed border-stone-200 rounded-2xl">
			<div class="w-14 h-14 bg-stone-100 rounded-2xl flex items-center justify-center mb-4">
				<svg class="w-7 h-7 text-stone-400" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
			</div>
			<h2 class="font-semibold text-stone-900 mb-1">No Election Selected</h2>
			<p class="text-stone-400 text-sm max-w-xs">Select an election from the dropdown above to manage partylists.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
			<!-- Form -->
			<div class="lg:col-span-4">
				<div class="bg-white rounded-2xl border border-stone-200 p-6 sticky top-6">
					<div class="flex items-center gap-3 mb-5">
						<div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
							<svg class="w-4 h-4 text-stone-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
						</div>
						<h2 class="text-sm font-semibold text-stone-900">Add Partylist</h2>
					</div>

					<form onsubmit={handleAddPartylist} class="space-y-4">
						<div>
							<label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5" for="party-name">Name</label>
							<input id="party-name" type="text" bind:value={newPartylist} placeholder="e.g. Student Forward" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 focus:ring-[3px] focus:ring-stone-900/[0.06] transition-all"/>
						</div>

						{#if errorMessage}
							<div class="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-semibold flex items-center gap-2">
								<svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
								{errorMessage}
							</div>
						{/if}

						{#if successMessage}
							<div class="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold flex items-center gap-2">
								<svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
								{successMessage}
							</div>
						{/if}

						<button type="submit" disabled={isSubmitting || !isModifiable()} class="w-full bg-stone-900 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-800 active:scale-[0.99] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
							{#if isSubmitting} <LoadingSpinner /> Adding... {:else} Save Partylist {/if}
						</button>
					</form>
				</div>
			</div>

			<!-- List -->
			<div class="lg:col-span-8 space-y-5">
				<div class="flex items-center justify-between">
					<h2 class="text-sm font-semibold text-stone-900">Organizations</h2>
					<span class="text-xs font-semibold text-stone-400 bg-stone-100 px-3 py-1 rounded-lg">{partylists.length} registered</span>
				</div>

				{#if partylists.length === 0}
					<div class="flex flex-col items-center justify-center py-20 text-center border-2 border-dashed border-stone-200 rounded-2xl">
						<div class="w-12 h-12 bg-stone-100 rounded-2xl flex items-center justify-center mb-3">
							<svg class="w-6 h-6 text-stone-300" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
						</div>
						<p class="font-semibold text-stone-600 text-sm">No partylists yet</p>
					</div>
				{:else}
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
						{#each partylists as party}
							<div class="group bg-white rounded-2xl border border-stone-200 p-5 hover:border-stone-400 transition-all relative">
								{#if editingPartylistId === party.id}
									<div class="space-y-3">
										<input 
											type="text" 
											bind:value={editingPartylistName}
											class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2 text-sm font-semibold focus:border-stone-900 outline-none"
											onkeydown={(e) => e.key === 'Enter' && handleUpdatePartylist()}
										/>
										<div class="flex gap-2">
											<button onclick={handleUpdatePartylist} class="flex-1 bg-stone-900 text-white rounded-lg py-1.5 text-xs font-semibold">Save</button>
											<button onclick={() => editingPartylistId = null} class="flex-1 bg-stone-100 text-stone-600 rounded-lg py-1.5 text-xs font-semibold">Cancel</button>
										</div>
									</div>
								{:else}
									<div class="flex items-center justify-between mb-3">
										<div class="w-8 h-8 bg-stone-100 rounded-lg flex items-center justify-center font-bold text-stone-600 text-xs">
											{party.name.substring(0,1).toUpperCase()}
										</div>
										<div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all">
											<button onclick={() => startEditPartylist(party)} class="p-1.5 text-stone-400 hover:text-stone-900 hover:bg-stone-50 rounded-lg transition-all" title="Rename"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg></button>
											<button onclick={() => handleDeletePartylist(party.id)} class="p-1.5 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all" title="Delete"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></button>
										</div>
									</div>
									<h3 class="font-semibold text-stone-900 truncate">{party.name}</h3>
									<p class="text-[10px] font-mono text-stone-400 mt-1">ID: {party.id.substring(0,8)}</p>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

