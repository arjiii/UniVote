<script>
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

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">
	<!-- Page Header -->
	<div class="flex items-center gap-4">
		<div class="h-12 w-12 bg-stone-100 dark:bg-stone-800 rounded-2xl flex items-center justify-center text-stone-600 dark:text-stone-300 shadow-inner">
			<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
		</div>
		<div>
			<p class="text-[10px] font-semibold text-stone-400 dark:text-stone-500 tracking-widest uppercase mb-1">Adviser</p>
			<h1 class="text-2xl font-semibold text-stone-900 dark:text-white">Audit History</h1>
			<p class="text-stone-500 dark:text-stone-400 text-sm mt-0.5">Reviewing system activities and administrative changes.</p>
		</div>
	</div>

	<div class="bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-700 rounded-2xl overflow-hidden">
		<div class="overflow-x-auto">
			<table class="w-full text-left border-collapse">
				<thead>
					<tr class="bg-stone-50 dark:bg-stone-800/50 border-b border-stone-100 dark:border-stone-700">
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-stone-400 dark:text-stone-500">Timestamp</th>
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-stone-400 dark:text-stone-500">Activity</th>
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-stone-400 dark:text-stone-500">Target</th>
						<th class="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-stone-400 dark:text-stone-500">Details</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-stone-50 dark:divide-stone-800">
					{#if isLoading}
						{#each Array(5) as _}
							<tr class="animate-pulse">
								<td class="px-6 py-4"><div class="h-4 bg-stone-100 dark:bg-stone-800 rounded w-32"></div></td>
								<td class="px-6 py-4"><div class="h-4 bg-stone-100 dark:bg-stone-800 rounded w-24"></div></td>
								<td class="px-6 py-4"><div class="h-4 bg-stone-100 dark:bg-stone-800 rounded w-20"></div></td>
								<td class="px-6 py-4"><div class="h-4 bg-stone-100 dark:bg-stone-800 rounded w-40"></div></td>
							</tr>
						{/each}
					{:else}
						{#each logs as log}
							<tr class="hover:bg-stone-50 dark:hover:bg-stone-800/50 transition-colors group">
								<td class="px-6 py-4 text-xs font-medium text-stone-500 dark:text-stone-400">
									{formatDate(log.created_at)}
								</td>
								<td class="px-6 py-4">
									<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-800">
										{formatAction(log.action)}
									</span>
								</td>
								<td class="px-6 py-4">
									<div class="flex flex-col">
										<span class="text-[10px] font-black uppercase tracking-tighter text-stone-400 dark:text-stone-500">{log.target_type || 'system'}</span>
										<span class="text-[11px] font-mono text-stone-600 dark:text-stone-300 truncate max-w-[100px]" title={log.target_id}>{log.target_id?.substring(0,8) || '---'}</span>
									</div>
								</td>
								<td class="px-6 py-4">
									<div class="flex flex-wrap gap-2">
										{#if log.details}
											{#each Object.entries(log.details) as [key, value]}
												<span class="text-[10px] bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 px-2 py-0.5 rounded-md border border-stone-200 dark:border-stone-700">
													<span class="font-bold opacity-50 uppercase">{key}:</span> {value}
												</span>
											{/each}
										{:else}
											<span class="text-[10px] text-stone-300 dark:text-stone-600 italic">No metadata available</span>
										{/if}
									</div>
								</td>
							</tr>
						{:else}
							<tr>
								<td colspan="4" class="px-6 py-20 text-center text-stone-400 dark:text-stone-500 font-medium italic">No activities have been recorded in the audit history.</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
		
		<div class="p-4 bg-stone-50 dark:bg-stone-800/50 border-t border-stone-100 dark:border-stone-700 flex items-center justify-between">
			<span class="text-[10px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-widest">Showing latest 100 entries</span>
			<button 
				onclick={loadLogs} 
				class="btn-link text-[10px] uppercase tracking-widest"
			>
				Refresh Feed
			</button>
		</div>
	</div>
</div>
