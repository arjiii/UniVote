<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth as authApi } from '$lib/api.js';
  import { authSession } from '$lib/stores/auth.js';
  import { theme, toggleTheme } from '$lib/stores/theme.js';

  onMount(() => {
    if ($authSession) goto($authSession.role === 'admin' ? '/admin' : '/adviser');
  });

  let id = $state('');
  let password = $state('');
  let showPassword = $state(false);
  let isSubmitting = $state(false);
  let errorMessage = $state('');

  async function handleLogin(/** @type {SubmitEvent} */ e) {
    e.preventDefault();
    if (!id || !password) { errorMessage = 'Please enter both ID and password.'; return; }
    isSubmitting = true;
    errorMessage = '';
    try {
      const data = await authApi.login(id, password);
      authSession.login(data);
      goto(data.role === 'admin' ? '/admin' : '/adviser');
    } catch (/** @type {any} */ err) {
      errorMessage = err.message ?? 'Sign in failed. Please check your credentials.';
    } finally { isSubmitting = false; }
  }
</script>

<svelte:head><title>Sign In | UniVote</title></svelte:head>

<div class="login-page" class:dark={$theme === 'dark'}>

  <!-- Topbar -->
  <nav class="login-topbar">
    <div style="display:flex;align-items:center;gap:0.5rem;">
      <button onclick={toggleTheme} class="login-logo" title="Toggle theme">U</button>
      <span style="font-size:0.9375rem;font-weight:700;color:var(--text-main);">UniVote</span>
    </div>
    <a href="/" style="font-size:0.75rem;color:var(--text-subtle);text-decoration:none;display:flex;align-items:center;gap:0.25rem;">
      <svg style="width:0.875rem;height:0.875rem;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
      Back to home
    </a>
  </nav>

  <!-- Form wrapper -->
  <div class="login-body">
    <div class="login-card admin-card">

      <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:1.25rem;font-weight:700;color:var(--text-main);">Staff Sign In</h1>
        <p style="font-size:0.8125rem;color:var(--text-muted);margin-top:0.25rem;">Enter your credentials to access the administration portal.</p>
      </div>

      <form onsubmit={handleLogin} style="display:flex;flex-direction:column;gap:1rem;">
        <div>
          <label class="field-label" for="id">Staff / Employee ID</label>
          <input
            type="text"
            id="id"
            class="input-base"
            bind:value={id}
            placeholder="e.g. 2024-001"
            autocomplete="username"
            required
          />
        </div>

        <div>
          <label class="field-label" for="password">Password</label>
          <div style="position:relative;">
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              class="input-base"
              bind:value={password}
              placeholder="••••••••"
              autocomplete="current-password"
              style="padding-right:2.5rem;"
              required
            />
            <button
              type="button"
              onclick={() => showPassword = !showPassword}
              class="btn-icon"
              style="position:absolute;right:0.375rem;top:50%;transform:translateY(-50%);"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {#if showPassword}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/></svg>
              {:else}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              {/if}
            </button>
          </div>
        </div>

        {#if errorMessage}
          <div style="padding:0.625rem 0.75rem;background-color:var(--status-danger-bg);border:1px solid rgba(220,38,38,0.2);border-radius:6px;font-size:0.75rem;color:var(--status-danger-fg);font-weight:500;">
            {errorMessage}
          </div>
        {/if}

        <button type="submit" disabled={isSubmitting} class="btn-primary" style="width:100%;margin-top:0.25rem;padding:0.625rem 1rem;font-size:0.875rem;">
          {#if isSubmitting}
            <div class="spinner" style="width:1rem;height:1rem;border-width:2px;border-top-color:#fff;"></div>
            Signing in…
          {:else}
            Sign In
          {/if}
        </button>
      </form>

      <div style="margin-top:1.25rem;padding-top:1.25rem;border-top:1px solid var(--border-main);display:flex;align-items:center;justify-content:space-between;">
        <p style="font-size:0.75rem;color:var(--text-muted);">
          No account?
          <a href="/register" style="color:var(--brand-primary);text-decoration:none;font-weight:500;">Register here</a>
        </p>
        <a href="/student/validate" style="font-size:0.75rem;color:var(--text-subtle);text-decoration:none;">Student login →</a>
      </div>
    </div>
  </div>
</div>

<style>
  :global(body) { background-color: var(--bg-main); }

  .login-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background-color: var(--bg-main);
  }
  .login-topbar {
    height: 52px;
    background-color: var(--bg-card);
    border-bottom: 1px solid var(--border-main);
    padding: 0 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
  }
  .login-logo {
    width: 28px; height: 28px;
    background-color: var(--brand-primary); color: #fff;
    border-radius: 6px; font-size: 0.75rem; font-weight: 800;
    border: none; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background-color 0.15s;
  }
  .login-logo:hover { background-color: var(--brand-primary-h); }

  .login-body {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1.5rem;
  }
  .login-card {
    width: 100%;
    max-width: 380px;
    padding: 1.75rem;
  }
</style>
