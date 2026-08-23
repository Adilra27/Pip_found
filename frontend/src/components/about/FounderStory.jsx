// src/components/about/FounderStory.jsx

import React from "react";
import { founderStoryData } from "../../data/aboutdata";

const FounderStory = () => {
  const data = founderStoryData;

  return (
    <section
      id="founders"
      className="about-founder"
      style={{ scrollMarginTop: "100px" }}
    >

      <div className="about-container">

        <div className="about-founder-grid">

          <div className="about-founder-image">

            <div className="about-founder-image-frame">

              <img
                src={data.image}
                alt={data.imageAlt}
              />

            </div>

            <div className="about-founder-badge">

              <strong>{data.name}</strong>

              <span>{data.role}</span>

            </div>

          </div>


          <div className="about-founder-content">

            <span className="about-eyebrow">
              {data.eyebrow}
            </span>

            <h2>{data.title}</h2>

            <p className="about-lead">
              {data.introduction}
            </p>

            <p>{data.story}</p>

            <div className="about-founder-vision">

              <span>Our Vision</span>

              <p>{data.vision}</p>

            </div>

            <blockquote>
              "{data.quote}"
            </blockquote>

          </div>

        </div>


        <div className="about-founder-milestones">

          {data.milestones.map((item, index) => (
            <article
              className="about-founder-milestone"
              key={index}
            >

              <span>{item.year}</span>

              <h3>{item.title}</h3>

              <p>{item.description}</p>

            </article>
          ))}

        </div>

      </div>

    </section>
  );
};

export default FounderStory;