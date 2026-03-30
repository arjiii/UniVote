<script>
	import { voterSession } from '$lib/stores/session.js';
	import { goto } from '$app/navigation';

	/** @type {{ initials?: string }} */
	let { initials = '??' } = $props();

	function handleLogout() {
		voterSession.logout();
		goto('/');
	}
</script>

<header class="topbar">
	<div class="topbar-logo">
		<img src="/Messenger_creation_1261776042047231.jpeg" alt="UniVote Logo" class="logo-img" />
		<span class="logo-text">UniVote</span>
	</div>
	<button class="topbar-logout-glass" onclick={handleLogout} aria-label="Sign Out">
		<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="power-icon">
			<path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10" />
		</svg>
	</button>
</header>

<style>
	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 14px 20px;
		background: var(--surface);
		border-bottom: 1px solid var(--border);
		position: sticky;
		top: 0;
		z-index: 150;
	}

	.topbar-logo {
		display: flex;
		align-items: center;
		gap: 9px;
	}

	.logo-img {
		width: 28px;
		height: 28px;
		object-fit: contain;
		border-radius: 6px;
		flex-shrink: 0;
	}

	.logo-text {
		font-weight: 800;
		font-size: 17px;
		letter-spacing: -0.4px;
		color: var(--text);
	}

	.topbar-logout-glass {
		width: 38px;
		height: 38px;
		border-radius: 50%;
		background: rgba(225, 29, 72, 0.06);
		border: 1.5px solid rgba(225, 29, 72, 0.12);
		display: grid;
		place-items: center;
		color: #e11d48;
		cursor: pointer;
		transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
		padding: 0;
		outline: none;
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
	}

	.topbar-logout-glass:hover {
		background: #e11d48;
		border-color: #e11d48;
		color: #fff;
		transform: scale(1.08) rotate(5deg);
		box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3);
	}

	.topbar-logout-glass:active {
		transform: scale(0.95);
	}

	.power-icon {
		width: 19px;
		height: 19px;
		stroke-width: 2.8;
	}

	@media (min-width: 768px) {
		.topbar {
			display: none;
		}
	}
</style>
