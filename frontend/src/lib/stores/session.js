import { writable } from 'svelte/store';

const SESSION_KEY = 'univote_voter_session';

/** 
 * @typedef {Object} StudentSession
 * @property {string} id - Database UUID
 * @property {string} student_id - Human readable ID
 * @property {string} full_name
 * @property {string} access_token - JWT for voting
 * @property {Array<{id: string, name: string, has_voted: boolean}>} [elections]
 */

function createSessionStore() {
  /** @type {StudentSession | null} */
  let initial = null;
  try {
    const stored = typeof window !== 'undefined' ? localStorage.getItem(SESSION_KEY) : null;
    initial = (stored && stored !== 'undefined') ? JSON.parse(stored) : null;
  } catch { initial = null; }

  const { subscribe, set, update } = writable(initial);

  return {
    subscribe,
    /** @param {StudentSession} student */
    login(student) {
      if (typeof window !== 'undefined') {
        localStorage.setItem(SESSION_KEY, JSON.stringify(student));
      }
      set(student);
    },
    /** Mark a specific election as voted in the session */
    /** @param {string} electionId */
    markVoted(electionId) {
      update(session => {
        if (!session) return session;
        const updated = {
          ...session,
          elections: (session.elections || []).map(e =>
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
  };
}

export const voterSession = createSessionStore();
