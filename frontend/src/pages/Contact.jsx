import React, { useState } from 'react';
import { submitContact } from '../api';
import { MapPin, Phone, Mail, Send, CheckCircle2, Loader2 } from 'lucide-react';
import SocialLinks from '../components/SocialLinks';

export default function Contact() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await submitContact({ name, email, phone, subject, message });
      setLoading(false);
      setSubmitted(true);
      setName('');
      setEmail('');
      setPhone('');
      setSubject('');
      setMessage('');
    } catch (err) {
      setLoading(false);
      setError('Failed to send your message. Please try again or call us directly.');
    }
  };

  return (
    <div>
      {/* Banner */}
      <section style={{ background: '#0f172a', color: '#ffffff', padding: '4rem 0 3rem 0', textAlign: 'center' }}>
        <div className="container">
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>We Are Here To Help</span>
          <h1 className="heading-xl" style={{ color: '#ffffff', marginBottom: '0.75rem' }}>Contact Piplad Foundation</h1>
          <p className="subheading" style={{ color: '#94a3b8', margin: '0 auto' }}>
            Have questions about our initiatives, corporate partnership, or 80G tax receipts? Reach out to our team.
          </p>
        </div>
      </section>

      <section className="section-padding" style={{ background: '#ffffff' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '3.5rem' }}>
          
          {/* Contact Details Column */}
          <div>
            <h2 className="heading-lg" style={{ marginBottom: '1.25rem' }}>Get in Touch</h2>
            <p style={{ color: '#475569', lineHeight: 1.6, marginBottom: '2rem' }}>
              Whether you want to volunteer, partner for CSR initiatives, or inquire about healthcare support for a child, we welcome your communication.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2.5rem' }}>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                <div style={{ background: '#d1fae5', color: '#059669', padding: '0.75rem', borderRadius: '10px' }}>
                  <MapPin size={22} />
                </div>
                <div>
                  <h4 style={{ fontWeight: 700, color: '#0f172a' }}>Headquarters Address</h4>
                  <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Vill-Manikpur, Shahkhund-813108, Bhagalpur, Bihar</p>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                <div style={{ background: '#d1fae5', color: '#059669', padding: '0.75rem', borderRadius: '10px' }}>
                  <Phone size={22} />
                </div>
                <div>
                  <h4 style={{ fontWeight: 700, color: '#0f172a' }}>Helpline & WhatsApp</h4>
                  <p style={{ color: '#64748b', fontSize: '0.95rem' }}>+91-9876543210</p>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                <div style={{ background: '#d1fae5', color: '#059669', padding: '0.75rem', borderRadius: '10px' }}>
                  <Mail size={22} />
                </div>
                <div>
                  <h4 style={{ fontWeight: 700, color: '#0f172a' }}>Email Address</h4>
                  <p style={{ color: '#64748b', fontSize: '0.95rem' }}>info@pipladfoundation.in</p>
                </div>
              </div>

              <div>
                <h4 style={{ fontWeight: 700, color: '#0f172a', marginBottom: '0.9rem' }}>Follow Our Work</h4>
                <SocialLinks onLight />
              </div>
            </div>
          </div>

          {/* Form Column */}
          <div className="card" style={{ padding: '2.5rem' }}>
            <h3 className="heading-md" style={{ marginBottom: '1.25rem' }}>Send Us a Message</h3>

            {submitted ? (
              <div style={{ textAlign: 'center', padding: '2rem 0' }}>
                <CheckCircle2 size={48} color="#059669" style={{ margin: '0 auto 1rem auto' }} />
                <h4 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.5rem' }}>Message Received!</h4>
                <p style={{ fontSize: '0.9rem', color: '#475569', marginBottom: '1.5rem' }}>
                  Thank you for reaching out. Our representative will contact you shortly.
                </p>
                <button className="btn btn-outline" onClick={() => setSubmitted(false)}>
                  Send Another Message
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                {error && (
                  <div style={{ background: '#fef2f2', color: '#dc2626', padding: '0.75rem', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '1rem' }}>
                    {error}
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label">Your Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="Full Name"
                    className="form-input"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label className="form-label">Email *</label>
                    <input
                      type="email"
                      required
                      placeholder="email@example.com"
                      className="form-input"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Phone</label>
                    <input
                      type="tel"
                      placeholder="Mobile No."
                      className="form-input"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Subject</label>
                  <input
                    type="text"
                    placeholder="Inquiry Subject"
                    className="form-input"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Your Message *</label>
                  <textarea
                    rows={4}
                    required
                    placeholder="Write your message here..."
                    className="form-textarea"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                  />
                </div>

                <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: '100%', padding: '0.85rem' }}>
                  {loading ? <Loader2 className="animate-spin" size={18} /> : <><Send size={18} /> Submit Message</>}
                </button>
              </form>
            )}
          </div>

        </div>
      </section>
    </div>
  );
}
