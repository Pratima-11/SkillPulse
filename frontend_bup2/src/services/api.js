const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("skillpulse_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  let data = {};

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    throw new Error(
      data.error || `Request failed with status ${response.status}`
    );
  }

  return data;
}

export const api = {
  get: (endpoint) =>
    request(endpoint, {
      method: "GET",
    }),

  post: (endpoint, body) =>
    request(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  register: (body) =>
  request("/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  }),
  
  login: (body) =>
  request("/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  }),

  put: (endpoint, body) =>
    request(endpoint, {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  delete: (endpoint) =>
    request(endpoint, {
      method: "DELETE",
    }),

  // Public homepage statistics
  publicStats: () => request("/stats"),

  // Public/open jobs
  jobs: (search = "") =>
    request(`/jobs${search ? `?q=${encodeURIComponent(search)}` : ""}`),

  // Apply for a job
  apply: (jobId) =>
    request(`/jobs/${jobId}/apply`, {
      method: "POST",
    }),

  // Logged-in user's profile
  me: () => request("/auth/me"),

  // Worker profile
  workerProfile: () =>
    request("/worker/profile", {
      method: "GET",
    }),

  updateWorkerProfile: (data) =>
  request("/worker/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  }),  
  
  contractorProfile: () =>
  request("/contractor/profile", {
    method: "GET",
  }),

  contractorJobs: () =>
  request("/contractor/jobs", {
      method: "GET",
    }),

  recommendations: (jobId) =>
  request(`/contractor/jobs/${jobId}/recommended-workers`, {
    method: "GET",
  }),  

applications: (jobId) =>
  request(`/contractor/jobs/${jobId}/applications`, {
    method: "GET",
  }),

  // Create contractor job
  createJob: (jobData) =>
    request("/contractor/jobs", {
      method: "POST",
      body: JSON.stringify(jobData),
    }),  

  updateJobStatus: (jobId, status) =>
  request(`/contractor/jobs/${jobId}/status`, {
    method: "POST",
    body: JSON.stringify({ status }),
  }),
    
    // Notifications
  notifications: () =>
    request("/notifications", {
      method: "GET",
    }),

  markNotificationRead: (notificationId) =>
    request(`/notifications/${notificationId}/read`, {
      method: "POST",
    }),

  markAllNotificationsRead: () =>
    request("/notifications/read-all", {
      method: "POST",
    }),

  // Update worker skills
  setSkills: (skillNames) =>
    request("/worker/skills", {
      method: "POST",
      body: JSON.stringify({
        skill_names: Array.isArray(skillNames)
          ? skillNames
          : String(skillNames)
              .split(",")
              .map((skill) => skill.trim())
              .filter(Boolean),
      }),
    }),

  // Set worker availability
  setAvailability: (availableDate, isAvailable = true) =>
    request("/worker/availability", {
      method: "POST",
      body: JSON.stringify({
        available_date: availableDate,
        is_available: isAvailable,
      }),
    }),

  availability: (availableDate, isAvailable = true) =>
  request("/worker/availability", {
    method: "POST",
    body: JSON.stringify({
      available_date: availableDate,
      is_available: isAvailable,
    }),
  }),  

  // Recommended jobs for worker
  recommendedJobs: () =>
    request("/worker/jobs/recommended", {
      method: "GET",
    }),

  // Worker's submitted applications
  workerApplications: () =>
    request("/worker/applications", {
      method: "GET",
    }),

  // Worker dashboard statistics
workerStats: () =>
  request("/worker/dashboard-stats", {
    method: "GET",
  }),

workerDashboardStats: () =>
  request("/worker/dashboard-stats", {
    method: "GET",
  }),

// Contractor dashboard statistics
contractorStats: () =>
  request("/contractor/dashboard-stats", {
    method: "GET",
  }),

  // Rate a worker after job completion
  rateWorker: (applicationId, ratingValue, comment = "") =>
    request(`/contractor/applications/${applicationId}/rate`, {
      method: "POST",
      body: JSON.stringify({
        rating_value: Number(ratingValue),
        comment,
      }),
    }),  

};

export const healthCheck = () => api.get("/health");