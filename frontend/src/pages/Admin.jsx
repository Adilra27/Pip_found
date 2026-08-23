import React, { useEffect, useState } from 'react';
import { fetchAdminStats, fetchDonationsList, fetchContactInquiries } from '../api';
import { DollarSign, Users, Heart, MessageSquare, ShieldCheck, RefreshCw } from 'lucide-react';

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [donations, setDonations] = useState([]);
  const [inquiries, setInquiries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('donations');

  const loadAllAdminData = async () => {
    setLoading(true);
    try {
      const [sData, dData, iData] = await Promise.all([
        fetchAdminStats(),
        fetchDonationsList(),
        fetchContactInquiries()
      ]);
      setStats(sData);
      setDonations(dData);
      setInquiries(iData);
    } catch (err) {
      console.error('Admin data load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllAdminData();
  }, []);

  return (
    <div>
      {/* Banner */}
      <section style={{ background: '#0f172a', color: '#ffffff', padding: '3.5rem 0 2.5rem 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <span className="badge badge-green" style={{ marginBottom: '0.5rem' }}>
              <ShieldCheck size={16} /> PWF Administrative Dashboard
            </span>
            <h1 className="heading-lg" style={{ color: '#ffffff' }}>Management Overview</h1>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <a href="http://localhost:8000/admin" target="_blank" rel="noopener noreferrer" className="btn" style={{ background: '#059669', color: '#ffffff', textDecoration: 'none' }}>
              <ShieldCheck size={16} /> Open Full Database Admin
            </a>
            <button className="btn btn-outline" onClick={loadAllAdminData} style={{ color: '#ffffff', borderColor: '#475569' }}>
              <RefreshCw size={16} /> Refresh Data
            </button>
          </div>
        </div>
      </section>

      {/* Main Admin Section */}
      <section className="section-padding" style={{ background: '#f8fafc' }}>
        <div className="container">
          
          {/* Stats Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #059669' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, marginBottom: '0.3rem' }}>Total Raised</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>
                ₹{(stats?.total_donations || 0).toLocaleString('en-IN')}
              </div>
            </div>

            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #d97706' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, marginBottom: '0.3rem' }}>Total Donors</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>
                {stats?.total_donors || 0}
              </div>
            </div>

            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #0284c7' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, marginBottom: '0.3rem' }}>Active Causes</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>
                {stats?.active_causes || 0}
              </div>
            </div>

            <div className="card" style={{ padding: '1.5rem', borderLeft: '4px solid #db2777' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, marginBottom: '0.3rem' }}>Contact Inquiries</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>
                {stats?.inquiries_count || 0}
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: '1rem', borderBottom: '2px solid #e2e8f0', marginBottom: '2rem' }}>
            <button
              onClick={() => setTab('donations')}
              style={{
                padding: '0.75rem 1.25rem',
                border: 'none',
                background: 'none',
                fontWeight: 700,
                fontSize: '1rem',
                cursor: 'pointer',
                color: tab === 'donations' ? '#059669' : '#64748b',
                borderBottom: tab === 'donations' ? '3px solid #059669' : '3px solid transparent'
              }}
            >
              Donations Records ({donations.length})
            </button>
            <button
              onClick={() => setTab('inquiries')}
              style={{
                padding: '0.75rem 1.25rem',
                border: 'none',
                background: 'none',
                fontWeight: 700,
                fontSize: '1rem',
                cursor: 'pointer',
                color: tab === 'inquiries' ? '#059669' : '#64748b',
                borderBottom: tab === 'inquiries' ? '3px solid #059669' : '3px solid transparent'
              }}
            >
              Contact Submissions ({inquiries.length})
            </button>
          </div>

          {/* Tab Content */}
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: '#64748b' }}>Loading logs...</div>
          ) : tab === 'donations' ? (
            <div className="card" style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#334155' }}>
                    <th style={{ padding: '1rem' }}>ID</th>
                    <th style={{ padding: '1rem' }}>Donor Name</th>
                    <th style={{ padding: '1rem' }}>Email / Phone</th>
                    <th style={{ padding: '1rem' }}>Amount</th>
                    <th style={{ padding: '1rem' }}>Status</th>
                    <th style={{ padding: '1rem' }}>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {donations.length === 0 ? (
                    <tr><td colSpan={6} style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>No donation records found.</td></tr>
                  ) : (
                    donations.map((d) => (
                      <tr key={d.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '1rem', fontWeight: 600 }}>#{d.id}</td>
                        <td style={{ padding: '1rem', fontWeight: 700, color: '#0f172a' }}>{d.donor_name}</td>
                        <td style={{ padding: '1rem', color: '#64748b' }}>{d.donor_email} {d.donor_phone ? `(${d.donor_phone})` : ''}</td>
                        <td style={{ padding: '1rem', fontWeight: 700, color: '#059669' }}>₹{d.amount.toLocaleString('en-IN')}</td>
                        <td style={{ padding: '1rem' }}>
                          <span className="badge badge-green" style={{ textTransform: 'capitalize' }}>
                            {d.status}
                          </span>
                        </td>
                        <td style={{ padding: '1rem', color: '#64748b' }}>{new Date(d.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="card" style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#334155' }}>
                    <th style={{ padding: '1rem' }}>ID</th>
                    <th style={{ padding: '1rem' }}>Name</th>
                    <th style={{ padding: '1rem' }}>Email / Phone</th>
                    <th style={{ padding: '1rem' }}>Subject</th>
                    <th style={{ padding: '1rem' }}>Message</th>
                    <th style={{ padding: '1rem' }}>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {inquiries.length === 0 ? (
                    <tr><td colSpan={6} style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>No contact submissions found.</td></tr>
                  ) : (
                    inquiries.map((i) => (
                      <tr key={i.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '1rem', fontWeight: 600 }}>#{i.id}</td>
                        <td style={{ padding: '1rem', fontWeight: 700, color: '#0f172a' }}>{i.name}</td>
                        <td style={{ padding: '1rem', color: '#64748b' }}>{i.email} {i.phone ? `(${i.phone})` : ''}</td>
                        <td style={{ padding: '1rem', fontWeight: 600 }}>{i.subject || 'General'}</td>
                        <td style={{ padding: '1rem', color: '#475569', maxWidth: '300px' }}>{i.message}</td>
                        <td style={{ padding: '1rem', color: '#64748b' }}>{new Date(i.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

        </div>
      </section>
    </div>
  );
}
