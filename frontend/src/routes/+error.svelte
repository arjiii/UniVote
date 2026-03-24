<script>
	import { page } from '$app/state';
	import favicon from '$lib/assets/favicon.svg';

	/** @type {Record<number, { title: string, subtitle: string, icon: string }>} */
	const errorDetails = {
		404: {
			title: 'Resource Segregation Error',
			subtitle: 'The requested ballot or path does not exist in the current voter registry.',
			icon: 'M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
		},
		500: {
			title: 'Core Engine Failure',
			subtitle: 'The tally mechanism encountered an unexpected exception during processing.',
			icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.268 16c-.77 1.333.192 3 1.732 3z'
		}
	};

	let status = $derived(page.status);
	let message = $derived(page.error?.message || 'Something went wrong on our end.');
	
	let details = $derived(errorDetails[status] || {
		title: 'System Discrepancy',
		subtitle: message,
		icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
	});
</script>

<svelte:head>
	<title>{status} | UniVote Error</title>
</svelte:head>

<div class="min-h-screen bg-surface-main flex items-center justify-center p-6 font-sans">
	<div class="max-w-md w-full text-center space-y-8 animate-in fade-in zoom-in duration-700">
		<!-- Brand Header -->
		<div class="flex justify-center mb-8">
			<img src={favicon} alt="UniVote Logo" class="h-12 w-12 grayscale opacity-50" />
		</div>

		<!-- Main Error Content -->
		<div class="bg-surface-card rounded-[40px] p-12 shadow-2xl border border-line-subtle relative overflow-hidden group">
			<!-- Animated Background Element -->
			<div class="absolute -top-24 -right-24 w-48 h-48 bg-surface-main rounded-full group-hover:scale-110 transition-transform duration-700"></div>
			
			<div class="relative">
				<!-- Status Badge -->
				<div class="inline-flex items-center px-4 py-1.5 rounded-full bg-content-main text-surface-main text-[10px] font-black uppercase tracking-widest mb-6 shadow-lg">
					Error Protocol {status}
				</div>

				<!-- Icon -->
				<div class="mb-6 flex justify-center">
					<div class="h-20 w-20 bg-surface-elevated border border-line-main rounded-3xl flex items-center justify-center text-content-subtle group-hover:text-content-muted transition-colors duration-500">
						<svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d={details.icon}></path>
						</svg>
					</div>
				</div>

				<h1 class="text-3xl font-bold text-content-main tracking-tight mb-3">
					{details.title}
				</h1>
				
				<p class="text-content-muted font-medium leading-relaxed mb-8">
					{details.subtitle}
				</p>

				<div class="flex flex-col gap-3">
					<a 
						href="/" 
						class="w-full btn-primary !py-4 !rounded-2xl shadow-xl flex items-center justify-center gap-2 group/btn"
					>
						<span>Return to Dashboard</span>
						<svg class="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
						</svg>
					</a>
					
					<button 
						onclick={() => window.location.reload()}
						class="btn-secondary w-full !py-4 !rounded-2xl"
					>
						Reconnect System
					</button>
				</div>
			</div>
		</div>

		<!-- System Footer -->
		<div class="pt-4">
			<p class="text-[10px] font-black uppercase tracking-widest text-content-subtle">
				UniVote Automated Recovery Service • v0.0.1
			</p>
		</div>
	</div>
</div>

<style>
	:global(body) {
		background-color: var(--bg-main);
		overflow: hidden;
	}
</style>
