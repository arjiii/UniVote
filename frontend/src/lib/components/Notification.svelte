<script>
  /** @type {{ text?: string, type?: 'info' | 'success' | 'error' }} */
  let { text = '', type = 'info' } = $props();

  /** @type {Record<'info' | 'success' | 'error', string>} */
  const styles = {
    info:    'bg-slate-800 border-slate-700 text-white',
    success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    error:   'bg-rose-500/10 border-rose-500/30 text-rose-400',
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
