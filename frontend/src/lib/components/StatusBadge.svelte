<script>
  /** @type {{ status: 'upcoming' | 'active' | 'completed' | 'closed' | boolean }} */
  let { status } = $props();

  /** @type {Record<string, string>} */
  const styles = {
    active:    'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    upcoming:  'bg-slate-500/10  text-slate-400   border-slate-500/30',
    completed: 'bg-violet-500/10 text-violet-400  border-violet-500/30',
    closed:    'bg-rose-500/10   text-rose-400    border-rose-500/30',
  };

  /** @type {Record<string, string>} */
  const labels = {
    active: 'Live', upcoming: 'Upcoming', completed: 'Completed', closed: 'Closed',
  };

  // $derived re-evaluates reactively whenever `status` changes
  const normalized = $derived(
    typeof status === 'boolean' ? (status ? 'active' : 'upcoming') : status
  );
</script>

<span
  class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border
         {styles[normalized] ?? styles.upcoming}"
>
  <span class="h-1.5 w-1.5 rounded-full bg-current {normalized === 'active' ? 'animate-pulse' : ''}"></span>
  {labels[normalized] ?? normalized}
</span>
