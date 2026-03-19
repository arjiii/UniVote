import { authSession } from './stores/auth.js';
import { voterSession } from './stores/session.js';

const BASE = 'http://localhost:8000';

let currentToken = /** @type {string | null} */ (null);

function updateToken() {
  let staff, voter;
  authSession.subscribe(s => staff = s)();
  voterSession.subscribe(s => voter = s)();
  currentToken = staff?.access_token || voter?.access_token || null;
}
authSession.subscribe(updateToken);
voterSession.subscribe(updateToken);

/**
 * Internal helper: fetch JSON and throw on non-2xx
 * @param {string} path
 * @param {RequestInit} [options]
 */
async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (currentToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${currentToken}`);
  }

  const mergedOptions = { ...options, headers };
  const res = await fetch(`${BASE}${path}`, mergedOptions);
  const data = await res.json().catch(() => null);
  
  if (!res.ok) {
    let message = data?.message ?? `Request failed: ${res.status}`;
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail.map((/** @type {any} */ err) => err.msg || JSON.stringify(err)).join(', ');
      }
    }
    throw new Error(message);
  }
  return data;
}

/** @param {object} body */
function json(body) {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  };
}

// ---------------------------------------------------------------------------
// Auth endpoints
// ---------------------------------------------------------------------------
export const auth = {
  /**
   * @param {string} email
   * @param {string} password
   */
  login: (email, password) =>
    request('/api/auth/login', json({ email, password })),

  /**
   * @param {object} payload
   * @param {string} payload.email
   * @param {string} payload.password
   * @param {string} payload.full_name
   * @param {string} payload.role
   * @param {string} [payload.department]
   */
  register: (payload) =>
    request('/api/auth/register', json(payload)),
};

// ---------------------------------------------------------------------------
// Student endpoints
// ---------------------------------------------------------------------------
export const student = {
  /** @param {string} student_id */
  validate: (student_id) =>
    request('/api/student/validate', json({ student_id })),

  /**
   * @param {string} student_id
   * @param {string} election_id
   * @param {Array<{candidate_id: string, position: string}>} votes
   */
  vote: (student_id, election_id, votes) =>
    request('/api/student/vote', { ...json({ student_id, election_id, votes }), method: 'POST' }),

  /** @param {string} election_id */
  getCandidates: (election_id) =>
    request(`/api/student/candidates?election_id=${election_id}`),

  /**
   * @param {string} student_id
   * @param {string} election_id
   */
  getVoteSummary: (student_id, election_id) =>
    request(`/api/student/vote-summary?student_id=${student_id}&election_id=${election_id}`),

  /** @param {string} election_id */
  getResults: (election_id) =>
    request(`/api/student/results?election_id=${election_id}`),
};

// ---------------------------------------------------------------------------
// Admin endpoints
// ---------------------------------------------------------------------------
export const admin = {
  getElections: () =>
    request('/api/admin/elections'),

  /**
   * @param {object} payload
   * @param {string} payload.name
   * @param {string} payload.start_date
   * @param {string} payload.end_date
   * @param {string} [payload.description]
   */
  createElection: (payload) =>
    request('/api/admin/elections', json(payload)),

  /**
   * @param {string} election_id
   * @param {'upcoming' | 'active' | 'completed'} status
   */
  toggleElection: (election_id, status) =>
    request(`/api/admin/elections/${election_id}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    }),

  /** @param {FormData} formData */
  uploadStudents: (formData) =>
    request('/api/admin/students/upload', { method: 'POST', body: formData }),

  /**
   * @param {object} payload
   * @param {string} payload.student_id
   * @param {string} payload.full_name
   * @param {string} [payload.course]
   * @param {number} [payload.year_level]
   */
  addStudent: (payload) =>
    request('/api/admin/students', json(payload)),

  getAuditLog: () =>
    request('/api/admin/audit-log'),

  /** @param {string} election_id */
  deleteElection: (election_id) =>
    request(`/api/admin/elections/${election_id}`, { method: 'DELETE' }),

  getStudents: () =>
    request('/api/admin/students'),

  /**
   * @param {string} student_id
   * @param {object} payload
   */
  updateStudent: (student_id, payload) =>
    request(`/api/admin/students/${student_id}`, { ...json(payload), method: 'PUT' }),

  /** @param {string} student_id */
  deleteStudent: (student_id) =>
    request(`/api/admin/students/${student_id}`, { method: 'DELETE' }),

  getAdvisers: () =>
    request('/api/admin/advisers'),

  /** @param {object} payload */
  createAdviser: (payload) =>
    request('/api/admin/advisers', json(payload)),

  /** @param {string} adviser_id */
  deleteAdviser: (adviser_id) =>
    request(`/api/admin/advisers/${adviser_id}`, { method: 'DELETE' }),
};

// ---------------------------------------------------------------------------
// Adviser endpoints
// ---------------------------------------------------------------------------
export const adviser = {
  /** @param {string} [election_id] */
  getPartylists: (election_id) =>
    request(`/api/adviser/partylists${election_id ? `?election_id=${election_id}` : ''}`),

  /**
   * @param {string} election_id
   * @param {string} name
   */
  createPartylist: (election_id, name) =>
    request(`/api/adviser/partylists?election_id=${election_id}`, json({ name })),

  /**
   * @param {string} partylist_id
   * @param {string} name
   */
  updatePartylist: (partylist_id, name) =>
    request(`/api/adviser/partylists/${partylist_id}`, { ...json({ name }), method: 'PUT' }),

  /**
   * @param {string} partylist_id
   */
  deletePartylist: (partylist_id) =>
    request(`/api/adviser/partylists/${partylist_id}`, { method: 'DELETE' }),

  /** @param {string} [election_id] */
  getCandidates: (election_id) =>
    request(`/api/adviser/candidates${election_id ? `?election_id=${election_id}` : ''}`),

  /**
   * @param {string} election_id
   * @param {object} payload
   */
  createCandidate: (election_id, payload) =>
    request(`/api/adviser/candidates?election_id=${election_id}`, json(payload)),

  /** @param {string} election_id */
  getLiveResults: (election_id) =>
    request(`/api/adviser/live-results/${election_id}`),

  /** @param {string} candidate_id */
  deleteCandidate: (candidate_id) =>
    request(`/api/adviser/candidates/${candidate_id}`, { method: 'DELETE' }),

  /** @param {number} [limit] */
  getAuditLog: (limit) =>
    request(`/api/adviser/audit-log${limit ? `?limit=${limit}` : ''}`),
};
