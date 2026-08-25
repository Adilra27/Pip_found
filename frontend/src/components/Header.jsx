import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Heart, Phone, Mail, Menu, X, ShieldCheck, ChevronDown } from 'lucide-react';

export default function Header({ onOpenDonate }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { label: 'Home', path: '/' },
    { 
      label: 'About Us', 
      path: '/about', 
      subItems: [
        { label: 'Introduction', path: '/about' },
        { label: 'Founders', path: '/about#founders' },
        { label: 'Mentors', path: '/about#mentors' }
      ]
    },
    {
      label: 'Our Team',
      path: '/team',
      subItems: [
        { label: 'Education & Skill development', path: '/team/education' },
        { label: 'Healthcare', path: '/team/healthcare' },
        { label: 'Finance & Legal', path: '/team/finance' },
        { label: 'Environment & Modern Agriculture', path: '/team/environment' },
        { label: 'Social Welfare', path: '/team/social' },
        { label: 'Culture & Tourism', path: '/team/culture' },
        { label: 'Sports & Yoga', path: '/team/sports' },
        { label: 'IT & Social Media', path: '/team/it' }
      ]
    },
    {
      label: 'Media & Awards',
      path: '/gallery',
      subItems: [
        { label: 'Photo Gallery', path: '/gallery' },
        { label: 'Video Gallery', path: '/gallery/videos' },
        { label: 'Upcoming Projects', path: '/projects' }
      ]
    },
    {
      label: 'Join Us',
      path: '/join',
      subItems: [
        { label: 'Join Us', path: '/join' },
        { label: 'Contact Us', path: '/contact' }
      ]
    },
    { label: 'Blog', path: '/blog' }
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <header className="header-wrapper" style={{ position: 'sticky', top: 0, zIndex: 900, background: '#ffffff', boxShadow: '0 2px 10px rgba(0,0,0,0.06)' }}>
      {/* Top bar info */}
      <div style={{ background: '#84cc16', color: '#ffffff', fontSize: '0.85rem', padding: '0.5rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center', fontWeight: 600 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Phone size={14} /> +91-8981266033
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Mail size={14} /> info@pipladfoundation.in
            </span>
          </div>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '80px' }}>
        {/* Brand Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'linear-gradient(135deg, #059669, #047857)', color: '#fff', width: '46px', height: '46px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '1.1rem', boxShadow: '0 4px 10px rgba(5,150,105,0.3)' }}>
            Tree
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '1.25rem', color: '#059669', lineHeight: 1.1 }}>
              PIPLAD
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#059669' }}>
              Welfare Foundation
            </div>
            <div style={{ fontSize: '0.6rem', color: '#64748b' }}>
              Creating Opportunities, Creating Lives
            </div>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }} className="desktop-nav">
          {navItems.map((item) => (
            <div key={item.path} className="nav-item-group" style={{ position: 'relative' }}>
              {item.subItems ? (
                <div 
                  className="nav-link"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.2rem',
                    fontWeight: 600,
                    color: '#334155',
                    fontSize: '0.95rem',
                    padding: '0.5rem 1rem',
                    cursor: 'pointer',
                    borderRadius: '4px'
                  }}
                >
                  {item.label}
                  <ChevronDown size={14} />
                </div>
              ) : (
                <Link
                  to={item.path}
                  className={`nav-link ${isActive(item.path) ? 'active-nav-link' : ''}`}
                  style={{
                    fontWeight: 600,
                    color: '#334155',
                    fontSize: '0.95rem',
                    padding: '0.5rem 1rem',
                    borderRadius: '4px',
                    display: 'block'
                  }}
                >
                  {item.label}
                </Link>
              )}

              {/* Dropdown Menu */}
              {item.subItems && (
                <div className="dropdown-menu" style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  background: '#ffffff',
                  boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                  borderRadius: '4px',
                  minWidth: '220px',
                  padding: '0.5rem 0',
                  zIndex: 50,
                  display: 'none',
                  flexDirection: 'column'
                }}>
                  {item.subItems.map(sub => (
                    <Link
                      key={sub.label}
                      to={sub.path}
                      style={{
                        padding: '0.75rem 1.5rem',
                        color: '#334155',
                        fontSize: '0.9rem',
                        fontWeight: 500,
                        textDecoration: 'none',
                        display: 'block',
                        transition: 'background 0.2s'
                      }}
                      className="dropdown-item"
                    >
                      {sub.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}

          <button className="btn btn-primary" onClick={onOpenDonate} style={{ borderRadius: '4px', padding: '0.65rem 1.5rem', background: '#65a30d', border: 'none' }}>
            Donate
          </button>
        </nav>

        {/* Mobile Hamburger Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          style={{ display: 'none', background: 'none', border: 'none', cursor: 'pointer', color: '#0f172a' }}
          className="mobile-menu-btn"
        >
          {mobileMenuOpen ? <X size={28} /> : <Menu size={28} />}
        </button>
      </div>

      {/* Mobile Menu Overlay (simplified for mobile) */}
      {mobileMenuOpen && (
        <div style={{ background: '#ffffff', borderTop: '1px solid #e2e8f0', padding: '1rem 1.5rem 1.5rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {navItems.map((item) => (
            <div key={item.label}>
              <div style={{ fontWeight: 700, color: '#059669', marginBottom: '0.5rem' }}>{item.label}</div>
              {item.subItems ? (
                <div style={{ paddingLeft: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {item.subItems.map(sub => (
                     <Link key={sub.label} to={sub.path} onClick={() => setMobileMenuOpen(false)} style={{ color: '#334155' }}>
                       {sub.label}
                     </Link>
                  ))}
                </div>
              ) : (
                <Link to={item.path} onClick={() => setMobileMenuOpen(false)} style={{ color: '#334155', paddingLeft: '1rem' }}>
                  Go to {item.label}
                </Link>
              )}
            </div>
          ))}
          <button className="btn btn-primary" onClick={() => { setMobileMenuOpen(false); onOpenDonate(); }} style={{ width: '100%', marginTop: '0.5rem', background: '#65a30d' }}>
            Donate Now
          </button>
        </div>
      )}

      <style>{`
        .nav-item-group:hover .dropdown-menu {
          display: flex !important;
        }
        .nav-link:hover {
          color: #65a30d !important;
        }
        .active-nav-link {
          background: #84cc16 !important;
          color: #ffffff !important;
        }
        .dropdown-item:hover {
          background: #f8fafc;
          color: #65a30d !important;
        }
        @media (max-width: 1024px) {
          .desktop-nav { display: none !important; }
          .mobile-menu-btn { display: block !important; }
        }
      `}</style>
    </header>
  );
}
