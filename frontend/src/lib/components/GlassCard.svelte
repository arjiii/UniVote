<script>
  /** @type {{ children: import('svelte').Snippet, headerExtra?: import('svelte').Snippet, title?: string, subtitle?: string }} */
  let { children, headerExtra, title, subtitle } = $props();
</script>

<div class="page-shell">
  <div class="page-content">

    <!-- Page Header -->
    {#if title}
      <div class="page-header">
        <div>
          {#if subtitle}
            <p class="page-subtitle">{subtitle}</p>
          {/if}
          <h1 class="page-title" style="margin-top: 0.25rem;">{title}</h1>
        </div>
        {#if headerExtra}
          <div class="page-header-extra">
            {@render headerExtra()}
          </div>
        {/if}
      </div>
    {/if}

    <!-- Content -->
    <div class="page-body" style={title ? 'margin-top: 1.25rem;' : ''}>
      {@render children()}
    </div>

  </div>
</div>

<style>
  .page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-main);
  }
  .page-header-extra {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
  }
  .page-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
</style>
