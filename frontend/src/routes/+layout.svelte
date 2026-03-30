<script>
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { theme } from '$lib/stores/theme.js';
	import { onMount } from 'svelte';
	import PageProgressBar from '$lib/components/PageProgressBar.svelte';

	let { children } = $props();

	onMount(() => {
		const unsub = theme.subscribe((val) => {
			if (val === 'dark') {
				document.documentElement.classList.add('dark');
			} else {
				document.documentElement.classList.remove('dark');
			}
		});
		return unsub;
	});
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<PageProgressBar />

{@render children()}
