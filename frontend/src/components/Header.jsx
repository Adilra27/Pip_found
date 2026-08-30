import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Phone,
  Mail,
  Menu,
  X,
  ChevronDown,
} from 'lucide-react';

export default function Header({ onOpenDonate }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    {
      label: 'Home',
      path: '/',
    },
    {
      label: 'About Us',
      path: '/about',
      subItems: [
        { label: 'Introduction', path: '/about' },
        { label: 'Founders', path: '/about#founders' },
        { label: 'Mentors', path: '/about#mentors' },
      ],
    },
    {
      label: 'Our Team',
      path: '/team',
      subItems: [
        {
          label: 'Education & Skill development',
          path: '/team/education-and-skill-development',
        },
        {
          label: 'Healthcare',
          path: '/team/healthcare',
        },
        {
          label: 'Finance & Legal',
          path: '/team/finance-and-legal',
        },
        {
          label: 'Environment & Modern Agriculture',
          path: '/team/environment-and-modern-agriculture',
        },
        {
          label: 'Social Welfare',
          path: '/team/social-welfare',
        },
        {
          label: 'Culture & Tourism',
          path: '/team/culture-and-tourism',
        },
        {
          label: 'Sports & Yoga',
          path: '/team/sports-and-yoga',
        },
        {
          label: 'IT & Social Media',
          path: '/team/it-and-social-media',
        },
      ],
    },
    {
      label: 'Media & Awards',
      path: '/gallery',
      subItems: [
        { label: 'Photo Gallery', path: '/gallery' },
        { label: 'Video Gallery', path: '/gallery/videos' },
        { label: 'Upcoming Projects', path: '/projects' },
      ],
    },
    {
      label: 'Join Us',
      path: '/join',
      subItems: [
        { label: 'Join Us', path: '/join' },
        { label: 'Contact Us', path: '/contact' },
      ],
    },
    {
      label: 'Blog',
      path: '/blog',
    },
  ];

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }

    return location.pathname === path;
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <header className="header-wrapper">
      {/* ============================================================
          TOP CONTACT BAR
      ============================================================ */}
      <div className="header-topbar">
        <div className="container header-topbar-inner">
          <div className="header-topbar-spacer" />

          <div className="header-contact-info">
            <a
              href="tel:+918981266033"
              className="header-contact-item"
            >
              <Phone size={14} />
              <span>+91-8981266033</span>
            </a>

            <a
              href="mailto:info@pipladfoundation.in"
              className="header-contact-item"
            >
              <Mail size={14} />
              <span>info@pipladfoundation.in</span>
            </a>
          </div>
        </div>
      </div>

      {/* ============================================================
          MAIN NAVIGATION
      ============================================================ */}
      <div className="header-main">
        <div className="container header-main-inner">
          {/* BRAND */}
          <Link
            to="/"
            className="site-brand"
            aria-label="Piplad Welfare Foundation Home"
            onClick={closeMobileMenu}
          >
            <img
              src="/piplad-logo.jpg"
              alt="Piplad Welfare Foundation"
              className="site-brand-logo"
            />
          </Link>

          {/* DESKTOP NAVIGATION */}
          <nav className="desktop-nav" aria-label="Main navigation">
            {navItems.map((item) => (
              <div
                key={item.path}
                className="nav-item-group"
              >
                {item.subItems ? (
                  <>
                    <button
                      type="button"
                      className={`nav-link nav-dropdown-trigger ${
                        isActive(item.path)
                          ? 'active-nav-link'
                          : ''
                      }`}
                    >
                      <span>{item.label}</span>
                      <ChevronDown size={15} />
                    </button>

                    <div className="dropdown-menu">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.path}
                          to={subItem.path}
                          className="dropdown-item"
                        >
                          {subItem.label}
                        </Link>
                      ))}
                    </div>
                  </>
                ) : (
                  <Link
                    to={item.path}
                    className={`nav-link ${
                      isActive(item.path)
                        ? 'active-nav-link'
                        : ''
                    }`}
                  >
                    {item.label}
                  </Link>
                )}
              </div>
            ))}

            <button
              type="button"
              className="header-donate-button"
              onClick={onOpenDonate}
            >
              Donate
            </button>
          </nav>

          {/* MOBILE MENU BUTTON */}
          <button
            type="button"
            className="mobile-menu-btn"
            aria-label={
              mobileMenuOpen
                ? 'Close navigation menu'
                : 'Open navigation menu'
            }
            aria-expanded={mobileMenuOpen}
            onClick={() =>
              setMobileMenuOpen((current) => !current)
            }
          >
            {mobileMenuOpen ? (
              <X size={27} />
            ) : (
              <Menu size={27} />
            )}
          </button>
        </div>
      </div>

      {/* ============================================================
          MOBILE NAVIGATION
      ============================================================ */}
      {mobileMenuOpen && (
        <div className="mobile-menu">
          <div className="container mobile-menu-inner">
            {navItems.map((item) => (
              <div
                key={item.label}
                className="mobile-nav-group"
              >
                {item.subItems ? (
                  <>
                    <div
                      className={`mobile-nav-heading ${
                        isActive(item.path)
                          ? 'mobile-nav-heading-active'
                          : ''
                      }`}
                    >
                      {item.label}
                    </div>

                    <div className="mobile-submenu">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.path}
                          to={subItem.path}
                          className="mobile-submenu-link"
                          onClick={closeMobileMenu}
                        >
                          {subItem.label}
                        </Link>
                      ))}
                    </div>
                  </>
                ) : (
                  <Link
                    to={item.path}
                    className={`mobile-nav-link ${
                      isActive(item.path)
                        ? 'mobile-nav-link-active'
                        : ''
                    }`}
                    onClick={closeMobileMenu}
                  >
                    {item.label}
                  </Link>
                )}
              </div>
            ))}

            <button
              type="button"
              className="mobile-donate-button"
              onClick={() => {
                closeMobileMenu();
                onOpenDonate();
              }}
            >
              Donate Now
            </button>
          </div>
        </div>
      )}
    </header>
  );
}