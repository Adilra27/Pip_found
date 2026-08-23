import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, ShieldCheck, Users, Award, BookOpen, UtensilsCrossed, ArrowRight, CheckCircle } from 'lucide-react';
import { fetchCauses } from '../api';
import CauseCard from '../components/CauseCard';

export default function Home({ onOpenDonate, onSelectCauseToDonate }) {
  const [causes, setCauses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCauses()
      .then((data) => {
        setCauses(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching causes:', err);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      {/* Hero Section */}
      <section style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', color: '#ffffff', padding: '5rem 0 6rem 0', position: 'relative', overflow: 'hidden' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '3rem', alignItems: 'center' }}>
          <div>
            <div className="badge badge-green" style={{ marginBottom: '1.25rem' }}>
              <ShieldCheck size={16} /> Empowering Communities Since Inception
            </div>
            <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '1.25rem' }}>
              Creating Opportunities, <span style={{ color: '#34d399' }}>Creating Lives</span>
            </h1>
            <p style={{ fontSize: '1.1rem', color: '#94a3b8', lineHeight: 1.6, marginBottom: '2rem', maxWidth: '580px' }}>
              Piplad Welfare Foundation is committed to transforming lives through childhood healthcare, quality education for all, zero hunger food drives, and women empowerment.
            </p>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={() => onOpenDonate()} style={{ padding: '0.9rem 1.8rem', fontSize: '1.05rem', borderRadius: '999px' }}>
                <Heart size={20} fill="#ffffff" /> Donate Now
              </button>
              <Link to="/causes" className="btn btn-outline" style={{ color: '#ffffff', borderColor: '#475569', borderRadius: '999px' }}>
                Explore Causes <ArrowRight size={18} />
              </Link>
            </div>
          </div>

          <div style={{ position: 'relative' }}>
            <div style={{ borderRadius: '20px', overflow: 'hidden', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)', border: '4px solid rgba(255,255,255,0.1)' }}>
              <img
                src="https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&q=80&w=800"
                alt="Piplad Welfare Foundation Drive"
                style={{ width: '100%', height: '420px', objectFit: 'cover', display: 'block' }}
              />
            </div>
            <div style={{ position: 'absolute', bottom: '-20px', left: '-20px', background: '#059669', color: '#fff', padding: '1.2rem 1.5rem', borderRadius: '14px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <Users size={36} />
              <div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>5,000+</div>
                <div style={{ fontSize: '0.85rem', color: '#a7f3d0' }}>Lives Impacted</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Stats Banner */}
      <section style={{ background: '#ffffff', borderBottom: '1px solid #e2e8f0', padding: '2.5rem 0' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem', textAlign: 'center' }}>
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#059669' }}>₹15L+</div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#64748b' }}>Welfare Funds Raised</div>
          </div>
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#059669' }}>1,200+</div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#64748b' }}>Children Educated</div>
          </div>
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#059669' }}>25,000+</div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#64748b' }}>Warm Meals Served</div>
          </div>
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#059669' }}>100%</div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#64748b' }}>Tax Benefit (80G)</div>
          </div>
        </div>
      </section>

      {/* Featured Causes */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span className="badge badge-green" style={{ marginBottom: '0.5rem' }}>Active Campaigns</span>
              <h2 className="heading-lg">Urgent Causes Needing Support</h2>
            </div>
            <Link to="/causes" className="btn btn-outline" style={{ borderRadius: '8px' }}>
              View All Causes <ArrowRight size={18} />
            </Link>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: '#64748b' }}>Loading active causes...</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
              {causes.slice(0, 3).map((cause) => (
                <CauseCard key={cause.id} cause={cause} onDonate={(c) => onSelectCauseToDonate(c)} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Mission & Core Pillars */}
      <section className="section-padding" style={{ background: '#ffffff' }}>
        <div className="container">
          <div style={{ textAlign: 'center', maxWidth: '700px', margin: '0 auto 3.5rem auto' }}>
            <span className="badge badge-amber" style={{ marginBottom: '0.5rem' }}>Why Choose PWF</span>
            <h2 className="heading-lg" style={{ marginBottom: '1rem' }}>Our Core Pillars of Transformation</h2>
            <p className="subheading" style={{ margin: '0 auto' }}>
              We focus our efforts where help is needed most, ensuring every rupee donated creates a direct, measurable impact.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
            <div className="card" style={{ padding: '2rem' }}>
              <div style={{ background: '#d1fae5', color: '#059669', width: '56px', height: '56px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <Heart size={28} />
              </div>
              <h3 className="heading-md" style={{ marginBottom: '0.75rem' }}>Child Healthcare</h3>
              <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.6 }}>
                Financial medical assistance for children suffering from cancer, heart diseases, and critical surgical needs.
              </p>
            </div>

            <div className="card" style={{ padding: '2rem' }}>
              <div style={{ background: '#fef3c7', color: '#d97706', width: '56px', height: '56px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <BookOpen size={28} />
              </div>
              <h3 className="heading-md" style={{ marginBottom: '0.75rem' }}>Quality Education</h3>
              <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.6 }}>
                Distributing school kits, books, digital tools, and funding school fees for bright underprivileged students.
              </p>
            </div>

            <div className="card" style={{ padding: '2rem' }}>
              <div style={{ background: '#e0f2fe', color: '#0284c7', width: '56px', height: '56px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <UtensilsCrossed size={28} />
              </div>
              <h3 className="heading-md" style={{ marginBottom: '0.75rem' }}>Zero Hunger Drives</h3>
              <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.6 }}>
                Providing nutritious cooked meals and monthly grocery ration kits to impoverished families and homeless children.
              </p>
            </div>

            <div className="card" style={{ padding: '2rem' }}>
              <div style={{ background: '#fce7f3', color: '#db2777', width: '56px', height: '56px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                <Users size={28} />
              </div>
              <h3 className="heading-md" style={{ marginBottom: '0.75rem' }}>Women Skill Training</h3>
              <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.6 }}>
                Vocational workshops in tailoring, digital literacy, and self-reliance skills to foster financial independence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action Banner */}
      <section style={{ background: '#059669', color: '#ffffff', padding: '4rem 0', textAlign: 'center' }}>
        <div className="container" style={{ maxWidth: '800px' }}>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '1rem' }}>
            Be the Light in Someone's Darkest Hour
          </h2>
          <p style={{ fontSize: '1.1rem', opacity: 0.9, marginBottom: '2rem', lineHeight: 1.6 }}>
            Your small donation today can fund life-saving cancer treatment or educate a child for an entire academic year. Every contribution receives 80G tax benefits.
          </p>
          <button className="btn" onClick={() => onOpenDonate()} style={{ background: '#ffffff', color: '#059669', padding: '0.9rem 2.2rem', fontSize: '1.1rem', fontWeight: 800, borderRadius: '999px', boxShadow: '0 10px 20px rgba(0,0,0,0.15)' }}>
            <Heart size={20} fill="#059669" /> Donate Now
          </button>
        </div>
      </section>
    </div>
  );
}
