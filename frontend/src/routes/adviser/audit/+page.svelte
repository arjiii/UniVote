<script>
	import { onMount } from 'svelte';
	import { adviser } from '$lib/api.js';
	import GlassCard from '$lib/components/GlassCard.svelte';
	import { fly, fade } from 'svelte/transition';

	/** @type {any[]} */
	let logs = $state([]);
	let isLoading = $state(true);

	async function loadLogs() {
		try {
			const res = await adviser.getAuditLog(100);
			logs = res.data || [];
		} catch (err) {
			console.error('Failed to load audit logs:', err);
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadLogs();
	});

	function formatAction(/** @type {string} */ action) {
		return action.replace(/_/g, ' ').toLowerCase();
	}

	function formatDate(/** @type {string} */ dateStr) {
		return new Date(dateStr).toLocaleString();
	}
</script>

<svelte:head>
	<title>System Audit Logs | UniVote</title>
</svelte:head>

<GlassCard
	title="Operational History"
	subtitle="Protocol Logs & Activity Ledger"
>
	{#snippet headerExtra()}
		<button 
			onclick={loadLogs} 
			class="btn-primary mt-4 lg:mt-0 px-6 py-3 rounded-2xl text-[10px] uppercase shadow-xl hover:scale-[1.02] active:scale-95 transition-all"
		>
			Refresh Protocol
		</button>
	{/snippet}

	<div class="bg-surface-elevated border border-line-subtle rounded-[2.5rem] p-8" in:fly={{ y: 20, duration: 800 }}>
		<div class="overflow-x-auto scrollbar-hide">
			<table class="w-full text-left border-collapse min-w-[800px]">
				<thead>
					<tr class="border-b border-line-main">
						<th class="px-6 py-6 text-[9px] font-black uppercase tracking-[0.2em] text-content-muted">Stardate / Time</th>
						<th class="px-6 py-6 text-[9px] font-black uppercase tracking-[0.2em] text-content-muted">Event</th>
						<th class="px-6 py-6 text-[9px] font-black uppercase tracking-[0.2em] text-content-muted">Subject</th>
						<th class="px-6 py-6 text-[9px] font-black uppercase tracking-[0.2em] text-content-muted">Metadata</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-line-subtle">
					{#if isLoading}
						{#each Array(6) as _}
							<tr class="animate-pulse">
								<td class="px-6 py-6"><div class="h-3 bg-surface-main rounded-full w-32 border border-line-main"></div></td>
								<td class="px-6 py-6"><div class="h-3 bg-surface-main rounded-full w-24 border border-line-main"></div></td>
								<td class="px-6 py-6"><div class="h-3 bg-surface-main rounded-full w-20 border border-line-main"></div></td>
								<td class="px-6 py-6"><div class="h-3 bg-surface-main rounded-full w-40 border border-line-main"></div></td>
							</tr>
						{/each}
					{:else}
						{#each logs as log}
							<tr class="hover:bg-surface-hover transition-all group border-transparent border-l-4 hover:border-l-content-main">
								<td class="px-6 py-6">
									<div class="flex flex-col">
										<span class="text-[10px] font-black text-content-main uppercase tracking-tight">{new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
										<span class="text-[8px] font-black text-content-subtle uppercase tracking-widest mt-1">{new Date(log.created_at).toLocaleDateString()}</span>
									</div>
								</td>
								<td class="px-6 py-6">
									<span class="inline-flex items-center px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest bg-content-main text-surface-main">
										{formatAction(log.action)}
									</span>
								</td>
								<td class="px-6 py-6">
									<div class="flex flex-col">
										<span class="text-[9px] font-black uppercase tracking-widest text-content-muted">{log.target_type || 'CORE'}</span>
										<span class="text-[10px] font-mono text-content-main tracking-widest mt-0.5">{log.target_id?.substring(0,8) || 'SYSTEM'}</span>
									</div>
								</td>
								<td class="px-6 py-6">
									<div class="flex flex-wrap gap-2">
										{#if log.details}
											{#each Object.entries(log.details) as [key, value]}
												<span class="text-[9px] bg-surface-main text-content-main px-2.5 py-1 rounded-md border border-line-main font-black uppercase tracking-tight hover:border-content-main transition-colors cursor-default">
													<span class="text-content-muted">{key}:</span> {value}
												</span>
											{/each}
										{:else}
											<span class="text-[9px] text-content-subtle uppercase tracking-[0.2em] italic">No Protocol Meta</span>
										{/if}
									</div>
								</td>
							</tr>
						{:else}
							<tr>
								<td colspan="4" class="px-6 py-32 text-center">
									<p class="text-[10px] font-black text-content-subtle uppercase tracking-[0.3em]">Protocol Log Vacant · Integrity Confirmed</p>
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
		
		<div class="px-8 py-6 flex items-center justify-between border-t border-line-main">
			<span class="text-[9px] font-black text-content-subtle uppercase tracking-[0.2em]">Telemetry data · Latest 100 clusters indexed</span>
		</div>
	</div>
</GlassCard>
