import React, { useEffect, useMemo, useState } from "react";
import "./App.css";
import { api } from "./api";

const fallbackJobs = [
  { id: "demo-1", icon: "🎨", skill: "Painter", description: "Interior wall painting for residential property", area_text: "Kumaraswamy Layout, Bengaluru", wage: 800, working_hours: "9:00 AM – 5:00 PM", job_date: "Tomorrow" },
  { id: "demo-2", icon: "🧱", skill: "Mason", description: "Brickwork and construction assistance required", area_text: "JP Nagar, Bengaluru", wage: 950, working_hours: "8:30 AM – 5:30 PM", job_date: "Tomorrow" },
  { id: "demo-3", icon: "🔧", skill: "Plumber", description: "Residential plumbing and pipe installation", area_text: "HSR Layout, Bengaluru", wage: 900, working_hours: "9:00 AM – 4:30 PM", job_date: "Tomorrow" },
];

const icons = { Painter: "🎨", Mason: "🧱", Plumber: "🔧", Electrician: "⚡", Carpenter: "🪚", Helper: "👷" };
const emptyStats = { verified_workers: 0, contractors: 0, jobs_completed: 0, average_rating: null, open_jobs: 0 };

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

        <section className="stats-section"><div className="stats-container"><div className="stat"><strong>{stats.verified_workers}</strong><span>Verified Workers</span></div><div className="stat"><strong>{stats.contractors}</strong><span>Contractors</span></div><div className="stat"><strong>{stats.jobs_completed}</strong><span>Jobs Completed</span></div><div className="stat"><strong>{stats.average_rating ?? "—"}</strong><span>Average Rating</span></div></div></section>

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
}

function AuthModal({ mode, setMode, onSubmit, error }) {
  const [role, setRole] = useState("worker");
  const [form, setForm] = useState({ email: "", password: "", full_name: "", phone: "", company_name: "", contact_person: "", expected_wage: 0, experience_years: 0 });
  const update = (key, value) => setForm({ ...form, [key]: value });
  return <div className="modal-backdrop"><div className="auth-modal"><button className="modal-close" onClick={() => setMode(null)}>×</button><div className="section-label">SKILLPULSE ACCOUNT</div><h2>{mode === "login" ? "Welcome back." : "Create your account."}</h2><p>{mode === "login" ? "Sign in to access your live dashboard." : "Choose how you want to use SkillPulse."}</p>{mode === "register" && <div className="role-toggle"><button className={role === "worker" ? "active" : ""} onClick={() => setRole("worker")}>Worker</button><button className={role === "contractor" ? "active" : ""} onClick={() => setRole("contractor")}>Contractor</button></div>}<form onSubmit={e => { e.preventDefault(); onSubmit({ ...form, role }); }} className="auth-form"><input required type="email" placeholder="Email" value={form.email} onChange={e => update("email", e.target.value)} /><input required type="password" placeholder="Password (8+ chars, letters + numbers)" value={form.password} onChange={e => update("password", e.target.value)} />{mode === "register" && role === "worker" && <><input required placeholder="Full name" value={form.full_name} onChange={e => update("full_name", e.target.value)} /><input required placeholder="Phone" value={form.phone} onChange={e => update("phone", e.target.value)} /><div className="form-grid"><input type="number" min="0" placeholder="Expected wage/day" value={form.expected_wage} onChange={e => update("expected_wage", e.target.value)} /><input type="number" min="0" placeholder="Experience years" value={form.experience_years} onChange={e => update("experience_years", e.target.value)} /></div></>}{mode === "register" && role === "contractor" && <><input required placeholder="Company name" value={form.company_name} onChange={e => update("company_name", e.target.value)} /><input required placeholder="Contact person" value={form.contact_person} onChange={e => update("contact_person", e.target.value)} /><input required placeholder="Phone" value={form.phone} onChange={e => update("phone", e.target.value)} /></>}{error && <div className="form-error">{error}</div>}<button className="primary-btn full-btn" type="submit">{mode === "login" ? "Login" : "Create account"} <span>→</span></button></form><button className="switch-auth" onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "Need an account? Register" : "Already have an account? Login"}</button></div></div>;
}

function Dashboard({ user, onLogout }) {
  const [stats, setStats] = useState({}); const [items, setItems] = useState([]); const [notifications, setNotifications] = useState([]); const [profile, setProfile] = useState(null); const [selectedJob, setSelectedJob] = useState(null); const [recommendations, setRecommendations] = useState([]); const [message, setMessage] = useState(""); const [loading, setLoading] = useState(true);
  const worker = user.role === "worker";
  const load = async () => { setLoading(true); try { const [s,p,n] = await Promise.all([worker ? api.workerStats() : api.contractorStats(), worker ? api.workerProfile() : api.contractorProfile(), api.notifications()]); setStats(s); setProfile(p.profile); setNotifications(n.notifications || []); if (worker) { const r=await api.recommendedJobs(); setItems(r.jobs || []); } else { const r=await api.contractorJobs(); setItems(r.jobs || []); } } catch(e) { setMessage(e.message); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);
  async function action(fn, success="Done") { try { await fn(); setMessage(success); await load(); } catch(e) { setMessage(e.message); } }
  async function getRecommendations(job) { setSelectedJob(job); try { const r=await api.recommendations(job.id); setRecommendations(r.workers || []); } catch(e) { setMessage(e.message); } }
  return <div className="dashboard-shell"><header className="navbar"><div className="nav-container"><div className="brand"><div className="brand-icon">S</div><div><div className="brand-name">SkillPulse</div><div className="brand-tagline">WORK. MATCHED.</div></div></div><div className="dashboard-user"><span>{user.role}</span><strong>{user.email}</strong><button className="login-btn" onClick={onLogout}>Logout</button></div></div></header><main className="dashboard-main"><div className="dashboard-head"><div><div className="section-label">{worker ? "WORKER DASHBOARD" : "CONTRACTOR DASHBOARD"}</div><h1>{worker ? "Your work, matched." : "Build your next crew."}</h1><p>{worker ? "Live recommendations are calculated from your profile and availability." : "Post requirements and review ranked workers from your live database."}</p></div></div>{message && <div className="inline-error">{message}</div>}<div className="dashboard-stats">{Object.entries(stats).slice(0,5).map(([k,v]) => <div className="dashboard-stat" key={k}><small>{k.replaceAll("_", " ")}</small><strong>{typeof v === "number" && k.includes("score") ? `${Math.round(v*100)}%` : v}</strong></div>)}</div>{worker ? <WorkerPanel items={items} profile={profile} action={action} /> : <ContractorPanel items={items} selectedJob={selectedJob} recommendations={recommendations} onSelect={getRecommendations} action={action} />}</main><div className="dashboard-footer">SkillPulse · live application data · model-assisted matching</div></div>;
}

function WorkerPanel({ items, profile, action }) { const [skills,setSkills]=useState((profile?.skills||[]).join(", ")); const [date,setDate]=useState(""); return <div className="dashboard-grid"><section className="dashboard-panel"><div className="panel-head"><div><div className="section-label">RECOMMENDED JOBS</div><h2>Jobs that fit you</h2></div></div>{items.length===0?<div className="empty-panel">No currently eligible jobs. Add skills and availability to unlock matching.</div>:items.map(j=><div className="live-row" key={j.id}><div><strong>{j.skill}</strong><small>{j.area_text || "Location set by contractor"} · ₹{Number(j.wage).toLocaleString("en-IN")}/day · {formatDate(j.job_date)}</small><span className="reason-line">{(j.reasons || []).slice(0,3).join(" · ")}</span></div><div className="row-actions"><b>{Math.round(j.match_score)}%</b><button className="dark-btn small-btn" onClick={()=>action(()=>api.apply(j.id),"Application sent")}>Apply</button></div></div>)}</section><section className="dashboard-panel"><div className="section-label">PROFILE</div><h2>{profile?.full_name || "Worker"}</h2><div className="profile-meta">{(profile?.skills || []).map(s=><span key={s}>{s}</span>)}</div><p>Experience: {profile?.experience_years || 0} years</p><p>Expected wage: ₹{Number(profile?.expected_wage || 0).toLocaleString("en-IN")}/day</p><p>Reliability: {Math.round((profile?.reliability_score || 0)*100)}%</p><p>Verification: {profile?.verification_status}</p><div className="mini-form"><input value={skills} onChange={e=>setSkills(e.target.value)} placeholder="Skills, comma separated"/><button className="secondary-btn small-btn" onClick={()=>action(()=>api.setSkills(skills.split(",").map(s=>s.trim()).filter(Boolean)),"Skills updated")}>Update skills</button><input type="date" value={date} onChange={e=>setDate(e.target.value)}/><button className="secondary-btn small-btn" disabled={!date} onClick={()=>action(()=>api.availability({available_date:date,is_available:true}),"Availability saved")}>Mark available</button></div></section></div>; }

function ContractorPanel({ items, selectedJob, recommendations, onSelect, action }) { const [form,setForm]=useState({skill_name:"Painter",job_date:"",latitude:"12.9716",longitude:"77.5946",area_text:"Bengaluru",wage:"800",working_hours:"9:00 AM - 5:00 PM",workers_required:1,min_experience:0,description:""}); const set=(k,v)=>setForm({...form,[k]:v}); return <div className="dashboard-grid"><section className="dashboard-panel"><div className="panel-head"><div><div className="section-label">YOUR JOBS</div><h2>Requirements</h2></div></div><div className="job-create"><input placeholder="Skill" value={form.skill_name} onChange={e=>set("skill_name",e.target.value)}/><input type="date" value={form.job_date} onChange={e=>set("job_date",e.target.value)}/><input placeholder="Area" value={form.area_text} onChange={e=>set("area_text",e.target.value)}/><div className="form-grid"><input type="number" min="1" placeholder="Wage/day" value={form.wage} onChange={e=>set("wage",e.target.value)}/><input type="number" min="1" placeholder="Workers" value={form.workers_required} onChange={e=>set("workers_required",e.target.value)}/></div><input placeholder="Working hours" value={form.working_hours} onChange={e=>set("working_hours",e.target.value)}/><input placeholder="Minimum experience (years)" value={form.min_experience} onChange={e=>set("min_experience",e.target.value)}/><button className="primary-btn small-btn" disabled={!form.job_date} onClick={()=>action(()=>api.createJob({...form,wage:Number(form.wage),workers_required:Number(form.workers_required),min_experience:Number(form.min_experience),latitude:Number(form.latitude),longitude:Number(form.longitude)}),"Job posted")}>Post requirement <span>→</span></button></div>{items.length===0?<div className="empty-panel">No jobs yet. Use the API or add the job-posting form next.</div>:items.map(j=><div className="live-row" key={j.id}><div><strong>{j.skill}</strong><small>{j.area_text || "Location"} · ₹{Number(j.wage).toLocaleString("en-IN")}/day · {formatDate(j.job_date)}</small><span className="reason-line">Status: {j.status}</span></div><div className="row-actions"><button className="dark-btn small-btn" onClick={()=>onSelect(j)}>Find workers</button>{j.status==="WORKER_SELECTED" && <button className="secondary-btn small-btn" onClick={()=>action(()=>api.updateJobStatus(j.id,"CONFIRMED"),"Job confirmed")}>Confirm</button>}</div></div>)}</section><section className="dashboard-panel"><div className="section-label">MATCH ENGINE</div><h2>{selectedJob ? `Ranked workers for ${selectedJob.skill}` : "Select a job"}</h2>{selectedJob && recommendations.length===0 && <div className="empty-panel">No eligible workers matched the hard filters.</div>}{recommendations.map(w=><div className="live-row" key={w.id}><div><strong>{w.full_name}</strong><small>{(w.skills||[]).join(", ")} · {w.experience_years} yrs · {w.area_text || "Location unavailable"}</small><span className="reason-line">{(w.reasons||[]).slice(0,4).join(" · ")}</span></div><div className="row-actions"><b>{Math.round(w.match_score)}%</b></div></div>)}</section></div>; }

export default App;
