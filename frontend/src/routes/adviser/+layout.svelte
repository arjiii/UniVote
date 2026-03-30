<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authSession } from '$lib/stores/auth.js';
	import { setTheme } from '$lib/stores/theme.js';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import { fly } from 'svelte/transition';

	/** @type {{ children: import('svelte').Snippet }} */
	let { children } = $props();
	let isChecking = $state(true);

	onMount(() => {
		const unsub = authSession.subscribe((session) => {
			if (!session) {
				goto('/login', { replaceState: true });
			} else if (session.role === 'admin') {
				goto('/admin', { replaceState: true });
			} else if (session.role === 'adviser') {
				// Adviser dashboard: enforce dark theme for data-dense environment
				setTheme('dark');
				isChecking = false;
			} else {
				goto('/login', { replaceState: true });
			}
		});

		return unsub;
	});
</script>

{#if !isChecking}
	<Sidebar role="adviser" student_info={$authSession}>
		<div
			style="display:flex;justify-content:flex-end;margin-bottom:1.5rem;"
			in:fly={{ y: -10, duration: 400 }}
		></div>
		{@render children()}
	</Sidebar>
{:else}
	<div class="flex min-h-screen items-center justify-center bg-surface-main">
		<div
			class="h-8 w-8 animate-spin rounded-full border-4 border-fuchsia-500/30 border-t-fuchsia-500"
		></div>
	</div>
{/if}
