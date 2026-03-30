<script>
	import { onMount } from 'svelte';
	import { admin as adminApi } from '$lib/api.js';

	/** @type {Array<any>} */
	let auditLogs = $state([]);
	let isLoading = $state(true);
	let pageHistory = $state([/** @type {string | null} */ (null)]);
	let currentPage = $state(0);
	let nextPageToken = $state(/** @type {string | null} */ (null));
	let searchQuery = $state('');

	onMount(async () => {
		await loadLogs();
	});

	/** @param {string | null} token */
	async function loadLogs(token = null) {
		try {
			isLoading = true;
			const res = await adminApi.getAuditLog(15, token);
			auditLogs = res.data ?? [];
			nextPageToken = res.next_page_token ?? null;
		} catch (err) {
			console.error('Failed to load audit log:', err);
		} finally {
			isLoading = false;
		}
	}

	async function goNext() {
		if (!nextPageToken || isLoading) return;
		pageHistory.push(nextPageToken);
		currentPage++;
		await loadLogs(nextPageToken);
	}

	async function goPrev() {
		if (currentPage === 0 || isLoading) return;
		currentPage--;
		pageHistory.pop();
		const prevToken = pageHistory[currentPage];
		await loadLogs(prevToken);
	}

	const filteredLogs = $derived(
		searchQuery
			? auditLogs.filter(
					(log) =>
						log.action?.toLowerCase().includes(searchQuery.toLowerCase()) ||
						log.target_type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
						log.actor_role?.toLowerCase().includes(searchQuery.toLowerCase())
				)
			: auditLogs
	);
</script>

<svelte:head><title>Audit Logs | UniVote Admin</title></svelte:head>

<div class="dash">
	<div class="dash-header">
		<div>
			<p class="dash-eyebrow"><span class="prefix">Pages /</span> System Administrator</p>
			<h1 class="dash-title">Audit Logs</h1>
		</div>
		<div style="position:relative;">
			<svg
				style="position:absolute;left:0.625rem;top:50%;transform:translateY(-50%);width:1rem;height:1rem;color:var(--text-subtle);"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
				><path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
				/></svg
			>
			<input
				bind:value={searchQuery}
				placeholder="Filter logs…"
				class="input-base btn-sm"
				style="padding-left:2rem;width:240px;"
			/>
		</div>
	</div>

	<!-- Log Table -->
	<div class="admin-card" style="overflow:hidden;">
		<div style="padding:0.75rem 1rem;border-bottom:1px solid var(--border-main);">
			<p class="section-label">
				Listing operational history
			</p>
		</div>

		{#if isLoading}
			<div style="padding:1.5rem;display:flex;flex-direction:column;gap:0.5rem;">
				{#each Array(5) as _}
					<div class="skeleton" style="height:3rem;"></div>
				{/each}
			</div>
		{:else if filteredLogs.length === 0}
			<div class="empty-state">
				{searchQuery ? 'No logs match your filter.' : 'No protocol data recorded.'}
			</div>
		{:else}
			<div style="overflow-x:auto;">
				<table class="data-table" style="width:100%;text-align:left;border-collapse:collapse;">
					<thead>
						<tr style="border-bottom:1px solid var(--border-main);">
							<th style="padding:1rem;font-size:0.6875rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;">Timestamp</th>
							<th style="padding:1rem;font-size:0.6875rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;">Event</th>
							<th style="padding:1rem;font-size:0.6875rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;">Role</th>
							<th style="padding:1rem;font-size:0.6875rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;">Context</th>
							<th style="padding:1rem;font-size:0.6875rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;text-align:right;">Status</th>
						</tr>
					</thead>
					<tbody>
						{#each filteredLogs as log (log.id || Math.random())}
							<tr style="border-bottom:1px solid var(--border-subtle);">
								<td style="padding:1rem;font-size:0.8125rem;color:var(--text-subtle);white-space:nowrap;">
									<span style="font-family:monospace;font-weight:600;color:var(--text-main);">
										{new Date(log.created_at).toLocaleTimeString()}
									</span>
									<div style="font-size:0.6875rem;">{new Date(log.created_at).toLocaleDateString()}</div>
								</td>
								<td style="padding:1rem;">
									<span style="font-size:0.75rem;font-weight:700;color:var(--brand-primary);background:var(--brand-glow);padding:0.25rem 0.5rem;border-radius:4px;">
										{log.action}
									</span>
								</td>
								<td style="padding:1rem;">
									<span class="pill pill-dot {log.actor_role === 'admin' ? 'pill-warning' : 'pill-info'}">
										{log.actor_role} Node
									</span>
								</td>
								<td style="padding:1rem;max-width:300px;">
									<div style="font-size:0.8125rem;font-weight:600;color:var(--text-main);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
										{log.target_type ? `Target: ${log.target_type}` : 'System Routine'}
									</div>
								</td>
								<td style="padding:1rem;text-align:right;">
									<span style="font-size:0.75rem;font-weight:700;color:var(--status-success-fg);">OK</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}

		<div style="padding:1rem;display:flex;align-items:center;justify-content:space-between;border-top:1px solid var(--border-main);">
			<button onclick={goPrev} disabled={currentPage === 0 || isLoading} class="btn-secondary btn-sm">Previous</button>
			<span style="font-size:0.75rem;font-weight:600;color:var(--text-muted);">Page {currentPage + 1}</span>
			<button onclick={goNext} disabled={!nextPageToken || isLoading} class="btn-primary btn-sm">Next</button>
		</div>
	</div>
</div>
