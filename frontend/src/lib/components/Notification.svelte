<script>
  /** @type {{ text?: string, type?: 'info' | 'success' | 'error' }} */
  let { text = '', type = 'info' } = $props();

  /** @type {Record<'info' | 'success' | 'error', string>} */
  const styles = {
    info:    'bg-[var(--status-info-bg)] border-[var(--status-info-fg)]/30 text-[var(--status-info-fg)]',
    success: 'bg-[var(--status-success-bg)] border-[var(--status-success-fg)]/30 text-[var(--status-success-fg)]',
    error:   'bg-[var(--status-danger-bg)] border-[var(--status-danger-fg)]/30 text-[var(--status-danger-fg)]',
  };
</script>

{#if text}
  <div
    class="fixed bottom-6 right-6 px-6 py-4 rounded-xl border shadow-2xl
           flex items-center gap-3 animate-in slide-in-from-bottom-5 fade-in duration-300
           {styles[type]}"
  >
    <div class="h-2 w-2 rounded-full bg-current animate-pulse"></div>
    <span>{text}</span>
  </div>
{/if}
