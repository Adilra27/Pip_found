// src/components/about/MentorsSection.jsx

import React, { useState } from "react";
import { mentorsData } from "../../data/aboutdata";

const MentorsSection = () => {
  const data = mentorsData;

  const [activeMentor, setActiveMentor] = useState(0);

  const mentor = data.mentors[activeMentor];

  return (
    <section className="about-mentors">

      <div className="about-container">

        <div className="about-section-heading about-centered">

          <span className="about-eyebrow">
            {data.eyebrow}
          </span>

          <h2>{data.title}</h2>

          <p>{data.description}</p>

        </div>


        <div className="about-mentor-selector">

          {data.mentors.map((item, index) => (
            <button
              type="button"
              className={`about-mentor-tab ${
                activeMentor === index
                  ? "active"
                  : ""
              }`}
              onClick={() => setActiveMentor(index)}
              key={index}
            >
              {item.name}
            </button>
          ))}

        </div>


        <div className="about-mentor-card">

          <div className="about-mentor-image">

            <img
              src={mentor.image}
              alt={mentor.name}
            />

          </div>


          <div className="about-mentor-content">

            <span className="about-card-label">
              Mentor
            </span>

            <h3>{mentor.name}</h3>

            <h4>{mentor.role}</h4>

            <p>{mentor.description}</p>

            <blockquote>
              "{mentor.quote}"
            </blockquote>

          </div>

        </div>

      </div>

    </section>
  );
};

export default MentorsSection;