import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { fetchTeam } from '../api';

import AboutHero from '../components/about/AboutHero';
import WhoWeAre from '../components/about/WhoWeAre';
import MissionVision from '../components/about/MissionVision';
import OurApproach from '../components/about/OurApproach';
import ImpactAreas from '../components/about/ImpactAreas';
import StrategicPriorities from '../components/about/StrategicPriorities';
import ValuesSection from '../components/about/ValuesSection';
import FounderStory from '../components/about/FounderStory';
import MentorsSection from '../components/about/MentorsSection';
import AboutCTA from '../components/about/AboutCTA';

import '../styles/about.css';

export default function About({ onOpenDonate }) {
  const location = useLocation();

  const [team, setTeam] = useState([]);
  const [teamLoading, setTeamLoading] = useState(true);
  const [teamError, setTeamError] = useState(null);

  /*
   * Load team information
   */
  useEffect(() => {
    let isMounted = true;

    const loadTeam = async () => {
      try {
        setTeamLoading(true);
        setTeamError(null);

        const data = await fetchTeam();

        if (isMounted) {
          setTeam(Array.isArray(data) ? data : []);
        }
      } catch (error) {
        console.error('Failed to fetch team:', error);

        if (isMounted) {
          setTeamError('Unable to load team information.');
          setTeam([]);
        }
      } finally {
        if (isMounted) {
          setTeamLoading(false);
        }
      }
    };

    loadTeam();

    return () => {
      isMounted = false;
    };
  }, []);

  /*
   * Handle hash navigation
   *
   * Examples:
   *
   * /about#founders
   * /about#mentors
   *
   * React Router changes the URL, but it does not
   * always automatically scroll to the hash target.
   */
  useEffect(() => {
    if (!location.hash) {
      return;
    }

    const hash = location.hash.replace('#', '');

    const scrollToSection = () => {
      const element = document.getElementById(hash);

      if (element) {
        element.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    };

    /*
     * Wait until the About page sections have rendered
     * before trying to find the target element.
     */
    const timeoutId = setTimeout(scrollToSection, 100);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [location.hash]);

  return (
    <main className="about-page">

      {/* =========================================
          1. ABOUT HERO
      ========================================== */}
      <AboutHero />

      {/* =========================================
          2. WHO WE ARE
      ========================================== */}
      <WhoWeAre />

      {/* =========================================
          3. MISSION & VISION
      ========================================== */}
      <MissionVision />

      {/* =========================================
          4. OUR APPROACH
      ========================================== */}
      <OurApproach />

      {/* =========================================
          5. IMPACT AREAS
      ========================================== */}
      <ImpactAreas />

      {/* =========================================
          6. STRATEGIC PRIORITIES
      ========================================== */}
      <StrategicPriorities />

      {/* =========================================
          7. OUR VALUES
      ========================================== */}
      <ValuesSection />

      {/* =========================================
          8. FOUNDER'S STORY
      ========================================== */}
      <FounderStory />

      {/* =========================================
          9. MENTORS / TEAM
      ========================================== */}
      <MentorsSection
        team={team}
        loading={teamLoading}
        error={teamError}
      />

      {/* =========================================
          10. FINAL CTA
      ========================================== */}
      <AboutCTA onOpenDonate={onOpenDonate} />

    </main>
  );
}