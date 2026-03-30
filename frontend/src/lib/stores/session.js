import { writable } from 'svelte/store';

const SESSION_KEY = 'univote_voter_session';

/**
 * @typedef {Object} StudentSession
 * @property {string} id - Database UUID
 * @property {string} student_id - Human readable ID
 * @property {string} full_name
 * @property {string} access_token - JWT for voting
 * @property {Array<{id: string, name: string, has_voted: boolean, end_date?: string}>} [elections]
 */

function createSessionStore() {
	/** @type {StudentSession | null} */
	let initial = null;
	try {
		const stored = typeof window !== 'undefined' ? localStorage.getItem(SESSION_KEY) : null;
		initial = stored && stored !== 'undefined' ? JSON.parse(stored) : null;
	} catch {
		initial = null;
	}

	const { subscribe, set, update } = writable(initial);

	return {
		subscribe,
		/** @param {any} data */
		login(data) {
			const student = data.student || data;
			const flattened = {
				access_token: data.access_token || student.access_token,
				student_id: student.student_id,
				full_name: student.full_name,
				id: student.id,
				program: student.program,
				year_level: student.year_level,
				elections: data.active_elections || data.elections || []
			};
			if (typeof window !== 'undefined') {
				localStorage.setItem(SESSION_KEY, JSON.stringify(flattened));
			}
			set(flattened);
		},
		/** Mark a specific election as voted in the session */
		/** @param {string} electionId */
		markVoted(electionId) {
			update((session) => {
				if (!session) return session;
				const updated = {
					...session,
					elections: (session.elections || []).map((e) =>
						e.id === electionId ? { ...e, has_voted: true } : e
					)
				};
				if (typeof window !== 'undefined') {
					localStorage.setItem(SESSION_KEY, JSON.stringify(updated));
				}
				return updated;
			});
		},
		logout() {
			if (typeof window !== 'undefined') {
				localStorage.removeItem(SESSION_KEY);
			}
			set(null);
		},
		/** @param {string} studentId */
		async sync(studentId) {
			try {
				const { student: studentApi } = await import('$lib/api.js');
				const data = await studentApi.validate(studentId);
				// data looks like { student: {...}, active_elections: [...], access_token: "..." }
				this.login(data);
				return data;
			} catch (err) {
				console.error('Session sync failed:', err);
				throw err;
			}
		}
	};
}


export const voterSession = createSessionStore();
