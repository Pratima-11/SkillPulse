import React, { useState } from "react";
import "./App.css";

// --- DATA ---
const jobsData = [
  {
    id: 1,
    icon: "🎨",
    title: "Painter",
    description: "Interior wall painting for high-end residential property.",
    location: "Kumaraswamy Layout, Bengaluru",
    wage: "₹800",
    hours: "9:00 AM – 5:00 PM",
    tag: "Tomorrow",
    category: "Painting",
  },
  {
    id: 2,
    icon: "🧱",
    title: "Mason",
    description: "Precision brickwork and foundation construction assistance.",
    location: "JP Nagar, Bengaluru",
    wage: "₹950",
    hours: "8:30 AM – 5:30 PM",
    tag: "Tomorrow",
    category: "Construction",
  },
  {
    id: 3,
    icon: "🔧",
    title: "Plumber",
    description: "Residential plumbing overhaul and pipe fitting installation.",
    location: "HSR Layout, Bengaluru",
    wage: "₹900",
    hours: "9:00 AM – 4:30 PM",
    tag: "Tomorrow",
    category: "Plumbing",
  },
];

const stats = [
  { value: "1,200+", label: "Verified Workers" },
  { value: "300+", label: "Active Contractors" },
  { value: "2,400+", label: "Jobs Completed" },
  { value: "4.9/5", label: "Worker Rating" },
];

// --- PAGE COMPONENTS ---

function HomePage({ navigateTo }) {
  return (
    <>
      {/* HERO SECTION */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="eyebrow-badge">
              <span className="pulse-dot"></span>
              <span className="eyebrow-text">NEXT-DAY LABOUR MATCHING</span>
            </div>

            <h1 className="hero-title">
              The right worker.
              <br />
              <span className="highlight-text">For the right job.</span>
              <br />
              Tomorrow.
            </h1>

            <p className="hero-description">
              SkillPulse connects construction contractors with verified, skilled daily-wage workers 
              based on real-time availability, proximity, and reliability metrics.
            </p>

            <div className="hero-actions">
              <button className="btn-accent" onClick={() => navigateTo("find-workers")}>
                Find Skilled Workers
                <span className="arrow-icon">→</span>
              </button>

              <button className="btn-outline" onClick={() => navigateTo("find-jobs")}>
                Explore Jobs
              </button>
            </div>

            <div className="hero-trust-bar">
              <div className="avatar-group">
                <span className="avatar">👷</span>
                <span className="avatar">👨‍🔧</span>
                <span className="avatar">👨‍🎨</span>
                <span className="avatar avatar-more">+</span>
              </div>
              <div className="trust-info">
                <strong>Built for real-world work</strong>
                <small>Connecting workers and contractors in under 2 minutes.</small>
              </div>
            </div>
          </div>

          {/* HERO VISUAL */}
          <div className="hero-visual">
            <div className="visual-background-glow"></div>
            
            <div className="hero-card-glow">
              <div className="worker-avatar-frame">
                <div className="worker-badge-status">
                  <span className="status-dot"></span> Available
                </div>
                <div className="illustration-avatar">👷‍♂️</div>
              </div>
            </div>

            {/* FLOATING GLASS CARDS */}
            <div className="floating-card match-card glass-morphism">
              <div className="check-icon-circle">✓</div>
              <div>
                <small className="card-label">AI Match Confidence</small>
                <strong className="card-val">94% Match Score</strong>
              </div>
            </div>

            <div className="floating-card distance-card glass-morphism">
              <div className="pulse-pin">📍</div>
              <div>
                <small className="card-label">Proximity</small>
                <strong className="card-val">2.4 km nearby</strong>
              </div>
            </div>

            <div className="floating-card status-card glass-morphism">
              <span className="green-dot">●</span> Next-Day Ready
            </div>
          </div>
        </div>
      </section>

      {/* STATS */}
      <section className="stats-section">
        <div className="stats-grid">
          {stats.map((stat, idx) => (
            <div className="stat-card" key={idx}>
              <h3 className="stat-value">{stat.value}</h3>
              <p className="stat-label">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="cta-banner">
          <div className="cta-content">
            <span className="section-badge orange">READY TO START?</span>
            <h2>Transform your daily hiring process today.</h2>
            <p>Connect with reliable workforce or secure steady work with zero hassle.</p>
          </div>
          <div className="cta-buttons">
            <button className="btn-accent" onClick={() => navigateTo("find-workers")}>
              Hire Skilled Labor →
            </button>
            <button className="btn-ghost-light" onClick={() => navigateTo("find-jobs")}>
              Find Jobs
            </button>
          </div>
        </div>
      </section>
    </>
  );
}

function FindJobsPage() {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredJobs = jobsData.filter((job) =>
    job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    job.location.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div style={{ paddingTop: "40px" }}>
      {/* SEARCH BAR */}
      <section className="search-section">
        <div className="search-card glass-morphism">
          <div className="search-input-group">
            <span className="search-icon">🔍</span>
            <div className="input-block">
              <label>WHAT DO YOU NEED?</label>
              <input
                type="text"
                placeholder="Painter, Mason, Plumber..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          <div className="divider"></div>

          <div className="search-input-group">
            <span className="search-icon">📍</span>
            <div className="input-block">
              <label>LOCATION</label>
              <input type="text" defaultValue="Bengaluru, KA" />
            </div>
          </div>

          <div className="divider"></div>

          <div className="search-input-group">
            <span className="search-icon">📅</span>
            <div className="input-block">
              <label>WHEN?</label>
              <input type="text" defaultValue="Tomorrow Morning" />
            </div>
          </div>

          <button className="btn-search">
            Search Matches <span>→</span>
          </button>
        </div>
      </section>

      {/* JOBS SECTION */}
      <section className="jobs-section">
        <div className="section-container">
          <div className="section-header-flex">
            <div>
              <span className="section-badge">OPPORTUNITIES</span>
              <h2 className="section-title">
                Available Jobs <span>Tomorrow.</span>
              </h2>
            </div>
          </div>

          <div className="jobs-grid">
            {filteredJobs.map((job) => (
              <article className="job-card-modern" key={job.id}>
                <div className="job-card-header">
                  <div className="job-icon-box">{job.icon}</div>
                  <span className="job-status-pill">{job.tag}</span>
                </div>

                <h3 className="job-title">{job.title}</h3>
                <p className="job-description">{job.description}</p>

                <div className="job-location">
                  <span className="loc-icon">📍</span>
                  <span>{job.location}</span>
                </div>

                <div className="job-metrics">
                  <div className="metric-col">
                    <small>DAILY WAGE</small>
                    <strong>{job.wage}</strong>
                  </div>
                  <div className="metric-col">
                    <small>HOURS</small>
                    <strong>{job.hours}</strong>
                  </div>
                </div>

                <button className="btn-card-action">
                  Apply / Accept <span>→</span>
                </button>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function FindWorkersPage() {
  return (
    <section className="worker-section">
      <div className="section-container grid-two-col">
        <div className="worker-info-side">
          <span className="section-badge">FOR WORKERS & CONTRACTORS</span>
          <h2 className="section-title">
            Skilled workers deserve <br />
            <span>better opportunities.</span>
          </h2>
          <p className="section-desc">
            Find nearby verified construction jobs matching your daily schedule and wage expectations.
          </p>

          <ul className="check-list">
            <li><span className="check">✓</span> Guaranteed transparent pay scales</li>
            <li><span className="check">✓</span> Proximity-based job matching</li>
            <li><span className="check">✓</span> Next-day shift confirmation</li>
          </ul>

          <button className="btn-accent">Find Opportunities →</button>
        </div>

        {/* MATCHING CARD */}
        <div className="matching-preview-card glass-morphism">
          <div className="profile-header">
            <div className="profile-avatar">👨‍🏭</div>
            <div className="profile-details">
              <strong>Rajesh Kumar</strong>
              <small>Painter • 4+ Years Exp</small>
            </div>
            <span className="score-badge">94%</span>
          </div>

          <div className="metric-bars">
            <div className="bar-group">
              <div className="bar-info"><span>Skill Compatibility</span><strong>96%</strong></div>
              <div className="bar-track"><div className="bar-fill" style={{ width: "96%" }}></div></div>
            </div>

            <div className="bar-group">
              <div className="bar-info"><span>Distance Proximity</span><strong>91%</strong></div>
              <div className="bar-track"><div className="bar-fill" style={{ width: "91%" }}></div></div>
            </div>

            <div className="bar-group">
              <div className="bar-info"><span>Reliability Score</span><strong>95%</strong></div>
              <div className="bar-track"><div className="bar-fill" style={{ width: "95%" }}></div></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorksPage() {
  return (
    <section className="how-section">
      <div className="section-container">
        <div className="center-header">
          <span className="section-badge">HOW IT WORKS</span>
          <h2 className="section-title">
            From requirement <br />
            <span>to worker in 3 steps.</span>
          </h2>
          <p className="center-description">
            SkillPulse streamlines traditional labor booking with fast, algorithmic matching.
          </p>
        </div>

        <div className="steps-grid">
          <div className="step-card">
            <span className="step-num">01</span>
            <div className="step-icon-bg">📝</div>
            <h3>Post a Requirement</h3>
            <p>Contractors specify skill type, location, wages, and working hours.</p>
          </div>

          <div className="step-card featured">
            <span className="step-num light">02</span>
            <div className="step-icon-bg light-icon">⚡</div>
            <h3>Instant Match</h3>
            <p>Algorithms verify and notify nearby workers based on skill and trust score.</p>
          </div>

          <div className="step-card">
            <span className="step-num">03</span>
            <div className="step-icon-bg">🤝</div>
            <h3>Get to Work</h3>
            <p>Worker accepts, arrives on site next morning, and gets paid securely.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function AiChatbotPage() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hello! I am your SkillPulse AI Assistant. Ask me about finding workers, daily wage estimates, or available shifts." }
  ]);
  const [inputVal, setInputVal] = useState("");

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    const userMsg = inputVal.trim();
    const newMessages = [...messages, { sender: "user", text: userMsg }];
    setMessages(newMessages);
    setInputVal("");

    // Enhanced smart response matching
    setTimeout(() => {
      let botReply = "I'm here to help you connect with reliable workers or find daily construction shifts. Could you clarify your request?";
      const lower = userMsg.toLowerCase();

      if (lower.includes("painter") || lower.includes("paint")) {
        botReply = "We have verified painters available in JP Nagar and Kumaraswamy Layout starting tomorrow morning. Standard wage is ₹800/day.";
      } else if (lower.includes("mason") || lower.includes("brick")) {
        botReply = "Mason profiles are active for tomorrow. Average rates are ₹950 per shift with verified reliability scores above 95%.";
      } else if (lower.includes("plumber") || lower.includes("pipe")) {
        botReply = "Plumbers are available in HSR Layout and surrounding areas. Shifts run from 9:00 AM to 4:30 PM at ₹900/day.";
      } else if (lower.includes("wage") || lower.includes("salary") || lower.includes("pay") || lower.includes("rate")) {
        botReply = "Daily wages on SkillPulse range from ₹800 to ₹1,000+ depending on the specific trade, skill verification level, and shift duration.";
      } else if (lower.includes("hello") || lower.includes("hi") || lower.includes("hey")) {
        botReply = "Hello! Are you looking to hire skilled labor for tomorrow, or are you searching for an active job listing?";
      } else if (lower.includes("bengaluru") || lower.includes("bangalore") || lower.includes("location")) {
        botReply = "We currently operate actively across multiple zones in Bengaluru including JP Nagar, HSR Layout, and Kumaraswamy Layout.";
      }

      setMessages((prev) => [...prev, { sender: "bot", text: botReply }]);
    }, 500);
  };

  return (
    <div className="section-container" style={{ padding: "60px 24px", minHeight: "70vh" }}>
      <span className="section-badge">AI ASSISTANT</span>
      <h2 className="section-title">
        AI <span>Chatbot</span>
      </h2>
      <p style={{ marginTop: "12px", color: "var(--text-muted)", fontSize: "16px" }}>
        Chat with our assistant to instantly check worker availability, estimates, or job specifications.
      </p>

      <div className="glass-morphism" style={{ marginTop: "32px", padding: "24px", borderRadius: "var(--radius-lg)", display: "flex", flexDirection: "column", height: "420px" }}>
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "14px", paddingRight: "8px" }}>
          {messages.map((m, index) => (
            <div 
              key={index} 
              style={{
                alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
                background: m.sender === "user" ? "var(--primary-orange)" : "var(--white)",
                color: m.sender === "user" ? "#fff" : "var(--text-primary)",
                padding: "12px 18px",
                borderRadius: "var(--radius-md)",
                maxWidth: "75%",
                fontSize: "14px",
                boxShadow: "var(--shadow-sm)",
                border: m.sender === "bot" ? "1px solid var(--border-color)" : "none"
              }}
            >
              {m.text}
            </div>
          ))}
        </div>

        <form onSubmit={handleSend} style={{ display: "flex", gap: "12px", marginTop: "16px", paddingTop: "16px", borderTop: "1px solid var(--border-subtle)" }}>
          <input 
            type="text" 
            placeholder="Ask about painters, masons, wages, or locations..."
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            style={{ flex: 1, padding: "12px 16px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-color)", outline: "none", fontSize: "14px", background: "var(--white)" }}
          />
          <button type="submit" className="btn-accent" style={{ padding: "12px 20px" }}>Send</button>
        </form>
      </div>
    </div>
  );
}

function AiVoicePage() {
  return (
    <div className="section-container" style={{ padding: "80px 24px", minHeight: "60vh" }}>
      <span className="section-badge">VOICE ASSISTANT</span>
      <h2 className="section-title">
        AI <span>Voice Assistant</span>
      </h2>
      <p style={{ marginTop: "16px", color: "var(--text-muted)", fontSize: "16px" }}>
        Use hands-free voice commands in your local language to quickly post jobs or find immediate worker availability.
      </p>

      <div className="glass-morphism" style={{ marginTop: "32px", padding: "40px", borderRadius: "var(--radius-lg)", textAlign: "center" }}>
        <div style={{ fontSize: "48px", marginBottom: "16px" }}>🎙️</div>
        <button className="btn-accent" style={{ margin: "0 auto" }}>
          Tap to Speak
        </button>
      </div>
    </div>
  );
}

// --- MAIN APP COMPONENT ---

function App() {
  const [currentPage, setCurrentPage] = useState("home");

  const navigateTo = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <HomePage navigateTo={navigateTo} />;
      case "find-jobs":
        return <FindJobsPage />;
      case "find-workers":
        return <FindWorkersPage />;
      case "how-it-works":
        return <HowItWorksPage />;
      case "ai-chatbot":
        return <AiChatbotPage />;
      case "ai-voice":
        return <AiVoicePage />;
      default:
        return <HomePage navigateTo={navigateTo} />;
    }
  };

  return (
    <div className="app">
      {/* NAVBAR */}
      <header className="navbar">
        <div className="nav-container">
          <div className="brand" onClick={() => navigateTo("home")}>
            <div className="brand-icon">
              <span>S</span>
            </div>
            <div className="brand-text">
              <span className="brand-name">SkillPulse</span>
              <span className="brand-tagline">WORK. MATCHED.</span>
            </div>
          </div>

          <nav className="nav-links">
            <button
              className={currentPage === "home" ? "active" : ""}
              onClick={() => navigateTo("home")}
            >
              Home
            </button>
            <button
              className={currentPage === "find-jobs" ? "active" : ""}
              onClick={() => navigateTo("find-jobs")}
            >
              Find Jobs
            </button>
            <button
              className={currentPage === "find-workers" ? "active" : ""}
              onClick={() => navigateTo("find-workers")}
            >
              Find Workers
            </button>
            <button
              className={currentPage === "how-it-works" ? "active" : ""}
              onClick={() => navigateTo("how-it-works")}
            >
              How It Works
            </button>
            <button
              className={currentPage === "ai-chatbot" ? "active" : ""}
              onClick={() => navigateTo("ai-chatbot")}
            >
              AI chatbot
            </button>
            <button
              className={currentPage === "ai-voice" ? "active" : ""}
              onClick={() => navigateTo("ai-voice")}
            >
              AI Voice
            </button>
          </nav>

          <div className="nav-actions">
            <button className="btn-ghost">Login</button>
            <button className="btn-primary-dark" onClick={() => navigateTo("find-workers")}>
              Get Started
            </button>
          </div>

          <button className="mobile-menu-btn" aria-label="Toggle Navigation">
            <span className="bar"></span>
            <span className="bar"></span>
          </button>
        </div>
      </header>

      {/* PAGE CONTAINER */}
      <main>{renderPage()}</main>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-brand">
            <div className="brand" onClick={() => navigateTo("home")}>
              <div className="brand-icon"><span>S</span></div>
              <span className="brand-name white">SkillPulse</span>
            </div>
            <p>Connecting verified daily workers and contractors through intelligent matching.</p>
          </div>

          <div className="footer-links">
            <div>
              <h4>Platform</h4>
              <a onClick={() => navigateTo("find-jobs")}>Find Jobs</a>
              <a onClick={() => navigateTo("find-workers")}>Find Workers</a>
              <a onClick={() => navigateTo("how-it-works")}>How It Works</a>
              <a onClick={() => navigateTo("ai-chatbot")}>AI Chatbot</a>
              <a onClick={() => navigateTo("ai-voice")}>AI Voice</a>
            </div>
            <div>
              <h4>Company</h4>
              <a href="#about">About Us</a>
              <a href="#contact">Contact</a>
              <a href="#careers">Careers</a>
            </div>
            <div>
              <h4>Legal</h4>
              <a href="#privacy">Privacy Policy</a>
              <a href="#terms">Terms of Service</a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p>© {new Date().getFullYear()} SkillPulse, Inc. All rights reserved.</p>
          <p>Made for real-world construction networks.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;