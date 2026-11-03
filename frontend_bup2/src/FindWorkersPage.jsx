import React from "react";
import "./FindWorkersPage.css";

const steps = [
  {
    number: "01",
    icon: "📋",
    title: "Post your requirement",
    description:
      "Choose the skill, work date, location, daily wage and number of workers you need.",
    tag: "Easy job creation",
  },
  {
    number: "02",
    icon: "🎯",
    title: "Discover smart matches",
    description:
      "SkillPulse filters eligible workers and ranks recommendations using your matching engine.",
    tag: "Intelligent matching",
  },
  {
    number: "03",
    icon: "🤝",
    title: "Build your workforce",
    description:
      "Review recommendations, select suitable workers and manage applications from your dashboard.",
    tag: "Complete control",
  },
];

const advantages = [
  {
    icon: "📍",
    title: "Location-aware matching",
    description:
      "Find eligible workers within your configured location radius.",
  },
  {
    icon: "🛠️",
    title: "Skill-based filtering",
    description:
      "Match workers according to the skills required for your job.",
  },
  {
    icon: "⭐",
    title: "Reliability ranking",
    description:
      "Use available worker reliability information as part of your matching process.",
  },
  {
    icon: "📅",
    title: "Availability checks",
    description:
      "Prioritise workers who are available for your required work date.",
  },
];

function FindWorkersPage({ onAuth }) {
  const openContractorLogin = () => {
    if (onAuth) {
      onAuth("login");
    }
  };

  return (
    <main className="fw-page">

      {/* HERO SECTION */}
      <section className="fw-hero">

        <div className="fw-hero-content">
          <div className="fw-eyebrow">
            <span className="fw-eyebrow-dot"></span>
            BUILT FOR CONTRACTORS
          </div>

          <h1>
            Find skilled workers.
            <br />
            <span>Build better teams.</span>
          </h1>

          <p className="fw-hero-description">
            Finding the right workforce shouldn't slow down your project.
            Let SkillPulse help you discover eligible workers through
            intelligent, location-aware matching.
          </p>

          <div className="fw-hero-actions">
            <button
              className="fw-primary-button"
              onClick={openContractorLogin}
            >
              Find Workers
              <span>→</span>
            </button>

            <a href="#fw-how-it-works" className="fw-secondary-button">
              Explore how it works
              <span>↓</span>
            </a>
          </div>

          <div className="fw-trust-line">
            <span>✓</span>
            Skill-based matching
            <span className="fw-trust-divider">•</span>
            <span>✓</span>
            Location-aware recommendations
          </div>
        </div>

        {/* MATCHING VISUAL */}
        <div className="fw-visual">

          <div className="fw-visual-orbit fw-orbit-one"></div>
          <div className="fw-visual-orbit fw-orbit-two"></div>

          <div className="fw-visual-label">
            <span className="fw-live-dot"></span>
            HOW SKILLPULSE MATCHES
          </div>

          <div className="fw-match-card">

            <div className="fw-match-header">
              <div>
                <span className="fw-card-caption">YOUR REQUIREMENT</span>
                <h3>Mason Workers</h3>
                <p>Bengaluru, Karnataka</p>
              </div>

              <div className="fw-match-icon">⌕</div>
            </div>

            <div className="fw-requirement-details">
              <div>
                <span>WORK DATE</span>
                <strong>Selected date</strong>
              </div>

              <div>
                <span>WORKERS NEEDED</span>
                <strong>As required</strong>
              </div>

              <div>
                <span>DAILY WAGE</span>
                <strong>Your budget</strong>
              </div>
            </div>

            <div className="fw-matching-line">
              <div className="fw-matching-icon">✦</div>

              <div>
                <strong>Smart matching process</strong>
                <span>Filtering and ranking eligible workers</span>
              </div>

              <div className="fw-matching-arrow">→</div>
            </div>

            <div className="fw-match-flow">
              <div className="fw-flow-item">
                <span className="fw-flow-number">01</span>
                <span>Skills</span>
              </div>

              <div className="fw-flow-connector"></div>

              <div className="fw-flow-item">
                <span className="fw-flow-number">02</span>
                <span>Location</span>
              </div>

              <div className="fw-flow-connector"></div>

              <div className="fw-flow-item">
                <span className="fw-flow-number">03</span>
                <span>Ranking</span>
              </div>
            </div>

            <div className="fw-demo-note">
              Illustrative matching preview — actual recommendations
              are generated through your authenticated contractor workflow.
            </div>

          </div>

          <div className="fw-floating-card fw-floating-top">
            <span>✦</span>
            Intelligent matching
          </div>

          <div className="fw-floating-card fw-floating-bottom">
            <span>✓</span>
            Eligibility checks
          </div>

        </div>
      </section>


      {/* HIGHLIGHT STRIP */}
      <section className="fw-highlight-strip">

        <div className="fw-highlight-item">
          <span className="fw-highlight-icon">🎯</span>
          <div>
            <strong>Skill-first</strong>
            <span>Relevant workers</span>
          </div>
        </div>

        <div className="fw-highlight-separator"></div>

        <div className="fw-highlight-item">
          <span className="fw-highlight-icon">📍</span>
          <div>
            <strong>Location-aware</strong>
            <span>Nearby eligibility</span>
          </div>
        </div>

        <div className="fw-highlight-separator"></div>

        <div className="fw-highlight-item">
          <span className="fw-highlight-icon">⚡</span>
          <div>
            <strong>Smart ranking</strong>
            <span>Weighted recommendations</span>
          </div>
        </div>

        <div className="fw-highlight-separator"></div>

        <div className="fw-highlight-item">
          <span className="fw-highlight-icon">🤝</span>
          <div>
            <strong>Easy management</strong>
            <span>Contractor dashboard</span>
          </div>
        </div>

      </section>


      {/* HOW IT WORKS */}
      <section className="fw-process-section" id="fw-how-it-works">

        <div className="fw-section-heading">
          <div className="fw-eyebrow">SIMPLE. SMART. EFFECTIVE.</div>

          <h2>
            Your workforce,
            <span> in three steps.</span>
          </h2>

          <p>
            From posting a requirement to managing applications,
            SkillPulse keeps the process organised.
          </p>
        </div>

        <div className="fw-process-grid">

          {steps.map((step, index) => (
            <article className="fw-process-card" key={step.number}>

              <div className="fw-process-top">
                <span className="fw-step-number">{step.number}</span>
                <span className="fw-process-icon">{step.icon}</span>
              </div>

              <span className="fw-process-tag">{step.tag}</span>

              <h3>{step.title}</h3>

              <p>{step.description}</p>

              {index !== steps.length - 1 && (
                <div className="fw-process-arrow">↗</div>
              )}

            </article>
          ))}

        </div>
      </section>


      {/* FEATURES */}
      <section className="fw-benefits-section">

        <div className="fw-benefits-intro">
          <div className="fw-eyebrow">WHY SKILLPULSE?</div>

          <h2>
            More than finding workers.
            <span> Finding the right fit.</span>
          </h2>

          <p>
            SkillPulse uses your existing matching engine to evaluate
            eligible candidates against job requirements.
          </p>

          <button
            className="fw-primary-button"
            onClick={openContractorLogin}
          >
            Get Started
            <span>→</span>
          </button>
        </div>

        <div className="fw-benefits-grid">

          {advantages.map((item, index) => (
            <article className="fw-benefit-card" key={item.title}>

              <div className="fw-benefit-icon">
                {item.icon}
              </div>

              <span className="fw-benefit-index">
                0{index + 1}
              </span>

              <h3>{item.title}</h3>

              <p>{item.description}</p>

            </article>
          ))}

        </div>

      </section>


      {/* CTA */}
      <section className="fw-cta-section">

        <div className="fw-cta-decoration fw-cta-decoration-one"></div>
        <div className="fw-cta-decoration fw-cta-decoration-two"></div>

        <div className="fw-cta-content">
          <div className="fw-cta-eyebrow">
            YOUR NEXT PROJECT STARTS HERE
          </div>

          <h2>
            The right team makes
            <br />
            <span>all the difference.</span>
          </h2>

          <p>
            Sign in to SkillPulse, post your requirement and
            discover suitable worker recommendations.
          </p>

          <button
            className="fw-cta-button"
            onClick={openContractorLogin}
          >
            Continue as Contractor
            <span>→</span>
          </button>
        </div>

        <div className="fw-cta-symbol">S</div>

      </section>

    </main>
  );
}

export default FindWorkersPage;