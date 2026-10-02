const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000/api";

async function request(path, options = {}) {
  const token = localStorage.getItem("skillpulse_token");
  const headers = { ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  let data = {};
  try { data = await response.json(); } catch (_) {}
  if (!response.ok) {
    if (response.status === 401) localStorage.removeItem("skillpulse_token");
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

export const api = {
  publicStats: () => request("/public/stats"),
  jobs: (params = {}) => {
    const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null));
    return request(`/jobs${qs.toString() ? `?${qs}` : ""}`);
  },
  login: (body) => request("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  register: (body) => request("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  me: () => request("/auth/me"),
  notifications: () => request("/notifications"),
  markAllRead: () => request("/notifications/read-all", { method: "POST" }),
  workerStats: () => request("/worker/dashboard-stats"),
  workerProfile: () => request("/worker/profile"),
  recommendedJobs: () => request("/worker/jobs/recommended"),
  applications: () => request("/worker/applications"),
  apply: (jobId) => request(`/jobs/${jobId}/apply`, { method: "POST" }),
  updateWorkerProfile: (body) => request("/worker/profile", { method: "PUT", body: JSON.stringify(body) }),
  setSkills: (skill_names) => request("/worker/skills", { method: "POST", body: JSON.stringify({ skill_names }) }),
  availability: (body) => request("/worker/availability", { method: "POST", body: JSON.stringify(body) }),
  contractorStats: () => request("/contractor/dashboard-stats"),
  contractorProfile: () => request("/contractor/profile"),
  contractorJobs: () => request("/contractor/jobs"),
  createJob: (body) => request("/contractor/jobs", { method: "POST", body: JSON.stringify(body) }),
  recommendations: (jobId) => request(`/contractor/jobs/${jobId}/recommended-workers`),
  selectWorker: (applicationId) => request(`/contractor/applications/${applicationId}/select`, { method: "POST" }),
  rejectWorker: (applicationId) => request(`/contractor/applications/${applicationId}/reject`, { method: "POST" }),
  updateJobStatus: (jobId, status) => request(`/contractor/jobs/${jobId}/status`, { method: "POST", body: JSON.stringify({ status }) }),
};
