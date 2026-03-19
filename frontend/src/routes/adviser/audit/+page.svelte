x<script>
	import { onMount } from 'svelte';
	import { adviser } from '$lib/api.js';

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

<div class="p-6 sm:p-10 space-y-8 animate-in fade-in duration-500">
	<!-- Page Header -->
	<div class="flex items-center gap-4">
		<div class="h-14 w-14 bg-slate-100 rounded-2xl flex items-center justify-center text-slate-600 shadow-inner">
			<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
		</div>
		<div>
			<h1 class="text-3xl font-bold text-slate-900 tracking-tight">Audit History</h1>
			<p class="text-slate-500 mt-1 font-medium">Reviewing system activities and administrative changes.</p>
		</div>
	</div>

	<div class="bg-white border border-slate-100 rounded-3xl shadow-xl shadow-slate-200/20 overflow-hidden">
		<div class="overflow-x-auto">
			<table class="w-full text-left border-collapse">
				<thead>
					<tr class="bg-slate-50/50 border-b border-slate-100">
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Timestamp</th>
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Activity</th>
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Target</th>
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Details</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-50">
					{#if isLoading}
						{#each Array(5) as _}
							<tr class="animate-pulse">
								<td class="px-6 py-4"><div class="h-4 bg-slate-100 rounded w-32"></div></td>
								<td class="px-6 py-4"><div class="h-4 bg-slate-100 rounded w-24"></div></td>
								<td class="px-6 py-4"><div class="h-4 bg-slate-100 rounded w-20"></div></td>
								<td class="px-6 py-4"><div class="h-4 bg-slate-100 rounded w-40"></div></td>
							</tr>
						{/each}
					{:else}
						{#each logs as log}
							<tr class="hover:bg-slate-50/50 transition-colors group">
								<td class="px-6 py-4 text-xs font-medium text-slate-500">
									{formatDate(log.created_at)}
								</td>
								<td class="px-6 py-4">
									<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter bg-blue-50 text-blue-600 border border-blue-100">
										{formatAction(log.action)}
									</span>
								</td>
								<td class="px-6 py-4">
									<div class="flex flex-col">
										<span class="text-[10px] font-black uppercase tracking-tighter text-slate-400">{log.target_type || 'system'}</span>
										<span class="text-[11px] font-mono text-slate-600 truncate max-w-[100px]" title={log.target_id}>{log.target_id?.substring(0,8) || '---'}</span>
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex flex-wrap gap-2">
										{#if log.details}
											{#each Object.entries(log.details) as [key, value]}
												<span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md border border-slate-200">
													<span class="font-bold opacity-50 uppercase">{key}:</span> {value}
												</span>
											{/each}
										{:else}
											<span class="text-[10px] text-slate-300 italic">No metadata available</span>
										{/if}
									</div>
								</td>
							</tr>
						{:else}
							<tr>
								<td colspan="4" class="px-6 py-20 text-center text-slate-400 font-medium italic">No activities have been recorded in the audit history.</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
		
		<div class="p-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
			<span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Showing latest 100 entries</span>
			<button 
				onclick={loadLogs} 
				class="btn-link text-[10px] uppercase tracking-widest"
			>
				Refresh Feed
			</button>
		</div>
	</div>
</div>
