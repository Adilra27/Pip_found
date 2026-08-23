import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, MapPin, Phone, Mail, ShieldCheck, ArrowRight } from 'lucide-react';

export default function Footer({ onOpenDonate }) {
  return (
    <footer style={{ background: '#0f172a', color: '#cbd5e1', paddingTop: '4rem', paddingBottom: '2rem' }}>
      <div className="container">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '3rem', marginBottom: '3rem' }}>
          
          {/* Col 1: Brand & Mission */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem' }}>
              <div style={{ background: '#059669', color: '#fff', width: '42px', height: '42px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.2rem' }}>
                PWF
              </div>
              <div>
                <div style={{ fontWeight: 800, fontSize: '1.1rem', color: '#ffffff' }}>PIPLAD WELFARE</div>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#34d399', letterSpacing: '0.08em' }}>FOUNDATION</div>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              Creating Opportunities, Creating Lives. Dedicated to child healthcare, quality education, zero hunger, and rural empowerment across India.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(16,185,129,0.1)', color: '#34d399', padding: '0.5rem 0.8rem', borderRadius: '6px', fontSize: '0.85rem', width: 'fit-content' }}>
              <ShieldCheck size={16} /> 80G Tax Deductible (Reg. NGO)
            </div>
          </div>

          {/* Col 2: Quick Links */}
          <div>
            <h4 style={{ color: '#ffffff', fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>Quick Links</h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem' }}>
              <li><Link to="/about" style={{ color: '#cbd5e1', hover: { color: '#34d399' } }}>About Our Foundation</Link></li>
              <li><Link to="/causes" style={{ color: '#cbd5e1' }}>Current Welfare Causes</Link></li>
              <li><Link to="/donate" style={{ color: '#cbd5e1' }}>Donate & 80G Benefits</Link></li>
              <li><Link to="/gallery" style={{ color: '#cbd5e1' }}>Media & Awards Gallery</Link></li>
              <li><Link to="/contact" style={{ color: '#cbd5e1' }}>Contact & Reach Us</Link></li>
              <li><Link to="/terms" style={{ color: '#cbd5e1' }}>Refund & Cancellation Policy</Link></li>
            </ul>
          </div>

          {/* Col 3: Causes */}
          <div>
            <h4 style={{ color: '#ffffff', fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>Our Core Focus</h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem', color: '#94a3b8' }}>
              <li>• Childhood Cancer Healthcare</li>
              <li>• Free Education & School Supplies</li>
              <li>• Daily Ration & Warm Meals</li>
              <li>• Women Skill Empowerment</li>
              <li>• Emergency Medical Financial Aid</li>
            </ul>
          </div>

          {/* Col 4: Contact Info */}
          <div>
            <h4 style={{ color: '#ffffff', fontSize: '1.1rem', fontWeight: 700, marginBottom: '1.25rem' }}>Contact Info</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.9rem', color: '#94a3b8' }}>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <MapPin size={18} color="#10b981" style={{ flexShrink: 0, marginTop: '3px' }} />
                <span>Piplad Welfare Foundation, Main Road, India</span>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <Phone size={18} color="#10b981" style={{ flexShrink: 0 }} />
                <span>+91-9876543210</span>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <Mail size={18} color="#10b981" style={{ flexShrink: 0 }} />
                <span>contact@pipladfoundation.in</span>
              </div>
              <button className="btn btn-primary" onClick={onOpenDonate} style={{ marginTop: '0.5rem', width: 'fit-content' }}>
                <Heart size={16} fill="#ffffff" /> Make a Donation
              </button>
            </div>
          </div>

        </div>

        <div style={{ borderTop: '1px solid #1e293b', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', fontSize: '0.85rem', color: '#64748b' }}>
          <div>
            © {new Date().getFullYear()} Piplad Welfare Foundation (PWF). All Rights Reserved.
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <Link to="/terms" style={{ color: '#64748b' }}>Terms & Conditions</Link>
            <Link to="/terms" style={{ color: '#64748b' }}>Refund Policy</Link>
            <Link to="/contact" style={{ color: '#64748b' }}>Support</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
