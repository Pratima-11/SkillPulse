import React, { useEffect, useState, useMemo } from "react";
import "./App.css";
import { api, healthCheck } from "./services/api";


const fallbackJobs = [
  { id: "demo-1", icon: "🎨", skill: "Painter", description: "Interior wall painting for residential property", area_text: "Kumaraswamy Layout, Bengaluru", wage: 800, working_hours: "9:00 AM – 5:00 PM", job_date: "Tomorrow" },
  { id: "demo-2", icon: "🧱", skill: "Mason", description: "Brickwork and construction assistance required", area_text: "JP Nagar, Bengaluru", wage: 950, working_hours: "8:30 AM – 5:30 PM", job_date: "Tomorrow" },
  { id: "demo-3", icon: "🔧", skill: "Plumber", description: "Residential plumbing and pipe installation", area_text: "HSR Layout, Bengaluru", wage: 900, working_hours: "9:00 AM – 4:30 PM", job_date: "Tomorrow" },
];

const icons = { Painter: "🎨", Mason: "🧱", Plumber: "🔧", Electrician: "⚡", Carpenter: "🪚", Helper: "👷" };
const emptyStats = { verified_workers: 0, contractors: 0, jobs_completed: 0, average_rating: 0, open_jobs: 0 };

function formatDate(value) {
  if (!value || value === "Tomorrow") return value || "";
  const d = new Date(`${value}T00:00:00`);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

function App() {
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState(emptyStats);
  const [search, setSearch] = useState({ skill: "", area: "" });
  const [loading, setLoading] = useState(true);
  const [authMode, setAuthMode] = useState(null);
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
    const [backendStatus, setBackendStatus] = useState("checking");


useEffect(() => {
  api.publicStats()
    .then((data) => {
      setStats(data);
    })
    .catch((err) => {
      console.error("Failed to load homepage statistics:", err);
    });
}, []);


  useEffect(() => {
    healthCheck()
      .then(() => {
        setBackendStatus("connected");
      })
      .catch(() => {
        setBackendStatus("disconnected");
      });
  }, []);

  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });

  useEffect(() => {
    Promise.all([api.publicStats(), api.jobs()])
      .then(([s, j]) => { setStats(s); setJobs(j.jobs || []); })
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
    if (localStorage.getItem("skillpulse_token")) api.me().then((r) => setUser(r.user)).catch(() => localStorage.removeItem("skillpulse_token"));
  }, []);

  const visibleJobs = useMemo(() => jobs.length ? jobs.slice(0, 6) : fallbackJobs, [jobs]);

  async function runSearch(e) {
    e?.preventDefault(); setLoading(true); setError("");
    try { const result = await api.jobs(search); setJobs(result.jobs || []); scrollTo("jobs"); }
    catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  async function handleAuth(form) {
    setError("");
    try {
      const result = authMode === "login" ? await api.login(form) : await api.register(form);
      if (authMode === "register") {
        const login = await api.login({ email: form.email, password: form.password });
        localStorage.setItem("skillpulse_token", login.access_token); setUser(login.user);
      } else { localStorage.setItem("skillpulse_token", result.access_token); setUser(result.user); }
      setAuthMode(null);
    } catch (err) { setError(err.message); }
  }

  if (user) return <Dashboard user={user} onLogout={() => { localStorage.removeItem("skillpulse_token"); setUser(null); }} />;

  return (
    <div className="app">
      <header className="navbar"><div className="nav-container">
        <div className="brand" onClick={() => scrollTo("home")}><div className="brand-icon">S</div><div><div className="brand-name">SkillPulse</div><div className="brand-tagline">WORK. MATCHED.</div></div></div>
        <nav className="nav-links"><button onClick={() => scrollTo("home")}>Home</button><button onClick={() => scrollTo("jobs")}>Find Jobs</button><button onClick={() => scrollTo("workers")}>Find Workers</button><button onClick={() => scrollTo("how-it-works")}>How It Works</button></nav>
        <div className="nav-actions"><button className="login-btn" onClick={() => setAuthMode("login")}>Login</button><button className="dark-btn" onClick={() => setAuthMode("register")}>Get Started</button></div>
        <button className="mobile-menu">☰</button>
      </div></header>

      <main>
        <section className="hero" id="home"><div className="hero-container"><div className="hero-content">
          <div className="eyebrow"><span></span>NEXT-DAY LABOUR MATCHING</div>
          <h1>The right worker.<br /><span>For the right job.</span><br />Tomorrow.</h1>
          <p className="hero-description">SkillPulse connects construction contractors with verified skilled daily-wage workers based on skill, location, availability, experience and reliability.</p>
          <div className="hero-buttons"><button className="primary-btn" onClick={() => setAuthMode("register")}>Find Skilled Workers <span>→</span></button><button className="secondary-btn" onClick={() => scrollTo("jobs")}>Find Jobs</button></div>
          <div className="hero-trust"><div className="trust-avatars"><span>👷</span><span>👨‍🔧</span><span>👨‍🎨</span><span>+</span></div><div><strong>Built for real-world work</strong><small>Real profiles, real availability, real matching.</small></div></div>
        </div><div className="hero-visual"><div className="hero-circle"></div><div className="worker-illustration"><div className="worker-head"></div><div className="worker-hat"></div><div className="worker-body"><div className="worker-logo">SP</div></div><div className="worker-arm left"></div><div className="worker-arm right"></div></div><div className="floating-card match-card"><div className="check-circle">✓</div><div><small>AI-assisted match</small><strong>Ranked worker</strong></div></div><div className="floating-card distance-card"><span className="location-dot">●</span><div><small>Location-aware</small><strong>Distance scored</strong></div></div><div className="floating-card available-card"><span>●</span> Availability checked</div></div></div></section>

        <section className="search-section"><form className="search-box" onSubmit={runSearch}><div className="search-field"><span className="field-icon">⌕</span><div><label>WHAT DO YOU NEED?</label><input value={search.skill} onChange={e => setSearch({ ...search, skill: e.target.value })} placeholder="Painter, Mason, Plumber..." /></div></div><div className="search-divider"></div><div className="search-field"><span className="field-icon">⌖</span><div><label>LOCATION</label><input value={search.area} onChange={e => setSearch({ ...search, area: e.target.value })} placeholder="Bengaluru area" /></div></div><div className="search-divider"></div><div className="search-field"><span className="field-icon">◷</span><div><label>WHEN?</label><strong>Upcoming jobs</strong></div></div><button className="search-btn">Search <span>→</span></button></form></section>

       <section className="stats-section">
  <div className="stats-container">
    <div className="stat">
      <strong>{stats.verified_workers}</strong>
      <span>Verified Workers</span>
    </div>

    <div className="stat">
      <strong>{stats.active_contractors}</strong>
      <span>Contractors</span>
    </div>

    <div className="stat">
      <strong>{stats.completed_jobs}</strong>
      <span>Jobs Completed</span>
    </div>

    <div className="stat">
      <strong>{stats.average_rating ?? "—"}</strong>
      <span>Average Rating</span>
    </div>
  </div>
</section>

        {error && <div className="inline-error">{error}</div>}
        <section className="jobs-section" id="jobs"><div className="section-container"><div className="section-heading-row"><div><div className="section-label">OPPORTUNITIES</div><h2>Jobs available <span>soon.</span></h2></div><button className="text-link" onClick={() => setAuthMode("login")}>Sign in to apply <span>→</span></button></div><div className="jobs-grid">
          {loading ? <div className="empty-panel">Loading live opportunities…</div> : visibleJobs.map((job) => <article className="job-card" key={job.id}><div className="job-card-top"><div className="job-icon">{icons[job.skill] || "👷"}</div><span className="job-tag">• {job.job_date === "Tomorrow" ? "Tomorrow" : formatDate(job.job_date)}</span></div><h3>{job.skill}</h3><p>{job.description || "Construction labour requirement posted on SkillPulse."}</p><div className="job-location"><span>⌖</span>{job.area_text || "Location provided after sign-in"}</div><div className="job-details"><div><small>DAILY WAGE</small><strong>₹{Number(job.wage || 0).toLocaleString("en-IN")}</strong></div><div><small>WORKING HOURS</small><strong>{job.working_hours || "Flexible"}</strong></div></div><button className="view-job" onClick={() => setAuthMode("login")}>View & apply <span>→</span></button></article>)}
        </div></div></section>

        <section className="how-section" id="how-it-works"><div className="section-container"><div className="center-heading"><div className="section-label">HOW IT WORKS</div><h2>From requirement<br /><span>to worker in three steps.</span></h2><p>SkillPulse digitizes the next-day labour search without losing the practical constraints that matter on a construction site.</p></div><div className="steps"><div className="step-card"><div className="step-number">01</div><div className="step-icon">✦</div><h3>Post a Job</h3><p>Contractors specify skill, wage, location, date and working hours.</p></div><div className="step-card featured-step"><div className="step-number">02</div><div className="step-icon light">✦</div><h3>Smart Matching</h3><p>Hard constraints remove unsuitable workers, then the model-supported ranking scores the remaining candidates.</p></div><div className="step-card"><div className="step-number">03</div><div className="step-icon">✓</div><h3>Get to Work</h3><p>Workers receive requests, accept suitable work and build a transparent reliability history.</p></div></div></div></section>

        <section className="worker-section" id="workers"><div className="section-container worker-content"><div><div className="section-label">FOR WORKERS</div><h2>Skilled workers deserve<br /><span>better opportunities.</span></h2><p>Find nearby jobs that match your skills, availability and preferred working distance.</p><ul className="benefit-list"><li><span>✓</span> Find jobs near you</li><li><span>✓</span> Know the wage before accepting</li><li><span>✓</span> Choose jobs for your availability</li></ul><button className="primary-btn" onClick={() => setAuthMode("register")}>Create worker account <span>→</span></button></div><div className="matching-card"><div className="matching-header"><div className="profile"><div className="profile-avatar">👷</div><div><strong>Transparent ranking</strong><small>Skill · distance · availability · reliability</small></div></div><span className="match-percent">AI</span></div><div className="progress-item"><div><span>Location</span><strong>Hard filter</strong></div><div className="progress"><span style={{ width: "88%" }}></span></div></div><div className="progress-item"><div><span>Experience</span><strong>Scored</strong></div><div className="progress"><span style={{ width: "76%" }}></span></div></div><div className="progress-item"><div><span>Reliability</span><strong>Model + history</strong></div><div className="progress"><span style={{ width: "92%" }}></span></div></div></div></div></section>

        <section className="cta-section" id="cta"><div className="cta-container"><div><div className="section-label orange-label">GET STARTED</div><h2>Ready to find the<br />right match?</h2><p>Whether you're hiring skilled labour or looking for your next job, SkillPulse brings both sides together.</p></div><div className="cta-buttons"><button className="primary-btn" onClick={() => setAuthMode("register")}>Create account <span>→</span></button><button className="cta-secondary" onClick={() => setAuthMode("login")}>Login</button></div></div></section>
      </main>

      <footer className="footer"><div className="footer-container"><div className="footer-brand"><div className="brand"><div className="brand-icon">S</div><div><div className="brand-name">SkillPulse</div><div className="brand-tagline">WORK. MATCHED.</div></div></div><p>Connecting skilled workers and contractors for<br />faster, better opportunities.</p></div><div className="footer-column"><h4>Platform</h4><button onClick={() => scrollTo("jobs")}>Find Jobs</button><button onClick={() => scrollTo("workers")}>Find Workers</button><button onClick={() => scrollTo("how-it-works")}>How It Works</button></div><div className="footer-column"><h4>Account</h4><button onClick={() => setAuthMode("login")}>Login</button><button onClick={() => setAuthMode("register")}>Register</button></div></div><div className="footer-bottom"><span>© 2026 SkillPulse. All rights reserved.</span><span>Built for real-world work.</span></div></footer>

      {authMode && <AuthModal mode={authMode} setMode={setAuthMode} onSubmit={handleAuth} error={error} />}
    </div>
  );

<div
  style={{
    position: "fixed",
    bottom: "15px",
    right: "15px",
    zIndex: 9999,
    padding: "8px 14px",
    borderRadius: "20px",
    background:
      backendStatus === "connected" ? "#16a34a" : "#dc2626",
    color: "white",
    fontSize: "12px",
    fontWeight: "600",
  }}
>
  Backend: {backendStatus}
</div>

}

function AuthModal({ mode, setMode, onSubmit, error }) {
  const [role, setRole] = useState("worker");
  const [form, setForm] = useState({ email: "", password: "", full_name: "", phone: "", company_name: "", contact_person: "", expected_wage: 0, experience_years: 0 });
  const update = (key, value) => setForm({ ...form, [key]: value });
  return <div className="modal-backdrop"><div className="auth-modal"><button className="modal-close" onClick={() => setMode(null)}>×</button><div className="section-label">SKILLPULSE ACCOUNT</div><h2>{mode === "login" ? "Welcome back." : "Create your account."}</h2><p>{mode === "login" ? "Sign in to access your live dashboard." : "Choose how you want to use SkillPulse."}</p>{mode === "register" && <div className="role-toggle"><button className={role === "worker" ? "active" : ""} onClick={() => setRole("worker")}>Worker</button><button className={role === "contractor" ? "active" : ""} onClick={() => setRole("contractor")}>Contractor</button></div>}<form onSubmit={e => { e.preventDefault(); onSubmit({ ...form, role }); }} className="auth-form"><input required type="email" placeholder="Email" value={form.email} onChange={e => update("email", e.target.value)} /><input required type="password" placeholder="Password (8+ chars, letters + numbers)" value={form.password} onChange={e => update("password", e.target.value)} />{mode === "register" && role === "worker" && <><input required placeholder="Full name" value={form.full_name} onChange={e => update("full_name", e.target.value)} /><input required placeholder="Phone" value={form.phone} onChange={e => update("phone", e.target.value)} /><div className="form-grid"><input type="number" min="0" placeholder="Expected wage/day" value={form.expected_wage} onChange={e => update("expected_wage", e.target.value)} /><input type="number" min="0" placeholder="Experience years" value={form.experience_years} onChange={e => update("experience_years", e.target.value)} /></div></>}{mode === "register" && role === "contractor" && <><input required placeholder="Company name" value={form.company_name} onChange={e => update("company_name", e.target.value)} /><input required placeholder="Contact person" value={form.contact_person} onChange={e => update("contact_person", e.target.value)} /><input required placeholder="Phone" value={form.phone} onChange={e => update("phone", e.target.value)} /></>}{error && <div className="form-error">{error}</div>}<button className="primary-btn full-btn" type="submit">{mode === "login" ? "Login" : "Create account"} <span>→</span></button></form><button className="switch-auth" onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "Need an account? Register" : "Already have an account? Login"}</button></div></div>;
}

function Dashboard({ user, onLogout }) {
const [stats, setStats] = useState({});
const [items, setItems] = useState([]);
const [applications, setApplications] = useState([]); 
const [notifications, setNotifications] = useState([]); const [profile, setProfile] = useState(null); const [selectedJob, setSelectedJob] = useState(null); const [recommendations, setRecommendations] = useState([]); const [message, setMessage] = useState(""); const [loading, setLoading] = useState(true);
  
  const worker = user.role === "worker";
  const admin = user.role === "admin";

  const load = async () => {
    setLoading(true);

    try {
      if (admin) {
        const s = await api.adminStats();
        setStats(s);
        setProfile(null);
        setNotifications([]);
        setItems([]);
        setApplications([]);
        return;
      }

      const [s, p, n] = await Promise.all([
        worker ? api.workerStats() : api.contractorStats(),
        worker ? api.workerProfile() : api.contractorProfile(),
        api.notifications(),
      ]);

      setStats(s);
      setProfile(p.profile);
      setNotifications(n.notifications || []);

      if (worker) {
        const [r, a] = await Promise.all([
          api.recommendedJobs(),
          api.workerApplications(),
        ]);
        setItems(r.jobs || []);
        setApplications(a.applications || []);
      } else {
        const r = await api.contractorJobs();
        setItems(r.jobs || []);
        setApplications([]);
      }
    } catch (e) {
      setMessage(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  async function action(fn, success="Done") { try { await fn(); setMessage(success); await load(); } catch(e) { setMessage(e.message); } }
  async function getRecommendations(job) { setSelectedJob(job); try { const r=await api.recommendations(job.id); setRecommendations(r.workers || []); } catch(e) { setMessage(e.message); } }
  return <div className="dashboard-shell"><header className="navbar"><div className="nav-container"><div className="brand"><div className="brand-icon">S</div><div><div className="brand-name">SkillPulse</div><div className="brand-tagline">WORK. MATCHED.</div></div></div>
  <div
  className="dashboard-user"
  style={{
    marginLeft: "auto",
    display: "flex",
    alignItems: "center",
    gap: "18px",
    visibility: "visible",
    opacity: 1,
    color: "#222"
  }}
>
  <span
    style={{
      display: "inline-block",
      color: "#f97316",
      fontSize: "12px",
      fontWeight: 700,
      textTransform: "uppercase",
      letterSpacing: "1px"
    }}
  >
    {user.role}
  </span>

  <strong
    style={{
      display: "inline-block",
      color: "#222",
      fontSize: "14px",
      fontWeight: 600
    }}
  >
    {user.email}
  </strong>

  <button
    type="button"
    title="Notifications"
    onClick={() => {
      document
        .getElementById("dashboard-notifications")
        ?.scrollIntoView({ behavior: "smooth" });
    }}
    style={{
      position: "relative",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      width: "42px",
      height: "42px",
      border: "1px solid #e5e0d8",
      borderRadius: "50%",
      background: "#ffffff",
      fontSize: "20px",
      cursor: "pointer"
    }}
  >
    🔔

    {notifications.filter((n) => !n.is_read).length > 0 && (
      <span
        style={{
          position: "absolute",
          top: "-3px",
          right: "-3px",
          minWidth: "19px",
          height: "19px",
          borderRadius: "50%",
          background: "#f97316",
          color: "#ffffff",
          fontSize: "10px",
          fontWeight: 800,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          border: "2px solid #ffffff"
        }}
      >
        {notifications.filter((n) => !n.is_read).length}
      </span>
    )}
  </button>

  <button
    type="button"
    onClick={onLogout}
    style={{
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "10px 18px",
      border: "1px solid #e5e0d8",
      borderRadius: "8px",
      background: "transparent",
      color: "#222",
      fontSize: "14px",
      fontWeight: 600,
      cursor: "pointer"
    }}
  >
    Logout
  </button>
</div>
</div></header><main className="dashboard-main"><div className="dashboard-head"><div><div className="section-label">{worker ? "WORKER DASHBOARD" : "CONTRACTOR DASHBOARD"}</div><h1>{worker ? "Your work, matched." : "Build your next crew."}</h1><p>{worker ? "Live recommendations are calculated from your profile and availability." : "Post requirements and review ranked workers from your live database."}</p></div></div>{message && <div className="inline-error">{message}</div>}<div className="dashboard-stats">{Object.entries(stats).slice(0,5).map(([k,v]) => <div className="dashboard-stat" key={k}><small>{k.replaceAll("_", " ")}</small><strong>{typeof v === "number" && k.includes("score") ? `${Math.round(v*100)}%` : v}</strong></div>)}</div>{user.role === "admin" ? (
  <AdminPanel
    stats={stats}
    message={setMessage}
  />
) : worker ? (
  <WorkerPanel
    items={items}
    profile={profile}
    applications={applications}
    notifications={notifications}
    action={action}
  />
) : (
  <ContractorPanel
    items={items}
    selectedJob={selectedJob}
    recommendations={recommendations}
    onSelect={getRecommendations}
    action={action}
    notifications={notifications}
  />
)}</main><div className="dashboard-footer">SkillPulse · live application data · model-assisted matching</div></div>;
}


function AdminPanel({ stats, message }) {
  const [workers, setWorkers] = useState([]);
  const [filter, setFilter] = useState("pending");
  const [loadingWorkers, setLoadingWorkers] = useState(false);
  const [error, setError] = useState("");

  async function loadWorkers() {
    setLoadingWorkers(true);
    setError("");

    try {
      const result = await api.adminWorkers(filter);
      setWorkers(result.workers || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingWorkers(false);
    }
  }

  useEffect(() => {
    loadWorkers();
  }, [filter]);

  async function updateVerification(workerId, status) {
    const actionText = status === "verified" ? "verify" : "reject";

    if (!window.confirm(`Are you sure you want to ${actionText} this worker?`)) {
      return;
    }

    try {
      await api.verifyWorker(workerId, status);
      message(`Worker ${status} successfully.`);
      await loadWorkers();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="dashboard-grid">
      <section className="dashboard-panel">
        <div className="section-label">ADMINISTRATION</div>
        <h2>Platform overview</h2>

        <div className="dashboard-stats">
          {Object.entries(stats).map(([key, value]) => (
            <div className="dashboard-stat" key={key}>
              <small>{key.replaceAll("_", " ")}</small>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="dashboard-panel">
        <div className="section-label">WORKER MANAGEMENT</div>
        <h2>Worker verification</h2>
        <p className="panel-description">
          Review worker profiles and update their verification status.
        </p>

        <div className="mini-form">
          <label>FILTER BY STATUS</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="pending">Pending verification</option>
            <option value="verified">Verified</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        {error && <div className="inline-error">{error}</div>}

        {loadingWorkers ? (
          <p>Loading workers...</p>
        ) : workers.length === 0 ? (
          <p>No workers found for this status.</p>
        ) : (
          <div className="worker-job-list">
            {workers.map((worker) => (
              <article className="worker-job-card" key={worker.id}>
                <div className="worker-job-main">
                  <div className="worker-job-info">
                    <h3>{worker.full_name || `Worker #${worker.id}`}</h3>
                    <p>Worker ID: {worker.id}</p>
                    <p>
                      Verification status:{" "}
                      <strong>{worker.verification_status}</strong>
                    </p>
                    {worker.area_text && <p>Area: {worker.area_text}</p>}
                    {worker.expected_wage != null && (
                      <p>Expected wage: ₹{worker.expected_wage}/day</p>
                    )}
                  </div>
                </div>

                {worker.verification_status !== "verified" && (
                  <button
                    className="primary-btn small-btn"
                    onClick={() => updateVerification(worker.id, "verified")}
                  >
                    Verify worker
                  </button>
                )}

                {worker.verification_status !== "rejected" && (
                  <button
                    className="secondary-btn small-btn"
                    onClick={() => updateVerification(worker.id, "rejected")}
                  >
                    Reject
                  </button>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}


function WorkerPanel({ items, profile, applications, notifications, action }) {
  const [skills, setSkills] = useState((profile?.skills || []).join(", "));
  const [date, setDate] = useState("");
  const [area, setArea] = useState(profile?.area_text || "Bengaluru");
  const [latitude, setLatitude] = useState(profile?.latitude ?? "12.9716");
  const [longitude, setLongitude] = useState(profile?.longitude ?? "77.5946");
  const [fullName, setFullName] = useState(profile?.full_name || "");
  const [phone, setPhone] = useState(profile?.phone || "");
  const [experience, setExperience] = useState(profile?.experience_years ?? 0);
  const [wage, setWage] = useState(profile?.expected_wage ?? 0);

  const today = new Date().toISOString().slice(0, 10);

  const saveProfile = () =>
    action(
      () => api.updateWorkerProfile({
        full_name: fullName,
        phone,
        experience_years: Number(experience),
        expected_wage: Number(wage),
      }),
      "Profile saved"
    );

  const saveSkills = () =>
    action(
      () => api.setSkills(skills.split(",").map((s) => s.trim()).filter(Boolean)),
      "Skills updated"
    );

  const saveLocation = () =>
    action(
      () => api.updateWorkerProfile({
        area_text: area,
        latitude: Number(latitude),
        longitude: Number(longitude),
      }),
      "Location saved"
    );

  const saveAvailability = () =>
    action(
      () => api.setAvailability(date, true),
      "Availability saved — refreshing your matches"
    );

  return (
    <div className="dashboard-grid contractor-dashboard-grid">
      <section className="dashboard-panel worker-recommendations-panel">
        <div className="panel-head">
          <div>
            <div className="section-label">AI-ASSISTED RECOMMENDATIONS</div>
            <h2>Jobs that fit you</h2>
          </div>
          <span className="match-count">{items.length} match{items.length === 1 ? "" : "es"}</span>
        </div>

        {items.length === 0 ? (
          <div className="worker-empty-panel">
            <div className="empty-icon">⌕</div>
            <strong>No matching jobs yet</strong>
            <p>Add at least one skill and mark yourself available for a job date to unlock personalized recommendations.</p>
          </div>
        ) : (
          <div className="worker-job-list">
            {items.map((j) => (
              <article className="worker-job-card" key={j.id}>
                <div className="worker-job-main">
                  <div className="worker-job-icon">{icons[j.skill] || "👷"}</div>
                  <div className="worker-job-info">
                    <div className="worker-job-title-row">
                      <h3>{j.skill}</h3>
                      <span className="match-badge">{Math.round(Number(j.match_score || 0))}% Match</span>
                    </div>
                    <p>{j.description || "Construction work requirement posted on SkillPulse."}</p>
                    <div className="worker-job-meta">
                      <span>⌖ {j.area_text || "Location provided"}</span>
                      <span>₹{Number(j.wage || 0).toLocaleString("en-IN")}/day</span>
                      <span>◷ {formatDate(j.job_date)}</span>
                    </div>
                    <div className="worker-reasons">
                      {(j.reasons || []).slice(0, 3).map((reason, i) => <span key={i}>✓ {reason}</span>)}
                    </div>
                  </div>
                </div>
                <button className="dark-btn small-btn" onClick={() => action(() => api.apply(j.id), "Application sent")}>Apply →</button>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="dashboard-panel worker-settings-panel">
        <div className="section-label">PROFILE SETTINGS</div>
        <h2>Keep your profile current.</h2>
        <p className="panel-description">Better profile data gives the matching engine more information to rank suitable work.</p>

        <div className="mini-form">
          <div className="worker-form-grid">
            <div><label>FULL NAME</label><input value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Your name" /></div>
            <div><label>PHONE</label><input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Phone number" /></div>
            <div><label>EXPERIENCE (YEARS)</label><input type="number" min="0" step="0.5" value={experience} onChange={(e) => setExperience(e.target.value)} /></div>
            <div><label>EXPECTED WAGE / DAY</label><input type="number" min="0" value={wage} onChange={(e) => setWage(e.target.value)} /></div>
          </div>
          <button className="dark-btn small-btn" onClick={saveProfile}>Save profile →</button>

          <div className="settings-divider" />
          <label>SKILLS</label>
          <input value={skills} onChange={(e) => setSkills(e.target.value)} placeholder="Painter, Mason, Plumber..." />
          <div className="profile-meta">
            {skills.split(",").map((s) => s.trim()).filter(Boolean).map((s) => <span key={s}>{s}</span>)}
          </div>
          <button className="secondary-btn small-btn" onClick={saveSkills} disabled={!skills.trim()}>Update skills</button>

          <div className="settings-divider" />
          <div className="section-label">WORK AREA</div>
          <input value={area} onChange={(e) => setArea(e.target.value)} placeholder="Area / City" />
          <div className="form-grid">
            <input type="number" step="any" value={latitude} onChange={(e) => setLatitude(e.target.value)} placeholder="Latitude" />
            <input type="number" step="any" value={longitude} onChange={(e) => setLongitude(e.target.value)} placeholder="Longitude" />
          </div>
          <button className="secondary-btn small-btn" onClick={saveLocation}>Save location</button>

          <div className="matching-note"><strong>✦ How matching works</strong><span>Skill fit, distance, availability and reliability are considered before recommendations are ranked.</span></div>
        </div>

        <div className="availability-box">
          <div className="section-label">AVAILABILITY</div>
          <h2>Tell us when you can work.</h2>
          <p className="panel-description">Mark yourself available for a date so contractors can include you in matching.</p>
          <div className="availability-row">
            <div><label>AVAILABLE DATE</label><input type="date" min={today} value={date} onChange={(e) => setDate(e.target.value)} /></div>
            <button className="primary-btn small-btn" disabled={!date} onClick={saveAvailability}>Save availability →</button>
          </div>
        </div>
      </section>

      <section className="dashboard-panel worker-applications-panel">
        <div className="panel-head">
          <div>
            <div className="section-label">MY APPLICATIONS</div>
            <h2>Track your work applications.</h2>
          </div>
          <span className="match-count">{applications.length} application{applications.length === 1 ? "" : "s"}</span>
        </div>
        {applications.length === 0 ? (
          <div className="worker-empty-panel compact-empty">
            <div className="empty-icon">⌕</div>
            <strong>No applications yet</strong>
            <p>When you apply for a recommended job, its status will appear here.</p>
          </div>
        ) : (
          <div className="worker-application-list">
            {applications.map((application) => {
              const job = application.job || {};
              const status = String(application.status || application.application_status || "PENDING").toUpperCase();
              const statusClass = status.toLowerCase().replace(/[^a-z_]/g, "-");
              return (
                <article className="worker-application-card" key={application.id || application.application_id}>
                  <div className="worker-application-main">
                    <div className="worker-job-icon">{icons[job.skill] || "👷"}</div>
                    <div>
                      <div className="worker-job-title-row">
                        <h3>{job.skill || "Construction job"}</h3>
                        <span className={`application-status ${statusClass}`}>{status}</span>
                      </div>
                      <p>{job.description || "Construction work requirement posted on SkillPulse."}</p>
                      <div className="worker-job-meta">
                        <span>⌖ {job.area_text || "Location provided"}</span>
                        <span>₹{Number(job.wage || 0).toLocaleString("en-IN")}/day</span>
                        <span>◷ {formatDate(job.job_date)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="application-footer">
                    {application.match_score !== null && application.match_score !== undefined && <span>Match score: <strong>{Math.round(Number(application.match_score))}%</strong></span>}
                    {application.applied_at && <span>Applied {formatDate(String(application.applied_at).slice(0, 10))}</span>}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="dashboard-panel worker-notifications-panel">
        <div className="panel-head">
          <div>
            <div className="section-label">NOTIFICATIONS</div>
            <h2>Stay on top of your work.</h2>
          </div>
          <span className="match-count">{notifications.filter((n) => !n.is_read).length} unread</span>
        </div>

        {notifications.length === 0 ? (
          <div className="worker-empty-panel compact-empty">
            <div className="empty-icon">◷</div>
            <strong>No notifications yet</strong>
            <p>Updates about applications and job decisions will appear here.</p>
          </div>
        ) : (
          <>
            <div className="notification-toolbar">
              {notifications.some((n) => !n.is_read) && (
                <button
                  className="secondary-btn small-btn"
                  onClick={() => action(() => api.markAllNotificationsRead(), "All notifications marked as read")}
                >
                  Mark all as read
                </button>
              )}
            </div>
            <div className="notification-list">
              {notifications.map((notification) => (
                <article className={`notification-card ${notification.is_read ? "read" : "unread"}`} key={notification.id}>
                  <div className="notification-icon">{notification.notif_type === "SELECTED" ? "✓" : notification.notif_type === "REJECTED" ? "×" : "•"}</div>
                  <div className="notification-content">
                    <div className="notification-title-row">
                      <strong>{notification.notif_type === "SELECTED" ? "Application selected" : notification.notif_type === "REJECTED" ? "Application update" : "SkillPulse update"}</strong>
                      {!notification.is_read && <span className="unread-dot">NEW</span>}
                    </div>
                    <p>{notification.message}</p>
                    <small>{notification.created_at ? new Date(notification.created_at).toLocaleString() : ""}</small>
                  </div>
                  {!notification.is_read && (
                    <button
                      className="text-action"
                      onClick={() => action(() => api.markNotificationRead(notification.id), "Notification marked as read")}
                    >
                      Mark read
                    </button>
                  )}
                </article>
              ))}
            </div>
          </>
        )}
               
        
</section>
    </div>
  );
}



           
   
function ContractorPanel({
  items,
  selectedJob,
  recommendations,
  onSelect,
  action,
  notifications,
}) {
  const [form, setForm] = useState({
    skill_name: "Painter",
    job_date: "",
    latitude: "12.9716",
    longitude: "77.5946",
    area_text: "Bengaluru",
    wage: "800",
    working_hours: "9:00 AM - 5:00 PM",
    workers_required: 1,
    min_experience: 0,
    description: "",
  });

  const [applications, setApplications] = useState([]);

  const [ratingApplication, setRatingApplication] = useState(null);
  const [ratingValue, setRatingValue] = useState(0);
  const [ratingComment, setRatingComment] = useState("");

  const set = (k, v) =>
    setForm({
      ...form,
      [k]: v,
    });

  const loadApplications = async () => {
    if (!selectedJob) {
      setApplications([]);
      return;
    }

    try {
  const result = await api.applications(selectedJob.id);

  console.log("APPLICATIONS RESPONSE:", result.applications);

  setApplications(result.applications || []);
} catch (e) {
  console.error("Failed to load applications:", e);
  setApplications([]);
}
  };
  useEffect(() => {
    loadApplications();
  }, [selectedJob]);

  const handleApplicationAction = async (
    applicationId,
    actionType,
    successMessage
  ) => {
    await action(
      async () => {
        await api.post(
          `/contractor/applications/${applicationId}/${actionType}`
        );

        await loadApplications();
      },
      successMessage
    );
  };

  return (
    <div className="dashboard-grid">

      {/* LEFT SIDE — JOBS */}
      <section className="dashboard-panel dashboard-panel">
        <div className="panel-head">
          <div>
            <div className="section-label">YOUR JOBS</div>
            <h2>Requirements</h2>
          </div>
        </div>

        <div className="contractor-create-card">

  <div className="contractor-create-header">
    <div>
      <div className="section-label">POST A REQUIREMENT</div>
      <h3>Find the right worker</h3>
      <p>
        Tell us what you need for tomorrow and SkillPulse will help match
        suitable workers.
      </p>
    </div>

    <div className="contractor-create-icon">＋</div>
  </div>

  <div className="contractor-form">

    <div className="contractor-field contractor-field-wide">
      <label>SKILL REQUIRED</label>
      <select
        value={form.skill_name}
        onChange={(e) => set("skill_name", e.target.value)}
      >
        <option value="Painter">Painter</option>
        <option value="Mason">Mason</option>
        <option value="Plumber">Plumber</option>
        <option value="Electrician">Electrician</option>
        <option value="Carpenter">Carpenter</option>
        <option value="Helper">Helper</option>
      </select>
    </div>

    <div className="contractor-field">
      <label>JOB DATE</label>
      <input
        type="date"
        value={form.job_date}
        onChange={(e) => set("job_date", e.target.value)}
      />
    </div>

    <div className="contractor-field">
      <label>WORKERS REQUIRED</label>

      <div className="worker-count-control">
        <button
          type="button"
          onClick={() =>
            set(
              "workers_required",
              Math.max(1, Number(form.workers_required) - 1)
            )
          }
        >
          −
        </button>

        <span>{form.workers_required}</span>

        <button
          type="button"
          onClick={() =>
            set(
              "workers_required",
              Math.min(50, Number(form.workers_required) + 1)
            )
          }
        >
          +
        </button>
      </div>
    </div>

    <div className="contractor-field contractor-field-wide">
      <label>WORK LOCATION</label>
      <input
        placeholder="Bengaluru area"
        value={form.area_text}
        onChange={(e) => set("area_text", e.target.value)}
      />
    </div>

    <div className="contractor-field">
      <label>DAILY WAGE</label>

      <div className="input-prefix">
        <span>₹</span>
        <input
          type="number"
          min="1"
          value={form.wage}
          onChange={(e) => set("wage", e.target.value)}
        />
      </div>
    </div>

    <div className="contractor-field">
      <label>MINIMUM EXPERIENCE</label>

      <div className="input-suffix">
        <input
          type="number"
          min="0"
          value={form.min_experience}
          onChange={(e) => set("min_experience", e.target.value)}
        />
        <span>years</span>
      </div>
    </div>

    <div className="contractor-field contractor-field-wide">
      <label>WORKING HOURS</label>
      <input
        value={form.working_hours}
        onChange={(e) => set("working_hours", e.target.value)}
        placeholder="9:00 AM - 5:00 PM"
      />
    </div>

    <div className="contractor-field contractor-field-wide">
      <label>JOB DESCRIPTION</label>

      <textarea
        rows="3"
        value={form.description}
        onChange={(e) => set("description", e.target.value)}
        placeholder="Describe the work, site requirements or anything the worker should know..."
      />
    </div>

  </div>

  <button
    className="contractor-post-btn"
    disabled={!form.job_date}
    onClick={() =>
      action(
        () =>
          api.createJob({
            ...form,
            wage: Number(form.wage),
            workers_required: Number(form.workers_required),
            min_experience: Number(form.min_experience),
            latitude: Number(form.latitude),
            longitude: Number(form.longitude),
          }),
        "Job posted"
      )
    }
  >
    Post requirement
    <span>→</span>
  </button>

</div>

        {items.length === 0 ? (
          <div className="empty-panel">
            No jobs yet. Use the API or add the job-posting form next.
          </div>
        ) : (
          items.map((j) => (
            <div className="contractor-job-card" key={j.id}>

  <div className="contractor-job-card-main">

    <div
        className="contractor-job-card-main"
        onClick={() => onSelect(j)}
        style={{ cursor: "pointer" }}
      >
    </div>

    <div className="contractor-job-info">

      <div className="contractor-job-title">
        <h3
            onClick={() => onSelect(j)}
            style={{ cursor: "pointer" }}
          >
            {j.skill}
        </h3>

        <span
          className={`contractor-status ${String(
            j.status || "MATCHING"
          ).toLowerCase()}`}
        >
          {String(j.status || "MATCHING").replaceAll("_", " ")}
        </span>
      </div>

      <div className="contractor-job-details">

        <span>
          📍 {j.area_text || "Location unavailable"}
        </span>

        <span>
          ₹{Number(j.wage || 0).toLocaleString("en-IN")}/day
        </span>

        <span>
          📅 {formatDate(j.job_date)}
        </span>

        <span>
          👷 {j.workers_required || 1} worker
          {Number(j.workers_required || 1) !== 1 ? "s" : ""}
        </span>

      </div>

    </div>

  </div>

  <div className="contractor-job-actions">

  {j.status === "MATCHING" && (
    <button
      className="dark-btn small-btn"
      onClick={() => onSelect(j)}
    >
      Find workers →
    </button>
  )}

  {j.status === "WORKER_SELECTED" && (
    <button
      className="contractor-confirm-btn"
      onClick={() =>
        action(
          () =>
            api.updateJobStatus(
              j.id,
              "CONFIRMED"
            ),
          "Job confirmed"
        )
      }
    >
      Confirm →
    </button>
  )}

  {j.status === "CONFIRMED" && (
  <button
    className="contractor-confirm-btn"
    onClick={() =>
      action(
        () => api.updateJobStatus(j.id, "IN_PROGRESS"),
        "Job marked as in progress"
      )
    }
  >
    Start job →
  </button>
)}

{j.status === "IN_PROGRESS" && (
  <button
    className="contractor-confirm-btn"
    onClick={() =>
      action(
        () => api.updateJobStatus(j.id, "COMPLETED"),
        "Job completed — you can now rate the worker"
      )
    }
  >
    Complete job ✓
  </button>
)}

  {j.status === "COMPLETED" && (
  <button
    className="contractor-complete-badge"
    onClick={() => onSelect(j)}
  >
    ✓ Completed · View
  </button>
)}

</div>

</div>
          ))
        )}
      </section>

      {/* RIGHT SIDE — MATCHING + APPLICATIONS */}
      <section className="dashboard-panel contractor-match-panel">

        {/* MATCH ENGINE */}
        <div className="section-label">
          MATCH ENGINE
        </div>

        <h2>
          {selectedJob
            ? `Ranked workers for ${selectedJob.skill}`
            : "Select a job"}
        </h2>

        {selectedJob && recommendations.length === 0 && (
          <div className="empty-panel">
            No eligible workers matched the hard filters.
          </div>
        )}

        {recommendations.map((w, index) => {
          const score = Number(w.match_score || 0);

const rankLabel =
  score >= 90
    ? "Top Match"
    : score >= 80
    ? "Strong Match"
    : score >= 70
    ? "Good Match"
    : "Match";

const rankIcon =
  index === 0
    ? "🥇"
    : index === 1
    ? "🥈"
    : index === 2
    ? "🥉"
    : "•";
  const breakdown = w.breakdown || {};
  const weights = {
  location: 0.30,
  experience: 0.20,
  wage: 0.20,
  reliability: 0.30,
};

const contribution = (score, weight) =>
  (Number(score || 0) * weight * 100).toFixed(1);

  const percentage = (value) =>
    Math.round(Number(value || 0) * 100);

  return (
    <div className="live-row match-worker-card" key={w.id}>

      <div className="match-worker-main">

        <div className="match-worker-header">

          <div className="worker-rank-badge">
  <span>{rankIcon}</span>
  {rankLabel}
</div>
          <div>
            <strong>{w.full_name}</strong>

            <small>
              {(w.skills || []).join(", ") || "Skill not listed"} ·{" "}
              {w.experience_years || 0} yrs ·{" "}
              {w.area_text || "Location unavailable"}
            </small>
          </div>

          <div className="match-score-circle">
            <b>{Math.round(Number(w.match_score || 0))}%</b>
            <span>MATCH</span>
          </div>
        </div>

        <div className="match-distance">
          📍 {breakdown.distance_km ?? "—"} km away
        </div>

        <div className="match-breakdown">

          <div className="match-breakdown-title">
            MATCH BREAKDOWN
          </div>

          <div className="match-factor">
            <div>
              <span>Location compatibility</span>
              <strong>
                {percentage(breakdown.location_score)}% · +
                {contribution(breakdown.location_score, weights.location)} pts
              </strong>
            </div>

            <div className="match-progress">
              <span
                style={{
                  width: `${percentage(breakdown.location_score)}%`,
                }}
              />
            </div>
          </div>

          <div className="match-factor">
            <div>
              <span>Experience compatibility</span>
                <strong>
                  {percentage(breakdown.experience_score)}% · +
                  {contribution(breakdown.experience_score, weights.experience)} pts
                </strong>
            </div>

            <div className="match-progress">
              <span
                style={{
                  width: `${percentage(breakdown.experience_score)}%`,
                }}
              />
            </div>
          </div>

          <div className="match-factor">
            <div>
              <span>Wage compatibility</span>
                <strong>
                  {percentage(breakdown.wage_score)}% · +
                  {contribution(breakdown.wage_score, weights.wage)} pts
                </strong>
            </div>

            <div className="match-progress">
              <span
                style={{
                  width: `${percentage(breakdown.wage_score)}%`,
                }}
              />
            </div>
          </div>

          <div className="match-factor">
            <div>
              <span>Reliability prediction</span>
                <strong>
                  {percentage(breakdown.reliability_score)}% · +
                  {contribution(breakdown.reliability_score, weights.reliability)} pts
                </strong> 
            </div>

            <div className="match-progress">
              <span
                style={{
                  width: `${percentage(breakdown.reliability_score)}%`,
                }}
              />
            </div>
          </div>

        </div>

        <div className="worker-match-reasons">
          {(w.reasons || []).slice(0, 4).map((reason, i) => (
            <span key={i}>✓ {reason}</span>
          ))}
        </div>

      </div>

      <div className="row-actions">
        <button
          className="dark-btn small-btn"
          onClick={() =>
            action(
              () => api.post(
                `/contractor/applications/worker/${w.id}`,
                { job_id: selectedJob.id }
              ),
              "Worker request sent"
            )
          }
        >
          Select →
        </button>
      </div>

    </div>
  );
})}

        {/* APPLICATIONS */}
        {selectedJob && (
          <>
            <div
              style={{
                marginTop: "32px",
                paddingTop: "24px",
                borderTop: "1px solid #e5e0d8",
              }}
            >
              <div className="section-label">
                APPLICATIONS
              </div>

              <h2>
                Applications
                {applications.length > 0 &&
                  ` · ${applications.length}`}
              </h2>
            </div>

            {applications.length === 0 ? (
              <div className="empty-panel">
                No applications received for this job yet.
              </div>
            ) : (
              applications.map((application) => (
                <div
                  className="contractor-application-card"
                  key={application.application_id}
                >
                  <div className="contractor-application-main">

                    <div className="contractor-application-avatar">
                      👷
                    </div>

                    <div className="contractor-application-info">

                      <div className="contractor-application-title">
                        <h3>{application.full_name}</h3>

                        <span
                          className={`contractor-application-status ${String(
                            application.application_status || "PENDING"
                          ).toLowerCase()}`}
                        >
                          {application.application_status || "PENDING"}
                        </span>
                      </div>

                      <div className="contractor-application-meta">
                        <span>
                          🛠️ {(application.skills || []).join(", ") ||
                            "Skills not listed"}
                        </span>

                        <span>
                          🎓 {application.experience_years || 0} yrs
                        </span>

                        <span>
                          📍 {application.area_text ||
                            "Location unavailable"}
                        </span>
                      </div>

                      {application.match_score !== null &&
                        application.match_score !== undefined && (
                          <div className="contractor-application-match">
                            Match score:
                            <strong>
                              {Math.round(Number(application.match_score))}%
                            </strong>
                          </div>
                        )}

                    </div>
                  </div>

                  <div className="contractor-application-actions">

                    {application.application_status === "PENDING" && (
                      <>
                        <button
                          className="contractor-select-btn"
                          onClick={() =>
                            handleApplicationAction(
                              application.application_id,
                              "select",
                              "Worker selected"
                            )
                          }
                        >
                          Select
                        </button>

                        <button
                          className="contractor-reject-btn"
                          onClick={() =>
                            handleApplicationAction(
                              application.application_id,
                              "reject",
                              "Application rejected"
                            )
                          }
                        >
                          Reject
                        </button>
                      </>
                    )}

                    {application.application_status === "SELECTED" && (
                      <span className="contractor-selected-badge">
                        ✓ Selected
                      </span>
                    )}

                    {application.application_status === "REJECTED" && (
                      <span className="contractor-rejected-badge">
                        Rejected
                      </span>
                    )}
                   {application.application_status === "COMPLETED" && (
  <>
    {application.has_rating ? (
      <span className="contractor-selected-badge">
        ✓ Worker Rated
      </span>
    ) : (
      <button
        type="button"
        className="contractor-rate-btn"
        onClick={() => {
          setRatingApplication(application);
          setRatingValue(0);
          setRatingComment("");
        }}
      >
        ⭐ Rate Worker
      </button>
    )}
  </>
)}
    


                  </div>
                </div>
              ))
            )}
          </>
                )}

        {/* NOTIFICATIONS */}
        <section
          id="dashboard-notifications"
          className="worker-notifications-panel"
          style={{ marginTop: "32px" }}
        >
          <div className="panel-head">
            <div>
              <div className="section-label">NOTIFICATIONS</div>
              <h2>Stay on top of your work.</h2>
            </div>

            <span className="match-count">
              {notifications.filter((n) => !n.is_read).length} unread
            </span>
          </div>

          {notifications.length === 0 ? (
            <div className="worker-empty-panel compact-empty">
              <div className="empty-icon">◷</div>

              <strong>No notifications yet</strong>

              <p>
                Updates about applications and worker decisions will appear
                here.
              </p>
            </div>
          ) : (
            <>
              <div className="notification-toolbar">
                {notifications.some((n) => !n.is_read) && (
                  <button
                    className="secondary-btn small-btn"
                    onClick={() =>
                      action(
                        () => api.markAllNotificationsRead(),
                        "All notifications marked as read"
                      )
                    }
                  >
                    Mark all as read
                  </button>
                )}
              </div>

              <div className="notification-list">
                {notifications.map((notification) => (
                  <article
                    className={`notification-card ${
                      notification.is_read ? "read" : "unread"
                    }`}
                    key={notification.id}
                  >
                    <div className="notification-icon">
                      {notification.notif_type === "SELECTED"
                        ? "✓"
                        : notification.notif_type === "REJECTED"
                        ? "×"
                        : "•"}
                    </div>

                    <div className="notification-content">
                      <div className="notification-title-row">
                        <strong>
                          {notification.notif_type === "SELECTED"
                            ? "Application selected"
                            : notification.notif_type === "REJECTED"
                            ? "Application update"
                            : "SkillPulse update"}
                        </strong>

                        {!notification.is_read && (
                          <span className="unread-dot">NEW</span>
                        )}
                      </div>

                      <p>{notification.message}</p>

                      <small>
                        {notification.created_at
                          ? new Date(
                              notification.created_at
                            ).toLocaleString()
                          : ""}
                      </small>
                    </div>

                    {!notification.is_read && (
                      <button
                        className="text-action"
                        onClick={() =>
                          action(
                            () =>
                              api.markNotificationRead(
                                notification.id
                              ),
                            "Notification marked as read"
                          )
                        }
                      >
                        Mark read
                      </button>
                    )}
                  </article>
                ))}
              </div>
            </>
          )}
                </section>

        {ratingApplication && (
          <div className="modal-backdrop">
            <div className="auth-modal rating-modal">

              <button
                type="button"
                className="modal-close"
                onClick={() => setRatingApplication(null)}
              >
                ×
              </button>

              <div className="section-label">
                WORKER FEEDBACK
              </div>

              <h2>
                Rate {ratingApplication.full_name}
              </h2>

              <p>
                How was your experience working with this worker?
              </p>

              <div className="rating-stars">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    className={star <= ratingValue ? "selected" : ""}
                    onClick={() => setRatingValue(star)}
                  >
                    ★
                  </button>
                ))}
              </div>

              <div className="rating-value">
                {ratingValue === 0
                  ? "Select a rating"
                  : `${ratingValue} out of 5`}
              </div>

              <textarea
                value={ratingComment}
                onChange={(e) => setRatingComment(e.target.value)}
                placeholder="Write a short review (optional)..."
                rows="4"
              />

              <button
                type="button"
                className="primary-btn full-btn"
                disabled={ratingValue === 0}
                onClick={async () => {
  alert("Submit button clicked!");

  try {
    const applicationId =
      ratingApplication.application_id || ratingApplication.id;

    alert("Application ID: " + applicationId);

    const result = await api.rateWorker(
      applicationId,
      ratingValue,
      ratingComment
    );

    console.log("RATING SUCCESS:", result);
    alert("Rating submitted successfully!");

    setRatingApplication(null);
    setRatingValue(0);
    setRatingComment("");

    await loadApplications();
  } catch (e) {
    console.error("RATING ERROR:", e);
    alert("RATING ERROR: " + e.message);
  }
}}
              >
                Submit rating →
              </button>

            </div>
          </div>
        )}

      </section>
    </div>
  );
}
      
  

export default App;
