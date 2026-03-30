<script>
	import { goto } from '$app/navigation';
	import { student as studentApi } from '$lib/api.js';
	import { voterSession } from '$lib/stores/session.js';
	import { theme, toggleTheme } from '$lib/stores/theme.js';
	import GlassCard from '$lib/components/GlassCard.svelte';
	import { fade, fly } from 'svelte/transition';

	let studentId = $state('');
	let isChecking = $state(false);
	let errorMessage = $state('');
	let retrySeconds = $state(0);

	async function checkStudentId(/** @type {SubmitEvent} */ e) {
		e.preventDefault();
		if (!studentId) { errorMessage = 'Please enter your Student ID.'; return; }
		isChecking = true;
		errorMessage = '';
		try {
			const data = await studentApi.validate(studentId);
			const elections = (data.active_elections || []).map(
				/** @param {any} e */ (e) => ({ id: e.id, name: e.name, has_voted: e.has_voted })
			);
			voterSession.login({ ...data.student, access_token: data.access_token, elections });
			goto('/student');
		} catch (/** @type {any} */ err) {
			if (err.retryAfter) {
				retrySeconds = err.retryAfter;
				errorMessage = `Too many attempts. Please wait ${retrySeconds}s.`;
			} else {
				errorMessage = err.message ?? 'Error validating student ID.';
			}
		} finally { isChecking = false; }
	}

	import { onMount, onDestroy } from 'svelte';
	/** @type {any} */ let timer;
	$effect(() => {
		if (retrySeconds > 0) {
			timer = setInterval(() => { retrySeconds -= 1; }, 1000);
			return () => clearInterval(timer);
		}
	});
</script>

<svelte:head>
	<title>Student Access | UniVote</title>
</svelte:head>

<!-- Full blue background -->
<div class="auth-page">
	<!-- Decorative spheres on the blue background -->
	<div class="sphere sphere-1"></div>
	<div class="sphere sphere-2"></div>
	<div class="sphere sphere-3"></div>
	<div class="sphere sphere-4"></div>

	<!-- Floating card container -->
	<div class="auth-card">
		<!-- Left side: text on blue (transparent, shows blue bg) -->
		<div class="auth-left">
			<div class="auth-brand">
				<button onclick={toggleTheme} class="auth-logo-btn">
					<img src="/Messenger_creation_1261776042047231.jpeg" alt="UniVote Logo" class="auth-logo" />
				</button>
				<span class="auth-brand-name">UNIVOTE</span>
			</div>

			<div class="auth-hero">
				<h2 class="auth-hero-title">YOUR VOTE,<br /><span class="auth-hero-accent">YOUR VOICE.</span></h2>
				<p class="auth-hero-desc">
					ENTER YOUR STUDENT ID TO VERIFY YOUR IDENTITY AND ACCESS THE SECURE DIGITAL BALLOT.
				</p>
				<div class="auth-features">
					{#each ['YOUR VOTE IS 100% ANONYMOUS', 'ONE STUDENT, ONE VOTE', 'SEE RESULTS IN REAL TIME'] as feature}
						<div class="auth-feature-item">
							<div class="auth-feature-check">
								<svg class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="4" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
								</svg>
							</div>
							<span>{feature}</span>
						</div>
					{/each}
				</div>
			</div>

			<p class="auth-footer-text">© 2025 UNIVOTE</p>
		</div>

		<!-- Right side: white form panel -->
		<div class="auth-right">
			<!-- Accent sphere bleeding into the white area -->
			<div class="accent-sphere accent-sphere-br"></div>

			<div class="auth-form-container" in:fade={{ duration: 400 }}>
				<h1 class="form-title">STUDENT LOGIN</h1>
				<p class="form-subtitle">ENTER YOUR CREDENTIALS</p>

				<form onsubmit={checkStudentId} class="auth-form">
					<div class="auth-field">
						<label for="studentId" class="field-label">OFFICIAL STUDENT ID</label>
						<div class="input-icon-wrap">
							<svg class="input-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
							<input
								id="studentId" type="text" bind:value={studentId}
								placeholder="E.G. 2021-00123"
								class="input-base input-with-icon w-full uppercase"
								required
							/>
						</div>
						<p class="auth-hint">USE YOUR OFFICIAL SCHOOL-ISSUED STUDENT ID.</p>
					</div>

					{#if errorMessage}
						<div class="pill pill-danger w-full py-3" in:fly={{ y: 5, duration: 200 }}>
							<div class="flex items-center gap-3">
								<svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
								</svg>
								<span class="font-bold">{errorMessage}</span>
							</div>
							{#if retrySeconds > 0}
								<span class="retry-badge">{retrySeconds}S</span>
							{/if}
						</div>
					{/if}

					<button type="submit" disabled={isChecking || !studentId || retrySeconds > 0} class="auth-btn-primary">
						{#if isChecking}
							<div class="flex items-center justify-center gap-3">
								<div class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
								VALIDATING...
							</div>
						{:else}
							ENTER VOTING BOOTH
						{/if}
					</button>
				</form>

				<div class="form-divider">
					<span>OR</span>
				</div>

				<a href="/" class="auth-btn-outline">BACK TO HOME</a>
			</div>
		</div>
	</div>

	<!-- Mobile layout (stacked) -->
	<div class="auth-mobile">
		<div class="auth-mobile-header">
			<button onclick={toggleTheme} class="auth-logo-btn auth-logo-btn-mobile">
				<img src="/Messenger_creation_1261776042047231.jpeg" alt="UniVote Logo" class="auth-logo auth-logo-lg" />
			</button>
			<h1 class="auth-mobile-title">UNIVOTE</h1>
			<p class="auth-mobile-sub">STUDENT PORTAL</p>
		</div>

		<div class="auth-mobile-card">
			<h2 class="form-title">STUDENT LOGIN</h2>
			<p class="form-subtitle">ENTER YOUR CREDENTIALS</p>

			<form onsubmit={checkStudentId} class="auth-form">
				<div class="auth-field">
					<label for="studentIdMobile" class="field-label">OFFICIAL STUDENT ID</label>
					<div class="input-icon-wrap">
						<svg class="input-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" /></svg>
						<input
							id="studentIdMobile" type="text" bind:value={studentId}
							placeholder="E.G. 2021-00123"
							class="input-base input-with-icon w-full uppercase"
							required
						/>
					</div>
				</div>

				{#if errorMessage}
					<div class="pill pill-danger w-full py-3" in:fly={{ y: 5, duration: 200 }}>
						<svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
						</svg>
						<span class="font-bold">{errorMessage}</span>
					</div>
				{/if}

				<button type="submit" disabled={isChecking || !studentId || retrySeconds > 0} class="auth-btn-primary">
					{#if isChecking}
						<div class="flex items-center justify-center gap-3">
							<div class="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
							VALIDATING...
						</div>
					{:else}
						ENTER VOTING BOOTH
					{/if}
				</button>
			</form>

			<div class="form-divider"><span>OR</span></div>
			<a href="/" class="auth-btn-outline">BACK TO HOME</a>
		</div>

		<p class="auth-mobile-copyright">© 2025 UNIVOTE</p>
	</div>
</div>

<style>
	/* ====== PAGE ====== */
	.auth-page {
		position: relative;
		min-height: 100vh;
		background: linear-gradient(135deg, #0b75fe 0%, #0052cc 50%, #003d99 100%);
		overflow: hidden;
	}

	/* ====== DESKTOP CARD ====== */
	.auth-card {
		display: none;
		position: relative;
		z-index: 2;
		width: 90%;
		max-width: 1100px;
		min-height: 600px;
		margin: auto;
		border-radius: 20px;
		overflow: hidden;
		box-shadow: 0 25px 80px rgba(0, 0, 0, 0.25);
	}

	@media (min-width: 1024px) {
		.auth-page {
			display: flex;
			align-items: center;
			justify-content: center;
		}
		.auth-card { display: flex; }
		.auth-mobile { display: none !important; }
	}

	/* ====== LEFT (transparent on blue) ====== */
	.auth-left {
		width: 42%;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		padding: 2.5rem;
		position: relative;
		z-index: 1;
	}

	.auth-brand { display: flex; align-items: center; gap: 0.75rem; }
	.auth-logo-btn {
		display: flex; align-items: center; justify-content: center;
		border: none; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
		border-radius: 12px; padding: 5px; cursor: pointer;
		transition: transform 0.2s, background 0.2s; outline: none;
	}
	.auth-logo-btn:hover { transform: scale(1.08) rotate(3deg); background: rgba(255,255,255,0.25); }
	.auth-logo { width: 38px; height: 38px; border-radius: 8px; object-fit: contain; }
	.auth-logo-lg { width: 64px; height: 64px; border-radius: 14px; }
	@media (min-width: 640px) { .auth-logo-lg { width: 72px; height: 72px; } }
	.auth-brand-name { font-size: 1.1rem; font-weight: 900; color: white; letter-spacing: 0.05em; }

	.auth-hero { max-width: 300px; }
	.auth-hero-title {
		font-size: 2.75rem; font-weight: 900; line-height: 1;
		color: white; letter-spacing: -0.02em; margin-bottom: 1rem;
	}
	.auth-hero-accent { color: rgba(255,255,255,0.45); }
	.auth-hero-desc {
		font-size: 0.55rem; font-weight: 600; letter-spacing: 0.12em;
		color: rgba(255,255,255,0.55); line-height: 1.8; margin-bottom: 1.5rem;
	}

	.auth-features { display: flex; flex-direction: column; gap: 0.75rem; }
	.auth-feature-item {
		display: flex; align-items: center; gap: 0.6rem;
		font-size: 0.5rem; font-weight: 700; letter-spacing: 0.15em; color: rgba(255,255,255,0.7);
	}
	.auth-feature-check {
		width: 22px; height: 22px; border-radius: 7px;
		background: rgba(255,255,255,0.18); backdrop-filter: blur(6px);
		display: flex; align-items: center; justify-content: center;
		color: white; flex-shrink: 0;
	}

	.auth-footer-text { font-size: 0.45rem; font-weight: 700; letter-spacing: 0.25em; color: rgba(255,255,255,0.3); }

	/* ====== RIGHT (white card) ====== */
	.auth-right {
		flex: 1;
		background: var(--bg-main);
		padding: 2.5rem 3rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		position: relative;
		overflow: hidden;
		border-radius: 0 20px 20px 0;
	}

	:global(.dark) .auth-right {
		background: var(--bg-card);
	}

	.accent-sphere {
		position: absolute; border-radius: 50%; pointer-events: none; z-index: 0;
	}
	.accent-sphere-br {
		width: 160px; height: 160px;
		bottom: -50px; right: -50px;
		background: radial-gradient(circle at 35% 35%, rgba(11,117,254,0.2), rgba(0,82,204,0.5) 60%, rgba(0,50,140,0.7));
		box-shadow: inset -4px -4px 10px rgba(0,0,0,0.2);
		animation: sphereBob2 14s ease-in-out infinite;
	}

	/* ====== FORM ====== */
	.auth-form-container {
		position: relative;
		z-index: 1;
		width: 100%;
		max-width: 380px;
	}

	.form-title {
		font-size: 1.75rem; font-weight: 900; color: var(--text-main);
		letter-spacing: -0.01em; margin: 0 0 0.25rem;
	}
	.form-subtitle {
		font-size: 0.6rem; font-weight: 600; letter-spacing: 0.12em;
		color: var(--text-subtle); margin: 0 0 1.5rem;
	}

	.auth-form { display: flex; flex-direction: column; gap: 1rem; }
	.auth-field { display: flex; flex-direction: column; gap: 0.35rem; }
	.auth-hint { font-size: 0.5rem; font-weight: 600; letter-spacing: 0.05em; color: var(--text-subtle); opacity: 0.6; }

	.input-icon-wrap {
		position: relative;
	}
	.input-icon {
		position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
		width: 18px; height: 18px; color: var(--text-subtle); opacity: 0.5;
		pointer-events: none;
	}
	.input-with-icon {
		padding-left: 2.5rem !important;
	}

	.auth-btn-primary {
		width: 100%; padding: 0.875rem;
		background: linear-gradient(135deg, #1a1a2e, #16213e);
		color: white; border: none; border-radius: 10px;
		font-size: 0.7rem; font-weight: 800; letter-spacing: 0.2em;
		cursor: pointer; transition: all 0.2s ease;
		text-transform: uppercase;
	}
	.auth-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }
	.auth-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

	.form-divider {
		display: flex; align-items: center; gap: 1rem; margin: 1rem 0;
	}
	.form-divider::before, .form-divider::after {
		content: ''; flex: 1; height: 1px; background: var(--border-main);
	}
	.form-divider span {
		font-size: 0.55rem; font-weight: 700; letter-spacing: 0.15em; color: var(--text-subtle);
	}

	.auth-btn-outline {
		display: block; width: 100%; padding: 0.75rem;
		border: 1.5px solid var(--border-main); border-radius: 10px;
		background: transparent; color: var(--text-main);
		font-size: 0.65rem; font-weight: 800; letter-spacing: 0.15em;
		text-align: center; text-decoration: none; text-transform: uppercase;
		cursor: pointer; transition: all 0.2s ease;
	}
	.auth-btn-outline:hover { border-color: var(--brand-primary); color: var(--brand-primary); }

	.retry-badge {
		flex-shrink: 0; border-radius: 4px; background: var(--status-danger-fg);
		padding: 2px 8px; font-family: monospace; font-size: 0.6rem; font-weight: 900; color: white;
	}

	/* ====== SPHERES ====== */
	.sphere { position: absolute; border-radius: 50%; z-index: 1; }
	.sphere-1 {
		width: 320px; height: 320px;
		bottom: -80px; left: -60px;
		background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.15), rgba(0,82,204,0.5) 50%, rgba(0,40,120,0.8));
		box-shadow: inset -10px -10px 30px rgba(0,0,0,0.3), 0 25px 80px rgba(0,0,0,0.15);
		animation: sphereBob1 10s ease-in-out infinite;
	}
	.sphere-2 {
		width: 140px; height: 140px;
		top: 40px; right: 8%;
		background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2), rgba(0,100,230,0.4) 60%, rgba(0,60,160,0.6));
		box-shadow: inset -5px -5px 15px rgba(0,0,0,0.2), 0 15px 40px rgba(0,0,0,0.1);
		animation: sphereBob2 12s ease-in-out infinite;
	}
	.sphere-3 {
		width: 70px; height: 70px;
		top: 60%; left: 35%;
		background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.25), rgba(0,120,255,0.3) 70%);
		box-shadow: inset -3px -3px 8px rgba(0,0,0,0.15);
		animation: sphereBob3 14s ease-in-out infinite;
	}
	.sphere-4 {
		width: 45px; height: 45px;
		top: 20%; left: 30%;
		background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.3), rgba(0,100,220,0.25) 70%);
		animation: sphereBob2 16s ease-in-out infinite reverse;
	}

	@keyframes sphereBob1 { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(15px, -25px); } }
	@keyframes sphereBob2 { 0%, 100% { transform: translate(0, 0) scale(1); } 50% { transform: translate(-12px, 18px) scale(1.06); } }
	@keyframes sphereBob3 { 0%, 100% { transform: translate(0, 0); } 33% { transform: translate(12px, -12px); } 66% { transform: translate(-8px, 10px); } }

	/* ====== MOBILE ====== */
	.auth-mobile {
		display: flex; flex-direction: column; align-items: center;
		min-height: 100vh; padding: 2rem 1.25rem; z-index: 2; position: relative;
	}

	@media (min-width: 1024px) {
		.auth-mobile { display: none; }
	}

	.auth-mobile-header {
		display: flex; flex-direction: column; align-items: center;
		gap: 0.5rem; margin-bottom: 1.5rem;
	}
	.auth-logo-btn-mobile { background: rgba(255,255,255,0.2); }
	.auth-mobile-title { font-size: 1.75rem; font-weight: 900; color: white; letter-spacing: 0.05em; }
	.auth-mobile-sub { font-size: 0.6rem; font-weight: 700; letter-spacing: 0.2em; color: rgba(255,255,255,0.6); }

	.auth-mobile-card {
		width: 100%; max-width: 420px;
		background: var(--bg-main); border-radius: 20px;
		padding: 1.75rem; box-shadow: 0 20px 60px rgba(0,0,0,0.2);
	}

	:global(.dark) .auth-mobile-card {
		background: var(--bg-card);
	}

	.auth-mobile-copyright {
		margin-top: auto; padding-top: 1.5rem;
		font-size: 0.5rem; font-weight: 700; letter-spacing: 0.2em; color: rgba(255,255,255,0.3);
	}
</style>
