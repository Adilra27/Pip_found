import React, { useEffect, useState } from 'react';
import { ShieldCheck, Heart, Award, Users, CheckCircle, User } from 'lucide-react';
import { fetchTeam } from '../api';

export default function About({ onOpenDonate }) {
  const [team, setTeam] = useState([]);

  useEffect(() => {
    fetchTeam().then(setTeam).catch(console.error);
  }, []);

  return (
    <div>
      {/* Page Header Banner */}
      <section style={{ background: '#0f172a', color: '#ffffff', padding: '4rem 0 3rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>About Piplad Welfare Foundation</span>
          <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '0.75rem' }}>Our Story & Mission</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            Empowering underprivileged lives across India through sustainable welfare, education, healthcare, and equal opportunities.
          </p>
        </div>
      </section>

      {/* Main Content */}
      <section className="section-padding" style={{ background: '#ffffff' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '3.5rem', alignItems: 'center' }}>
          <div>
            <span className="badge badge-amber" style={{ marginBottom: '0.75rem' }}>Who We Are</span>
            <h2 className="heading-lg" style={{ marginBottom: '1.25rem' }}>
              Transforming Compassion Into Direct Action
            </h2>
            <p style={{ fontSize: '1rem', color: '#475569', lineHeight: 1.7, marginBottom: '1.25rem' }}>
              <strong>Piplad Welfare Foundation (PWF)</strong> is a non-profit non-governmental organization registered in India. Founded with the vision of <em>"Creating Opportunities, Creating Lives"</em>, our team works relentlessly at ground level to bring dignity, health, and education to marginalized communities.
            </p>
            <p style={{ fontSize: '1rem', color: '#475569', lineHeight: 1.7, marginBottom: '1.5rem' }}>
              From supporting children fighting critical life-threatening conditions like pediatric cancer to setting up free study circles in rural villages, our transparent model ensures that maximum resources directly benefit the needy.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontWeight: 600, color: '#0f172a' }}>
                <CheckCircle size={20} color="#059669" /> 100% Transparent Financial Reporting & Audits
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontWeight: 600, color: '#0f172a' }}>
                <CheckCircle size={20} color="#059669" /> Registered under 80G for Tax Deductions
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontWeight: 600, color: '#0f172a' }}>
                <CheckCircle size={20} color="#059669" /> Grassroots Volunteers & Field Operators Across India
              </div>
            </div>

            <button className="btn btn-primary" onClick={onOpenDonate} style={{ padding: '0.85rem 1.8rem' }}>
              <Heart size={18} fill="#ffffff" /> Join Our Mission
            </button>
          </div>

          <div>
            <div style={{ borderRadius: '16px', overflow: 'hidden', boxShadow: '0 15px 30px rgba(0,0,0,0.1)' }}>
              <img
                src="https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?auto=format&fit=crop&q=80&w=800"
                alt="Child Healthcare Support"
                style={{ width: '100%', height: '400px', objectFit: 'cover' }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Vision & Mission Cards */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
            <div className="card" style={{ padding: '2.5rem', borderTop: '4px solid #059669' }}>
              <h3 className="heading-md" style={{ marginBottom: '1rem', color: '#059669' }}>Our Mission</h3>
              <p style={{ color: '#475569', lineHeight: 1.6 }}>
                To eradicate poverty-driven barriers in education, healthcare, and nutrition by deploying direct financial aid, community drives, and sustainable skill development for vulnerable children and families.
              </p>
            </div>

            <div className="card" style={{ padding: '2.5rem', borderTop: '4px solid #d97706' }}>
              <h3 className="heading-md" style={{ marginBottom: '1rem', color: '#d97706' }}>Our Vision</h3>
              <p style={{ color: '#475569', lineHeight: 1.6 }}>
                An inclusive India where every child gets access to quality healthcare and education regardless of socio-economic background, and every family has the tools to achieve self-reliance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="section-padding" style={{ background: '#ffffff' }}>
        <div className="container">
          <h2 className="heading-lg" style={{ marginBottom: '1.5rem', textAlign: 'center', color: '#0f172a' }}>Our Team</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem' }}>
            {team.map((member) => (
              <div key={member.id} style={{ textAlign: 'center', padding: '1rem', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                {member.photo_url ? (
                  <img src={member.photo_url} alt={member.name} style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '8px', marginBottom: '0.75rem' }} />
                ) : (
                  <User size={48} color="#059669" style={{ marginBottom: '0.75rem' }} />
                )}
                <h4 style={{ margin: '0.5rem 0', color: '#0f172a' }}>{member.name}</h4>
                {member.role && <p style={{ margin: 0, color: '#475569', fontSize: '0.9rem' }}>{member.role}</p>}
                {member.bio && <p style={{ marginTop: '0.5rem', color: '#64748b', fontSize: '0.85rem' }}>{member.bio}</p>}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
