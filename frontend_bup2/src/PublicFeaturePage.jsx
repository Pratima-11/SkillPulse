import React, { useEffect, useRef, useState } from "react";
import { api } from "./services/api";

const SKILLS = ["Painter", "Mason", "Plumber", "Electrician", "Carpenter", "Helper"];

function JobResults({ jobs, loading, error, onApply, onLogin }) {
  if (loading) return <p className="sp-state">Loading live jobs from SkillPulse…</p>;
  if (error) return <p className="sp-error" role="alert">{error}</p>;
  if (!jobs.length) return <p className="sp-state">No open jobs match these filters right now. Try another skill or area.</p>;
  return <div className="sp-job-grid">{jobs.map((job) => (
    <article className="sp-job-card" key={job.id}>
      <div className="sp-card-top"><span className="sp-chip">{job.skill || "Daily work"}</span><span>{job.job_date || "Date not specified"}</span></div>
      <h3>{job.title || job.skill || "Labour requirement"}</h3>
      <p>{job.description || "A contractor has posted this work requirement."}</p>
      <p className="sp-location">⌖ {job.area_text || "Location shared in job details"}</p>
      <div className="sp-job-meta"><strong>₹{Number(job.wage || 0).toLocaleString("en-IN")} <small>/ day</small></strong><span>{job.working_hours || "Hours to be confirmed"}</span></div>
      <button className="sp-primary" onClick={() => onApply(job)}>View / Apply</button>
    </article>
  ))}</div>;
}

export default function PublicFeaturePage({ page, onAuth, onSearchJobs }) {
  const [filters, setFilters] = useState({ skill: "", area: "", min_wage: "", date: "" });
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [language, setLanguage] = useState("en-IN");
  const [heardText, setHeardText] = useState("");
  const [voiceStatus, setVoiceStatus] = useState("");
  const recognitionRef = useRef(null);

  async function searchJobs(nextFilters = filters) {
    setLoading(true); setError("");
    try {
      const result = await api.jobs(nextFilters);
      setJobs(result.jobs || []);
    } catch (err) {
      setError(err.message || "Unable to load jobs. Check that the backend is running.");
    } finally { setLoading(false); }
  }

  useEffect(() => {
    if (page === "find-jobs") searchJobs({ skill: "", area: "", min_wage: "", date: "" });
    return () => {
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, [page]);

  function parseVoiceQuery(text) {
    const normalized = text.toLowerCase();
    const skill = SKILLS.find((item) => normalized.includes(item.toLowerCase())) || "";
    let area = "";
    const match = text.match(/(?:near|in|around)\s+(.+)$/i) || text.match(/(?:में|ನಲ್ಲಿ|ಹತ್ತಿರ)\s*(.+)$/i);
    if (match) area = match[1].trim().replace(/[.!?]+$/, "");
    return { ...filters, skill, area };
  }

  function startVoiceSearch() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceStatus("Voice recognition is not supported in this browser. Please use the text search below.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = language;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognitionRef.current = recognition;
    setVoiceStatus("Listening… Please say a skill and optionally an area.");
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript || "";
      setHeardText(transcript);
      const parsed = parseVoiceQuery(transcript);
      setFilters(parsed);
      setVoiceStatus("I heard your request. Review the filters and search.");
    };
    recognition.onerror = (event) => setVoiceStatus(`Voice input error: ${event.error}. You can use typed search instead.`);
    recognition.onend = () => recognitionRef.current = null;
    recognition.start();
  }

  function stopVoiceSearch() {
    recognitionRef.current?.stop();
    setVoiceStatus("Voice input stopped.");
  }

  if (page === "find-jobs") return (
    <section className="sp-page">
      <div className="sp-page-heading"><span className="sp-eyebrow">LIVE OPPORTUNITIES</span><h1>Find your next <em>job.</em></h1><p>Search real open requirements posted by SkillPulse contractors.</p></div>
      <form className="sp-filter-panel" onSubmit={(e) => { e.preventDefault(); searchJobs(); }}>
        <label>Skill<select value={filters.skill} onChange={(e) => setFilters({ ...filters, skill: e.target.value })}><option value="">All skills</option>{SKILLS.map((s) => <option key={s}>{s}</option>)}</select></label>
        <label>Area<input value={filters.area} onChange={(e) => setFilters({ ...filters, area: e.target.value })} placeholder="e.g. KR Puram" /></label>
        <label>Minimum daily wage<input type="number" min="0" value={filters.min_wage} onChange={(e) => setFilters({ ...filters, min_wage: e.target.value })} placeholder="₹" /></label>
        <label>Job date<input type="date" value={filters.date} onChange={(e) => setFilters({ ...filters, date: e.target.value })} /></label>
        <button className="sp-primary" type="submit">Search jobs</button>
      </form>
      <JobResults jobs={jobs} loading={loading} error={error} onApply={() => onAuth("login")} />
      <p className="sp-note">Applying requires a worker account and sign-in. Eligibility is checked by the existing SkillPulse backend.</p>
    </section>
  );

  if (page === "find-workers") return (
    <section className="sp-page">
      <div className="sp-page-heading"><span className="sp-eyebrow">FOR CONTRACTORS</span><h1>Find the right <em>workers.</em></h1><p>SkillPulse ranks eligible workers for each job using your existing matching engine.</p></div>
      <div className="sp-info-panel"><div className="sp-icon">✦</div><div><h2>Job-specific worker recommendations</h2><p>Sign in as a contractor, open one of your posted jobs and choose its recommended workers. SkillPulse applies skill and availability requirements, location constraints and the configured ranking weights.</p><button className="sp-primary" onClick={() => onAuth("login")}>Contractor sign in</button></div></div>
      <div className="sp-three-grid"><article><b>01</b><h3>Post a requirement</h3><p>Set the skill, work date, area, wage and number of workers.</p></article><article><b>02</b><h3>Review ranked matches</h3><p>See eligible candidates and their existing match explanations.</p></article><article><b>03</b><h3>Manage applications</h3><p>Use the contractor dashboard to select, reject or manage workers.</p></article></div>
      <p className="sp-note">Worker profiles are not exposed in a public directory. Recommendations are available through authenticated contractor job workflows.</p>
    </section>
  );

  if (page === "how-it-works") return (
    <section className="sp-page">
      <div className="sp-page-heading"><span className="sp-eyebrow">A CLEARER WAY TO HIRE</span><h1>How SkillPulse <em>works.</em></h1><p>From a labour requirement to a suitable next-day match.</p></div>
      <div className="sp-process-list">
        <article><span>01</span><div><h2>Contractor posts a job</h2><p>The contractor enters the required skill, work location, date, daily wage, working hours and number of workers.</p></div></article>
        <article><span>02</span><div><h2>SkillPulse checks eligibility</h2><p>Workers are filtered against hard requirements such as skill and availability. Location and other configured factors contribute to ranking.</p></div></article>
        <article><span>03</span><div><h2>Workers receive opportunities</h2><p>Workers can review recommended jobs and apply through their authenticated account.</p></div></article>
        <article><span>04</span><div><h2>Contractor manages the match</h2><p>Contractors review recommendations and applications, select workers and manage job progress.</p></div></article>
        <article><span>05</span><div><h2>Feedback improves transparency</h2><p>After work is completed, ratings and work history contribute to the platform's reliability information.</p></div></article>
      </div>
    </section>
  );

  if (page === "ai-voice-assistant") return (
    <section className="sp-page">
      <div className="sp-page-heading"><span className="sp-eyebrow">VOICE-ENABLED JOB SEARCH</span><h1>Speak. Search. <em>Find work.</em></h1><p>Use your voice or type a request to find open SkillPulse jobs.</p></div>
      <div className="sp-voice-panel">
        <label>Recognition language<select value={language} onChange={(e) => setLanguage(e.target.value)}><option value="en-IN">English (India)</option><option value="hi-IN">Hindi</option><option value="kn-IN">Kannada</option></select></label>
        <div className="sp-voice-actions"><button className="sp-primary" onClick={startVoiceSearch}>🎙 Start voice search</button><button className="sp-secondary" onClick={stopVoiceSearch}>Stop listening</button></div>
        <p className="sp-voice-status" aria-live="polite">{voiceStatus || "Example: “Painter jobs near KR Puram”."}</p>
        {heardText && <p><strong>Recognized:</strong> {heardText}</p>}
        <form className="sp-filter-panel sp-voice-filters" onSubmit={(e) => { e.preventDefault(); searchJobs(); }}>
          <label>Skill<select value={filters.skill} onChange={(e) => setFilters({ ...filters, skill: e.target.value })}><option value="">All skills</option>{SKILLS.map((s) => <option key={s}>{s}</option>)}</select></label>
          <label>Area<input value={filters.area} onChange={(e) => setFilters({ ...filters, area: e.target.value })} placeholder="Enter area" /></label>
          <button className="sp-primary" type="submit">Search live jobs</button>
        </form>
      </div>
      <JobResults jobs={jobs} loading={loading} error={error} onApply={() => onAuth("login")} />
      <p className="sp-note">Voice recognition depends on browser support and microphone permission. This module performs voice-enabled search; it is not a generative conversational voice agent.</p>
    </section>
  );

  return null;
}
