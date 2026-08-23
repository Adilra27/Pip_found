import React from 'react';

export default function Team() {
  return (
    <div>
      <section style={{ background: '#0f172a', color: '#fff', padding: '4rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>Our Team</span>
          <h1 className="heading-xl" style={{ marginBottom: '0.75rem' }}>Meet the People Behind PWF</h1>
        </div>
      </section>
      <section className="section-padding">
        <div className="container">
          <p>Team members will be displayed here.</p>
        </div>
      </section>
    </div>
  );
}
