<script>
  import { onMount } from 'svelte';
  import { admin as adminApi } from '$lib/api.js';
  import Notification from '$lib/components/Notification.svelte';

  /** @type {Array<any>} */
  let students = $state([]);
  let isLoading = $state(true);
  let studentSearch = $state('');
  let csvFile = $state(/** @type {File | null} */ (null));
  let isUploading = $state(false);
  let newStudent = $state({ student_id: '', full_name: '', course: '', year_level: '' });
  let isAddingStudent = $state(false);
  let editingStudent = $state(/** @type {any} */ (null));

  /** @type {{ text: string, type: 'info' | 'success' | 'error' }} */
  let notification = $state({ text: '', type: 'info' });

  onMount(async () => { await loadStudents(); });

  async function loadStudents() {
    try {
      isLoading = true;
      const res = await adminApi.getStudents();
      students = res.data ?? [];
    } catch (err) { console.error('Failed to load students:', err); }
    finally { isLoading = false; }
  }

  function notify(text = '', type = /** @type {'info' | 'success' | 'error'} */ ('info')) {
    notification = { text, type };
    setTimeout(() => (notification = { text: '', type: 'info' }), 3500);
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
      editingStudent = null;
      await loadStudents();
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to save student', 'error'); }
    finally { isAddingStudent = false; }
  }

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
      await loadStudents();
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Error uploading students.', 'error'); }
    finally { isUploading = false; }
  }

  async function deleteStudent(id) {
    if (!confirm('Delete this student and their votes?')) return;
    try {
      await adminApi.deleteStudent(id);
      students = students.filter(s => s.student_id !== id);
      notify('Student removed', 'success');
    } catch (/** @type {any} */ err) { notify(err.message ?? 'Failed to delete student', 'error'); }
  }

  const filteredStudents = $derived(
    studentSearch ? students.filter(s =>
      s.full_name.toLowerCase().includes(studentSearch.toLowerCase()) ||
      s.student_id.includes(studentSearch)
    ) : students
  );
</script>

<svelte:head>
  <title>Voters | UniVote Admin</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-5 md:px-8 py-8 space-y-6">
  <div>
    <p class="text-[10px] font-semibold text-stone-400 tracking-widest uppercase mb-1">Admin</p>
    <h1 class="text-2xl font-semibold text-stone-900">Voter Management</h1>
    <p class="text-stone-500 text-sm mt-0.5">Add, edit, or import student voters.</p>
  </div>

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
          <label for="student_id" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Student ID</label>
          <input id="student_id" bind:value={newStudent.student_id} disabled={!!editingStudent} placeholder="e.g. 2024-0001" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all disabled:bg-stone-50"/>
        </div>
        <div>
          <label for="student_full_name" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Full Name</label>
          <input id="student_full_name" bind:value={newStudent.full_name} placeholder="e.g. Juan Dela Cruz" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="student_course" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Course</label>
            <input id="student_course" bind:value={newStudent.course} placeholder="BSIT" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
          <div>
            <label for="student_year" class="block text-xs font-semibold text-stone-500 tracking-wide uppercase mb-1.5">Year</label>
            <input id="student_year" type="number" bind:value={newStudent.year_level} placeholder="1" class="w-full bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-sm text-stone-900 focus:outline-none focus:border-stone-900 transition-all"/>
          </div>
        </div>
        <div class="flex gap-2 pt-2">
          {#if editingStudent}
            <button type="button" onclick={() => { editingStudent = null; newStudent = { student_id: '', full_name: '', course: '', year_level: '' }; }} class="flex-1 bg-stone-100 text-stone-600 rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-200 transition-all">Cancel</button>
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
            <input type="file" accept=".csv" class="hidden" onchange={(e) => csvFile = /** @type {HTMLInputElement} */ (e.target).files?.[0] || null} />
          </label>
          <button type="submit" disabled={!csvFile || isUploading} class="w-full bg-stone-100 text-stone-900 border border-stone-200 rounded-xl py-2.5 text-sm font-semibold hover:bg-stone-200 disabled:opacity-40 transition-all">
            {isUploading ? 'Importing...' : 'Upload & Import'}
          </button>
        </form>
      </div>
    </div>

    <!-- Voter List -->
    <div class="lg:col-span-2 bg-white rounded-2xl border border-stone-200 p-6 flex flex-col min-h-[600px]">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 bg-stone-100 rounded-xl flex items-center justify-center">
            <svg class="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
          </div>
          <h2 class="text-sm font-semibold text-stone-900">Voter Database <span class="text-stone-400 font-normal">({students.length})</span></h2>
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
            {#if isLoading}
              {#each Array(5) as _}
                <tr class="animate-pulse"><td colspan="4" class="py-4 px-4"><div class="h-8 bg-stone-100 rounded-lg"></div></td></tr>
              {/each}
            {:else if filteredStudents.length === 0}
              <tr><td colspan="4" class="py-12 text-center text-stone-400 text-xs italic">No students found.</td></tr>
            {:else}
              {#each filteredStudents as student}
                <tr class="hover:bg-stone-50/80 transition-colors group">
                  <td class="py-4 px-4 text-xs font-mono font-medium text-stone-900 uppercase tracking-tighter">{student.student_id}</td>
                  <td class="py-4 px-4 text-xs font-semibold text-stone-900">{student.full_name}</td>
                  <td class="py-4 px-4 text-[10px] text-stone-400 italic">{student.course || 'N/A'} {student.year_level ? `• Year ${student.year_level}` : ''}</td>
                  <td class="py-4 px-4 text-right space-x-1 whitespace-nowrap">
                    <button onclick={() => { editingStudent = student; newStudent = { ...student }; }} class="p-2 text-stone-400 hover:text-stone-900 hover:bg-stone-200 rounded-lg transition-all" title="Edit">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </button>
                    <button onclick={() => deleteStudent(student.student_id)} class="p-2 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100" title="Delete">
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
</div>

<div class="fixed bottom-6 right-6 z-[60]">
  <Notification text={notification.text} type={notification.type} />
</div>
