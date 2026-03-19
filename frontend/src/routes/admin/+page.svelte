<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import Notification from '$lib/components/Notification.svelte';

  /** @type {Array<any>} */
  let auditLogs = $state([]);
  let isLoadingLogs = $state(true);

  let elections = $state([]);
  let isLoadingElections = $state(true);

  let students = $state([]);
  let isLoadingStudents = $state(true);
  let studentSearch = $state('');

  let advisers = $state([]);
  let isLoadingAdvisers = $state(true);

  let newElection = $state({ name: '', start_date: '', end_date: '', description: '' });
  let isCreating = $state(false);

  let csvFile = $state(/** @type {File | null} */ (null));
  let isUploading = $state(false);

  let newStudent = $state({ student_id: '', full_name: '', course: '', year_level: '' });
  let isAddingStudent = $state(false);
  let editingStudent = $state(/** @type {any} */ (null));

  let newAdviser = $state({ full_name: '', email: '', password: '', department: '' });
  let isAddingAdviser = $state(false);

  let activeTab = $state('elections'); // 'elections', 'voters', 'advisers', 'activity'
  
  /** @type {{ text: string, type: 'info' | 'success' | 'error' }} */
  let notification = $state({ text: '', type: 'info' });

  onMount(async () => { await refreshData(); });

  async function refreshData() {
    try {
      const [logsRes, electionsRes, studentsRes, advisersRes] = await Promise.all([
        adminApi.getAuditLog(), 
        adminApi.getElections(),
        adminApi.getStudents(),
        adminApi.getAdvisers()
      ]);
      auditLogs = logsRes.data ?? [];
      elections = electionsRes.data ?? [];
      students = studentsRes.data ?? [];
      advisers = advisersRes.data ?? [];
    } catch (err) { console.error('Failed to load data:', err); }
    finally { 
      isLoadingLogs = false; 
      isLoadingElections = false; 
      isLoadingStudents = false;
      isLoadingAdvisers = false;
    }
  }

  function notify(text = '', type = /** @type {'info' | 'success' | 'error'} */ ('info')) {
    notification = { text, type };
    setTimeout(() => (notification = { text: '', type: 'info' }), 3500);
  }

  // --- Election Handlers ---
  async function handleCreateElection(e) {
    e.preventDefault();
    if (!newElection.name || !newElection.start_date || !newElection.end_date) {
      notify('Please fill in all required fields.', 'error'); return;
    }
    const start = new Date(newElection.start_date);
    const end = new Date(newElection.end_date);
    if (end <= start) { notify('End date must be after start date.', 'error'); return; }
    isCreating = true;
    try {
      await adminApi.createElection({ ...newElection, start_date: new Date(newElection.start_date).toISOString(), end_date: new Date(newElection.end_date).toISOString() });
      await refreshData();
      newElection = { name: '', start_date: '', end_date: '', description: '' };
      notify('Election created successfully', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to create election', 'error'); }
    finally { isCreating = false; }
  }

  async function toggleElection(id, current_status) {
    let nextStatus = 'upcoming';
    if (current_status === 'upcoming') nextStatus = 'active';
    else if (current_status === 'active') nextStatus = 'completed';
    try {
      await adminApi.toggleElection(id, nextStatus);
      const res = await adminApi.getElections();
      elections = res.data ?? [];
      notify('Election status updated', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Error updating status', 'error'); }
  }

  async function deleteElection(id) {
    if (!confirm('Are you sure? This will delete all candidates, partylists, and votes for this election permanently.')) return;
    try {
      await adminApi.deleteElection(id);
      elections = elections.filter(e => e.id !== id);
      notify('Election deleted', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to delete election', 'error'); }
  }

  // --- Student Handlers ---
  async function handleCSVUpload(e) {
    e.preventDefault();
    if (!csvFile) return;
    isUploading = true;
    notify('Uploading students...', 'info');
    const formData = new FormData();
    formData.append('file', csvFile);
    try {
      const data = await adminApi.uploadStudents(formData);
      notify(data.message ?? 'Students imported successfully.', 'success');
      csvFile = null;
      await refreshData();
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Error uploading students.', 'error'); }
    finally { isUploading = false; }
  }

  async function handleAddStudent(e) {
    e.preventDefault();
    if (!newStudent.student_id || !newStudent.full_name) {
      notify('Student ID and Full Name are required.', 'error'); return;
    }
    isAddingStudent = true;
    try {
      const payload = { ...newStudent, year_level: newStudent.year_level ? parseInt(newStudent.year_level) : undefined };
      if (editingStudent) {
        await adminApi.updateStudent(editingStudent.student_id, payload);
        notify('Student updated', 'success');
      } else {
        await adminApi.addStudent(payload);
        notify('Student added', 'success');
      }
      newStudent = { student_id: '', full_name: '', course: '', year_level: '' };
  function handleFileChange(e) {
    const input = /** @type {HTMLInputElement} */ (e.target);
    csvFile = input.files?.[0] ?? null;
  }

  async function deleteStudent(id) {
    if (!confirm('Delete this student and their votes?')) return;
    try {
      await adminApi.deleteStudent(id);
      students = students.filter(s => s.student_id !== id);
      notify('Student removed', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to delete student', 'error'); }
  }

  // --- Adviser Handlers ---
  async function handleAddAdviser(e) {
    e.preventDefault();
    if (!newAdviser.email || !newAdviser.password || !newAdviser.full_name) {
      notify('All fields are required.', 'error'); return;
    }
    isAddingAdviser = true;
    try {
      await adminApi.createAdviser(newAdviser);
      newAdviser = { email: '', password: '', full_name: '', department: '' };
      notify('Adviser account created', 'success');
      await refreshData();
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to create adviser', 'error'); }
    finally { isAddingAdviser = false; }
  }

  async function deleteAdviser(id) {
    if (!confirm('Delete this adviser account?')) return;
    try {
      await adminApi.deleteAdviser(id);
      advisers = advisers.filter(a => a.id !== id);
      notify('Adviser account removed', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to delete adviser', 'error'); }
  }

  const filteredStudents = $derived(
    studentSearch ? students.filter(s => 
      s.full_name.toLowerCase().includes(studentSearch.toLowerCase()) || 
      s.student_id.includes(studentSearch)
    ) : students
  );
</script>

<svelte:head>
  <title>Admin Dashboard | UniVote</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">

  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    <div>
      <p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Admin</p>
      <h1 class="text-2xl font-semibold text-stone-900">Dashboard</h1>
      <p class="text-stone-500 text-sm mt-0.5">Manage elections, students, and staff.</p>
    </div>
    <div class="flex items-center gap-2">
      <button 
        onclick={refreshData} 
        class="flex items-center gap-2 px-4 py-2 bg-white border border-stone-200 rounded-xl text-sm font-medium text-stone-700 hover:bg-stone-50 hover:border-stone-300 transition-all"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
        Refresh
      </button>
    </div>
  </div>

  <!-- Tabs -->
  <div class="flex items-center gap-1 bg-stone-100 p-1 rounded-xl w-fit">
    {#each ['elections', 'voters', 'advisers', 'activity'] as tab}
      <button 
        onclick={() => activeTab = tab}
        class="px-4 py-2 text-xs font-semibold rounded-lg transition-all uppercase tracking-wider
          {activeTab === tab ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500 hover:text-stone-700'}"
      >
        {tab}
      </button>
    {/each}
  </div>

  <!-- KPI Stats (Always visible or contextual?) - Let's keep them always visible for overview -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    {#each [
      { label: 'Total Elections', value: elections.length, icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
      { label: 'Active', value: elections.filter(e => e.status === 'active').length, icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
      { label: 'Total Voters', value: students.length, icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
      { label: 'Advisers', value: advisers.length, icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' }
    ] as stat}
      <div class="bg-white rounded-2xl border border-stone-200 p-5">
        <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center mb-3">
          <svg class="w-4 h-4 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={stat.icon}/></svg>
        </div>
        <p class="text-3xl font-semibold text-stone-900">{stat.value}</p>
        <p class="text-[10px] font-semibold text-stone-400 uppercase tracking-widest mt-1">{stat.label}</p>
      </div>
    {/each}
  </div>

  <!-- Content Sections -->
  {#if activeTab === 'elections'}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- New Election Form -->
      <div class="bg-white rounded-2xl border border-stone-200 p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/></svg>
          </div>
          <h2 class="text-sm font-semibold text-stone-900">New Election</h2>
        </div>
        <form onsubmit={handleCreateElection} class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Election Name</label>
            <input bind:value={newElection.name} placeholder="e.g. Student Council 2024" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 focus:ring-[3px] focus:ring-stone-900/[0.06] transition-all"/>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Start Date</label>
              <input type="datetime-local" bind:value={newElection.start_date} class="w-full bg-white border border-stone-200 rounded-xl px-3 py-2.5 text-xs text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">End Date</label>
              <input type="datetime-local" bind:value={newElection.end_date} class="w-full bg-white border border-stone-200 rounded-xl px-3 py-2.5 text-xs text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
            </div>
          </div>
          <button type="submit" disabled={isCreating} class="w-full bg-stone-900 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-800 disabled:opacity-50 transition-all">
            {isCreating ? 'Creating...' : 'Create Election'}
          </button>
        </form>
      </div>

      <!-- Elections List -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-stone-200 p-6 overflow-hidden">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <h2 class="text-sm font-semibold text-stone-900">Existing Elections</h2>
        </div>
        <div class="space-y-3 overflow-y-auto max-h-[400px] pr-2 scrollbar-hide">
          {#if isLoadingElections}
            <div class="py-12 flex items-center justify-center text-stone-400 text-sm animate-pulse">Loading elections...</div>
          {:else if elections.length === 0}
            <div class="py-12 flex flex-col items-center justify-center border-2 border-dashed border-stone-100 rounded-xl text-stone-400 text-sm italic">No elections found.</div>
          {:else}
            {#each elections as election}
              <div class="flex items-center justify-between p-4 bg-stone-50 rounded-xl border border-stone-100 hover:border-stone-200 transition-all group">
                <div>
                  <p class="font-medium text-stone-900 text-sm">{election.name}</p>
                  <div class="flex items-center gap-3 mt-1">
                    <span class="inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide
                      {election.status === 'active' ? 'text-emerald-600' : election.status === 'completed' ? 'text-stone-500' : 'text-amber-600'}">
                      <span class="w-1.5 h-1.5 rounded-full {election.status === 'active' ? 'bg-emerald-500 animate-pulse' : election.status === 'completed' ? 'bg-stone-400' : 'bg-amber-400'}"></span>
                      {election.status}
                    </span>
                    <span class="text-[10px] text-stone-400 bg-stone-100 px-1.5 py-0.5 rounded italic">Ends {new Date(election.end_date).toLocaleDateString()}</span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  {#if election.status === 'upcoming'}
                    <button onclick={() => toggleElection(election.id, election.status)} class="bg-stone-900 text-white hover:bg-stone-800 rounded-lg px-3 py-1.5 text-[10px] font-bold uppercase transition-all">Start</button>
                  {:else if election.status === 'active'}
                    <button onclick={() => toggleElection(election.id, election.status)} class="bg-red-50 text-red-600 border border-red-100 hover:bg-red-100 rounded-lg px-3 py-1.5 text-[10px] font-bold uppercase transition-all">End</button>
                  {/if}
                  <button 
                    onclick={() => deleteElection(election.id)}
                    class="p-2 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                    title="Delete Election"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
  {:else if activeTab === 'voters'}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Student Form -->
      <div class="bg-white rounded-2xl border border-stone-200 p-6 h-fit sticky top-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
          </div>
          <h2 class="text-sm font-semibold text-stone-900">{editingStudent ? 'Edit Student' : 'Manual Entry'}</h2>
        </div>
        <form onsubmit={handleAddStudent} class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Student ID</label>
            <input bind:value={newStudent.student_id} disabled={!!editingStudent} placeholder="e.g. 2024-0001" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all disabled:bg-stone-50"/>
          </div>
          <div>
            <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Full Name</label>
            <input bind:value={newStudent.full_name} placeholder="e.g. Juan Dela Cruz" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Course</label>
              <input bind:value={newStudent.course} placeholder="BSIT" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Year</label>
              <input type="number" bind:value={newStudent.year_level} placeholder="1" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
            </div>
          </div>
          <div class="flex gap-2 pt-2">
            {#if editingStudent}
              <button type="button" onclick={() => { editingStudent = null; newStudent = { student_id: '', full_name: '', course: '', year_level: '' }; }} class="flex-1 bg-stone-100 text-stone-600 rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-200 transition-all text-center">Cancel</button>
            {/if}
            <button type="submit" disabled={isAddingStudent} class="flex-[2] bg-stone-900 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-800 disabled:opacity-50 transition-all">
              {isAddingStudent ? 'Saving...' : editingStudent ? 'Update Voter' : 'Add Voter'}
            </button>
          </div>
        </form>

        <div class="mt-8 pt-8 border-t border-stone-100">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center text-stone-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/></svg>
            </div>
            <h2 class="text-sm font-semibold text-stone-900">Bulk Import</h2>
          </div>
          <form onsubmit={handleCSVUpload} class="space-y-4">
            <label class="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-stone-200 rounded-xl cursor-pointer hover:border-stone-400 hover:bg-stone-50 transition-all bg-stone-50/50">
              <p class="text-xs text-stone-500 font-medium px-4 text-center">{csvFile ? csvFile.name : 'Select CSV file'}</p>
              <input type="file" accept=".csv" class="hidden" onchange={(e) => csvFile = e.target.files?.[0] || null} />
            </label>
            <button type="submit" disabled={!csvFile || isUploading} class="w-full bg-stone-100 text-stone-900 border border-stone-200 rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-200 disabled:opacity-40 transition-all">
              {isUploading ? 'Importing...' : 'Upload & Import'}
            </button>
          </form>
        </div>
      </div>

      <!-- Voter List Table -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-stone-200 p-6 flex flex-col min-h-[600px]">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
            </div>
            <h2 class="text-sm font-semibold text-stone-900">Voter Database</h2>
          </div>
          <div class="relative max-w-xs w-full">
            <svg class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            <input bind:value={studentSearch} placeholder="Search ID or name..." class="w-full pl-9 pr-4 py-2 bg-stone-50 border border-stone-200 rounded-xl text-xs focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
        </div>

        <div class="flex-1 overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="border-b border-stone-100">
                <th class="pb-4 pt-0 font-semibold text-stone-400 text-[10px] uppercase tracking-wider px-4">Student ID</th>
                <th class="pb-4 pt-0 font-semibold text-stone-400 text-[10px] uppercase tracking-wider px-4">Full Name</th>
                <th class="pb-4 pt-0 font-semibold text-stone-400 text-[10px] uppercase tracking-wider px-4">Details</th>
                <th class="pb-4 pt-0 font-semibold text-stone-400 text-[10px] uppercase tracking-wider px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-stone-50">
              {#if isLoadingStudents}
                {#each Array(5) as _}
                  <tr class="animate-pulse">
                    <td colspan="4" class="py-4 px-4 h-12 bg-stone-50/50 rounded-lg mb-2"></td>
                  </tr>
                {/each}
              {:else if filteredStudents.length === 0}
                <tr>
                  <td colspan="4" class="py-12 text-center text-stone-400 text-xs italic">No students found matching your search.</td>
                </tr>
              {:else}
                {#each filteredStudents as student}
                  <tr class="hover:bg-stone-50/80 transition-colors group">
                    <td class="py-4 px-4 text-xs font-mono font-medium text-stone-900 uppercase tracking-tighter">{student.student_id}</td>
                    <td class="py-4 px-4 text-xs font-semibold text-stone-900">{student.full_name}</td>
                    <td class="py-4 px-4 text-[10px] text-stone-400 italic">
                      {student.course || 'N/A'} {student.year_level ? `• Year ${student.year_level}` : ''}
                    </td>
                    <td class="py-4 px-4 text-right space-x-1 whitespace-nowrap">
                      <button 
                        onclick={() => { editingStudent = student; newStudent = { ...student }; }}
                        class="p-2 text-stone-400 hover:text-stone-900 hover:bg-stone-200 rounded-lg transition-all"
                        title="Edit Student"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                      </button>
                      <button 
                        onclick={() => deleteStudent(student.student_id)}
                        class="p-2 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                        title="Delete Student"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                      </button>
                    </td>
                  </tr>
                {/each}
              {/if}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  {:else if activeTab === 'advisers'}
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Add Adviser Form -->
      <div class="bg-white rounded-2xl border border-stone-200 p-6 h-fit">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
          </div>
          <h2 class="text-sm font-semibold text-stone-900">New Adviser</h2>
        </div>
        <form onsubmit={handleAddAdviser} class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Full Name</label>
            <input bind:value={newAdviser.full_name} placeholder="e.g. Prof. Jane Doe" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Email Address</label>
            <input type="email" bind:value={newAdviser.email} placeholder="jane.doe@univote.edu" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Password</label>
            <input type="password" bind:value={newAdviser.password} placeholder="••••••••" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
          <div>
            <label class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Department (Optional)</label>
            <input bind:value={newAdviser.department} placeholder="e.g. CITE" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
          <button type="submit" disabled={isAddingAdviser} class="w-full bg-stone-900 text-white rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-800 disabled:opacity-50 transition-all">
            {isAddingAdviser ? 'Creating...' : 'Create Adviser Account'}
          </button>
        </form>
      </div>

      <!-- Adviser List -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-stone-200 p-6 overflow-hidden">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
          </div>
          <h2 class="text-sm font-semibold text-stone-900">Manage Advisers</h2>
        </div>
        <div class="space-y-3 overflow-y-auto max-h-[500px] pr-2 scrollbar-hide">
          {#if isLoadingAdvisers}
            <div class="py-12 flex items-center justify-center text-stone-400 text-sm animate-pulse">Loading advisers...</div>
          {:else if advisers.length === 0}
            <div class="py-12 flex flex-col items-center justify-center border-2 border-dashed border-stone-100 rounded-xl text-stone-400 text-sm italic">No adviser accounts yet.</div>
          {:else}
            {#each advisers as adviser}
              <div class="flex items-center justify-between p-4 bg-stone-50 rounded-xl border border-stone-100 hover:border-stone-200 transition-all group">
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 rounded-full bg-stone-200 flex items-center justify-center text-stone-600 font-bold text-xs uppercase">
                    {adviser.full_name?.charAt(0) || 'A'}
                  </div>
                  <div>
                    <p class="font-semibold text-stone-900 text-sm">{adviser.full_name}</p>
                    <p class="text-[10px] text-stone-400 font-medium tracking-tight mt-0.5">{adviser.email} {adviser.department ? `• ${adviser.department}` : ''}</p>
                  </div>
                </div>
                <button 
                  onclick={() => deleteAdviser(adviser.id)}
                  class="p-2.5 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all opacity-0 group-hover:opacity-100"
                  title="Delete Adviser"
                >
                  <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </div>
  {:else if activeTab === 'activity'}
    <div class="bg-white rounded-2xl border border-stone-200 p-6 flex flex-col min-h-[500px]">
      <div class="flex items-center gap-3 mb-8">
        <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
          <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/></svg>
        </div>
        <h2 class="text-sm font-semibold text-stone-900">System Audit Trail</h2>
      </div>
      <div class="flex-1 overflow-y-auto pr-2 scrollbar-hide">
        {#if isLoadingLogs}
          <div class="py-20 flex items-center justify-center text-stone-400 text-sm animate-pulse italic">Retrieving audit logs...</div>
        {:else if auditLogs.length === 0}
          <div class="py-20 flex flex-col items-center justify-center border-2 border-dashed border-stone-100 rounded-xl text-stone-400 text-xs gap-2">
             <p>No activity has been logged yet.</p>
          </div>
        {:else}
          <div class="space-y-4">
            {#each auditLogs as log}
              <div class="flex items-start gap-4 p-4 bg-stone-50 rounded-xl border border-stone-100 hover:border-stone-200 transition-all">
                <div class="w-8 h-8 rounded-lg bg-stone-200 flex items-center justify-center shrink-0">
                  <span class="text-[10px] font-bold text-stone-500 uppercase">{log.actor_role?.[0] || 'U'}</span>
                </div>
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <p class="text-xs font-bold text-stone-900">{log.action}</p>
                    <span class="text-[10px] font-semibold text-stone-400 uppercase tracking-tighter bg-white px-1.5 py-0.5 rounded border border-stone-100">{log.target_type}</span>
                  </div>
                  <p class="text-[10px] text-stone-500 italic">Performed by {log.actor_role} at {new Date(log.created_at).toLocaleString()}</p>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <div class="fixed bottom-6 right-6 z-[60]">
    <Notification text={notification.text} type={notification.type} />
  </div>
</div>
