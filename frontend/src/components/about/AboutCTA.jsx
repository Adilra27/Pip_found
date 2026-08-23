// src/components/about/AboutCTA.jsx

import React from "react";
import { aboutCTAData } from "../../data/aboutdata";

const AboutCTA = () => {
  const data = aboutCTAData;

  return (
    <section
      className="about-cta"
      id="about-cta"
    >

      <div className="about-container">

        <div className="about-cta-inner">

          <div className="about-cta-decoration">
            🌱
          </div>

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p>{data.description}</p>

          <div className="about-cta-actions">

            <a
              href="/join-us"
              className="about-btn about-btn-primary"
            >
              {data.primaryButton}
            </a>

            <a
              href="/donate-now"
              className="about-btn about-btn-light"
            >
              {data.secondaryButton}
            </a>

          </div>

          <span className="about-cta-closing">
            {data.closingText}
          </span>

        </div>

      </div>

    </section>
  );
};

export default AboutCTA;